"""
Task 7: Parse 통합환경허가 '공개내용' free-text column.

Input:  data/통합환경허가/*.csv  (cp949)
Output: data/interim/integrated_permit_sites.parquet

The '공개내용' column has structured text:
  ·상호(명칭) :포스코필바라리튬솔루션
  ·성명(대표자) :  대표이사
  ·주소(사업장) : 전라남도 광양시 ...

허가번호 is parsed from '제목' column: e.g. (제724-01호)
업종 is parsed from '제목' column: e.g. [통합허가 무기화학]
"""

import re
import glob
import logging
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from consolidate_gir import normalize_corp_name

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Regex patterns
RE_PERMIT_NO = re.compile(r"\(제\s*([\w\-]+호)\)")
RE_SECTOR = re.compile(r"\[(통합허가|변경허가|재발급|기타)\s*([^\]]+)\]")
RE_CORP_NAME = re.compile(r"상호\(명칭\)\s*[:：]\s*(.+?)(?:\s*·|\s*·|\n|$)")
RE_REP = re.compile(r"성명\(대표자\)\s*[:：]\s*(.+?)(?:\s*·|\s*·|\n|1\.|$)")
RE_ADDR = re.compile(r"주소\(사업장\)\s*[:：]\s*(.+?)(?:\s*1\.|\s*2\.|\s*$)")


def parse_row(row: pd.Series) -> dict:
    title = str(row.get("제목", ""))
    content = str(row.get("공개내용", ""))

    # 허가번호 from title
    m_permit = RE_PERMIT_NO.search(title)
    permit_no = m_permit.group(1).strip() if m_permit else None

    # 업종 from title
    m_sector = RE_SECTOR.search(title)
    sector = m_sector.group(2).strip() if m_sector else None

    # Company name from content
    m_corp = RE_CORP_NAME.search(content)
    corp_name = m_corp.group(1).strip() if m_corp else None

    # Representative from content
    m_rep = RE_REP.search(content)
    rep = m_rep.group(1).strip() if m_rep else None

    # Address from content
    m_addr = RE_ADDR.search(content)
    address = m_addr.group(1).strip() if m_addr else None

    return {
        "허가번호": permit_no,
        "기업명": corp_name,
        "기업명_normalized": normalize_corp_name(corp_name) if corp_name else None,
        "대표자": rep,
        "주소": address,
        "업종": sector,
        "작성자": row.get("작성자", None),
        "파일번호": row.get("파일번호", None),
        "순번": row.get("순번", None),
    }


def main(
    input_dir: str = "data/통합환경허가",
    output_path: str = "data/interim/integrated_permit_sites.parquet",
    failure_path: str = "data/interim/failures_integrated_permit.csv",
) -> pd.DataFrame:
    files = glob.glob(f"{input_dir}/*.csv")
    if not files:
        logger.error(f"No CSV in {input_dir}")
        return pd.DataFrame()

    path = files[0]
    for enc in ("cp949", "utf-8-sig", "utf-8"):
        try:
            df_raw = pd.read_csv(path, encoding=enc, dtype=str)
            logger.info(f"Loaded with encoding={enc}, shape={df_raw.shape}")
            break
        except Exception as e:
            logger.warning(f"{enc} failed: {e}")
    else:
        logger.error("Cannot decode 통합환경허가 CSV")
        return pd.DataFrame()

    results = []
    failures = []
    for _, row in tqdm(df_raw.iterrows(), total=len(df_raw), desc="Parsing 통합환경허가"):
        try:
            parsed = parse_row(row)
            results.append(parsed)
            if not parsed["기업명"]:
                failures.append({"순번": row.get("순번"), "reason": "corp_name_not_found", "title": row.get("제목")})
        except Exception as e:
            failures.append({"순번": row.get("순번"), "reason": str(e), "title": row.get("제목")})

    df_out = pd.DataFrame(results)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df_out.to_parquet(output_path, index=False)
    logger.info(f"Saved {len(df_out):,} rows -> {output_path}")

    if failures:
        df_fail = pd.DataFrame(failures)
        df_fail.to_csv(failure_path, index=False, encoding="utf-8-sig")
        logger.info(f"Logged {len(failures)} failures -> {failure_path}")

    logger.info(f"Rows with corp_name extracted: {df_out['기업명'].notna().sum():,}")
    logger.info(f"Rows with address extracted: {df_out['주소'].notna().sum():,}")
    return df_out


if __name__ == "__main__":
    main()
