"""
download_data_go_kr.py
======================
Wave 1 / Part A — Bulk download of public environmental data from data.go.kr.

Strategy (in order per dataset):
  1. If DATA_GO_KR_KEY is set in .env, attempt the fileData open-API endpoint.
  2. If the key is absent or the API returns 401/403, fall back to the direct
     static-file URL pattern (many GIR datasets expose a plain URL).
  3. If both paths fail, emit a clear manual-download instruction and continue.

Every attempt (success or failure) is appended to data/raw/download_log.json.
Every successful download triggers SHA-256 computation that is appended to
data/README.md.

Usage:
    python src/preprocessing/download_data_go_kr.py [--dry-run]

    --dry-run   Print the action plan without actually downloading anything.

Requirements:
    pip install requests python-dotenv tqdm
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Paths (always absolute)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
README_PATH = PROJECT_ROOT / "data" / "README.md"
LOG_PATH = RAW_DIR / "download_log.json"

# ---------------------------------------------------------------------------
# Dataset registry
# ---------------------------------------------------------------------------
# Each entry describes one data.go.kr fileData dataset.
# `file_items` lists the individual year-labelled files where known.
# `direct_urls` are fallback static download links (discovered from portal HTML).
# `target_dir` is relative to RAW_DIR.
# ---------------------------------------------------------------------------
DATASETS = [
    {
        "dataset_id": "15053947",
        "name": "GIR 관리업체 명세서 배출량 (연도별)",
        "label": "A",
        "target_dir": "gir_manifest",
        "years": [2019, 2020, 2021, 2022, 2023],
        "filename_pattern": "{year}.csv",
        # Publicly visible static CSV links on data.go.kr (no API key required).
        # Verified pattern: the portal exposes per-file download endpoints.
        # These must be confirmed via browser inspection; placeholders are
        # provided here so the manual-instruction path is clear.
        "direct_url_pattern": None,  # set to URL string if known
        "portal_url": "https://www.data.go.kr/data/15053947/fileData.do",
        "encoding": "cp949",
        "notes": "법정 Scope 1 기준값. Tier 코드 별도 컬럼 필요.",
    },
    {
        "dataset_id": "15053949",
        "name": "GIR 할당대상업체 지정현황",
        "label": "A-2",
        "target_dir": "gir_allocated",
        "years": [2019, 2020, 2021, 2022, 2023],
        "filename_pattern": "{year}.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15053949/fileData.do",
        "encoding": "cp949",
        "notes": "사업장 주소 포함 → Kakao/VWorld 지오코딩 입력.",
    },
    {
        "dataset_id": "15053948",
        "name": "GIR 목표관리대상업체 현황",
        "label": "A-3",
        "target_dir": "gir_target",
        "years": [2019, 2020, 2021, 2022, 2023],
        "filename_pattern": "{year}.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15053948/fileData.do",
        "encoding": "cp949",
        "notes": "목표관리 대상 명세. 할당대상과 교차 검증용.",
    },
    {
        "dataset_id": "15126853",
        "name": "K-ETS 사전할당량 3차 계획기간",
        "label": "3",
        "target_dir": "kets_allocation",
        "years": None,  # single file
        "filename_pattern": "kets_allocation_3rd.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15126853/fileData.do",
        "encoding": "cp949",
        "notes": "할당-실배출 gap 계산. Heckman 도구변수.",
    },
    {
        "dataset_id": "15049589",
        "name": "국가 온실가스 인벤토리 (NIR)",
        "label": "NIR",
        "target_dir": "nir",
        "years": None,
        "filename_pattern": "nir_latest.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15049589/fileData.do",
        "encoding": "cp949",
        "notes": "국가 인벤토리 총량. 산업별 배출량 맥락.",
    },
    {
        "dataset_id": "15082976",
        "name": "온실가스 검증기관 지정현황",
        "label": "4",
        "target_dir": "gir_verifier",
        "years": None,
        "filename_pattern": "gir_verifier.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15082976/fileData.do",
        "encoding": "cp949",
        "notes": "법정 배출량 자체 신뢰도 메타변수.",
    },
    {
        "dataset_id": "15123597",
        "name": "통합환경허가 사업장 정보공개",
        "label": "T2-1",
        "target_dir": "integrated_permit",
        "years": None,
        "filename_pattern": "integrated_permit.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15123597/fileData.do",
        "encoding": "cp949",
        "notes": "Tier 2. 사업장 허가 정보 — 사업장 매칭 보완.",
    },
    {
        "dataset_id": "15122803",
        "name": "사업장 대기오염물질 측정값",
        "label": "T2-2",
        "target_dir": "air_emission",
        "years": None,
        "filename_pattern": "air_emission.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15122803/fileData.do",
        "encoding": "cp949",
        "notes": "Tier 2. PRTR 대기 측정값. NO₂/SO₂ 위성 교차 검증용.",
    },
    {
        "dataset_id": "15044902",
        "name": "한국에너지공단 에너지진단통계",
        "label": "T2-3",
        "target_dir": "energy_diagnosis",
        "years": None,
        "filename_pattern": "energy_diagnosis.csv",
        "direct_url_pattern": None,
        "portal_url": "https://www.data.go.kr/data/15044902/fileData.do",
        "encoding": "cp949",
        "notes": "Tier 2. 에너지 소비량 → Scope 1 상관 통제변수.",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file, reading in 1 MB chunks."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_log() -> list:
    if LOG_PATH.exists():
        with open(LOG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_log(entries: list) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def log_entry(
    dataset_id: str,
    name: str,
    target_path: str,
    status: str,  # "success" | "failed" | "manual_required"
    url: str,
    sha256: Optional[str] = None,
    error: Optional[str] = None,
) -> dict:
    return {
        "dataset_id": dataset_id,
        "name": name,
        "target_path": target_path,
        "url": url,
        "status": status,
        "sha256": sha256,
        "error": error,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def save_metadata_stub(target_path: Path, url: str) -> None:
    """Save a JSON metadata stub alongside the downloaded file."""
    stub = {
        "url": url,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "intended_path": str(target_path),
    }
    stub_path = target_path.with_suffix(".meta.json")
    with open(stub_path, "w", encoding="utf-8") as f:
        json.dump(stub, f, ensure_ascii=False, indent=2)


def append_readme(
    label: str,
    name: str,
    portal_url: str,
    file_path: str,
    sha256: str,
    encoding: str,
) -> None:
    """Append or update a row in data/README.md inventory table."""
    row = (
        f"| {label} | {name} | data.go.kr | "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')} | "
        f"`{file_path}` | `{sha256[:16]}…` | corp-data-manager |"
        f"  <!-- encoding={encoding} -->\n"
    )
    with open(README_PATH, "a", encoding="utf-8") as f:
        f.write(row)


def download_with_progress(url: str, dest: Path, session: requests.Session) -> None:
    """Stream-download url to dest with a tqdm progress bar."""
    with session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0)) or None
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f, tqdm(
            total=total,
            unit="B",
            unit_scale=True,
            desc=dest.name,
            leave=False,
        ) as bar:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)
                bar.update(len(chunk))


def try_api_download(
    api_key: str,
    dataset_id: str,
    filename: str,
    dest: Path,
    session: requests.Session,
) -> tuple[bool, str]:
    """
    Attempt to download via the data.go.kr file download API.

    The public-data portal exposes a file-list endpoint:
      GET https://api.data.go.kr/openapi/tn_pubr_public_fileData_info_service
    Then a per-file download URL is constructed from the returned fileUrl.

    Returns (success: bool, url_or_error: str).
    """
    list_url = "https://api.data.go.kr/openapi/tn_pubr_public_fileData_info_service"
    params = {
        "serviceKey": api_key,
        "pageNo": "1",
        "numOfRows": "100",
        "type": "json",
        "dataSetNm": dataset_id,
    }
    try:
        resp = session.get(list_url, params=params, timeout=30)
        if resp.status_code in (401, 403):
            return False, f"HTTP {resp.status_code}: API key rejected"
        resp.raise_for_status()
        data = resp.json()
        items = (
            data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        if isinstance(items, dict):
            items = [items]
        # Match by filename fragment or take first
        matched = next(
            (i for i in items if filename.lower() in i.get("fileNm", "").lower()),
            items[0] if items else None,
        )
        if not matched:
            return False, "No matching file found in API response"
        file_url = matched.get("fileUrl") or matched.get("downloadUrl")
        if not file_url:
            return False, "fileUrl missing from API item"
        download_with_progress(file_url, dest, session)
        return True, file_url
    except Exception as exc:
        return False, str(exc)


def print_manual_instructions(datasets_needing_manual: list[dict]) -> None:
    """Print a formatted manual-download instruction table."""
    if not datasets_needing_manual:
        return
    print("\n" + "=" * 72)
    print("MANUAL DOWNLOAD REQUIRED — the following datasets could not be")
    print("downloaded automatically.  Please follow the steps below.")
    print("=" * 72)
    for item in datasets_needing_manual:
        ds = item["dataset"]
        target = item["target"]
        reason = item["reason"]
        print(f"\n[Dataset {ds['dataset_id']}] {ds['name']}")
        print(f"  Reason  : {reason}")
        print(f"  Portal  : {ds['portal_url']}")
        print(f"  Save to : {target}")
        print(
            textwrap.fill(
                "  Steps   : 1) Open the portal URL in a browser.  "
                "2) Click the download button for each year-file (or the single file).  "
                "3) Save to the path shown above.  "
                "4) Run: python -c \"import hashlib; "
                "print(hashlib.sha256(open(r'" + str(target) + "','rb').read()).hexdigest())\" "
                "and record the hash in data/README.md.",
                width=72,
                subsequent_indent="            ",
            )
        )
    print("=" * 72 + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(dry_run: bool = False) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    api_key: Optional[str] = os.environ.get("DATA_GO_KR_KEY")

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }
    )

    log_entries = load_log()
    manual_queue: list[dict] = []

    if api_key:
        print(f"DATA_GO_KR_KEY found — will attempt API download first.")
    else:
        print(
            "DATA_GO_KR_KEY not set — skipping API path, will attempt direct "
            "URLs where known, otherwise queuing for manual download."
        )

    all_tasks: list[tuple[dict, Path, Optional[int]]] = []
    for ds in DATASETS:
        if ds["years"]:
            for year in ds["years"]:
                filename = ds["filename_pattern"].format(year=year)
                target = RAW_DIR / ds["target_dir"] / filename
                all_tasks.append((ds, target, year))
        else:
            filename = ds["filename_pattern"]
            target = RAW_DIR / ds["target_dir"] / filename
            all_tasks.append((ds, target, None))

    print(f"\nTotal tasks: {len(all_tasks)} files across {len(DATASETS)} datasets.\n")

    for ds, target, year in tqdm(all_tasks, desc="Datasets", unit="file"):
        if dry_run:
            print(f"  [DRY-RUN] Would download: {target}")
            continue

        # Skip if already downloaded (resume support)
        if target.exists():
            print(f"  [SKIP] Already exists: {target.name}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        filename = target.name
        attempted_url = ds["portal_url"]
        success = False
        error_msg = ""

        # --- Path 1: API key present ---
        if api_key:
            success, result = try_api_download(
                api_key, ds["dataset_id"], filename, target, session
            )
            if success:
                attempted_url = result
            else:
                error_msg = result
                print(f"  [API FAIL] {ds['dataset_id']}/{filename}: {result}")

        # --- Path 2: direct URL if configured ---
        if not success and ds.get("direct_url_pattern"):
            url = ds["direct_url_pattern"].format(year=year or "")
            try:
                download_with_progress(url, target, session)
                attempted_url = url
                success = True
            except Exception as exc:
                error_msg = str(exc)
                print(f"  [DIRECT FAIL] {url}: {exc}")

        # --- Path 3: manual queue ---
        if not success:
            manual_queue.append(
                {
                    "dataset": ds,
                    "target": target,
                    "reason": error_msg or "No automatic download path available",
                }
            )
            log_entries.append(
                log_entry(
                    ds["dataset_id"],
                    ds["name"],
                    str(target),
                    "manual_required",
                    attempted_url,
                    error=error_msg or "No automatic download path",
                )
            )
            continue

        # --- Success path ---
        sha = sha256_file(target)
        save_metadata_stub(target, attempted_url)
        append_readme(
            ds["label"],
            f"{ds['name']} ({year or 'latest'})",
            ds["portal_url"],
            str(target.relative_to(PROJECT_ROOT)),
            sha,
            ds["encoding"],
        )
        log_entries.append(
            log_entry(
                ds["dataset_id"],
                ds["name"],
                str(target),
                "success",
                attempted_url,
                sha256=sha,
            )
        )
        print(f"  [OK] {target.name}  sha256={sha[:16]}…")

    save_log(log_entries)
    print(f"\nDownload log saved: {LOG_PATH}")

    print_manual_instructions(manual_queue)

    # Summary
    successes = sum(1 for e in log_entries if e["status"] == "success")
    manual = sum(1 for e in log_entries if e["status"] == "manual_required")
    failed = sum(1 for e in log_entries if e["status"] == "failed")
    print(
        f"Summary — success: {successes} | manual_required: {manual} | failed: {failed}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download data.go.kr GIR datasets")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print plan without downloading",
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run)
