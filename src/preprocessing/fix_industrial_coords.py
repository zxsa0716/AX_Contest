"""Fix Gold sites coordinates for chemical/heavy industry firms.

GIR allocation 데이터의 첫 record가 본사 주소인 경우가 다수 — 실제 산업시설 좌표로 교체.
서비스·금융 firms (네이버·KT·삼성생명·IBK·롯데쇼핑·이마트·대한항공·삼성물산·두산·한화·현대모비스·현대차·CJ제일제당)은 HQ 적절 (Scope 1 미미).
화학·중공업 firms (롯데케미칼·한화솔루션) HQ 잘못 → 산업시설 좌표 명시.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SITES = ROOT / "data" / "interim" / "gold_sites.csv"

# Industrial site corrections (verified public addresses)
CORRECTIONS = {
    # 롯데케미칼 여수 본부 + 대산 공장
    "11170": {"lat": 34.8553, "lon": 127.7115, "address": "전라남도 여수시 여수산단로 918 (롯데케미칼 여수공장)", "industry": "petrochem"},
    # 한화솔루션 여수 (한화케미칼 출신)
    "9830":  {"lat": 34.8800, "lon": 127.6900, "address": "전라남도 여수시 여수국가산업단지 (한화솔루션 여수)", "industry": "petrochem"},
    # CJ제일제당 인천 공장 (식품 가공)
    "97950": {"lat": 37.4500, "lon": 126.6300, "address": "인천광역시 서구 봉수대로 (CJ제일제당 인천공장)", "industry": "other"},
    # 두산 — 두산에너빌리티 창원 공장 (제조 부문)
    "150":   {"lat": 35.2206, "lon": 128.6815, "address": "경상남도 창원시 성산구 창원대로 555 (두산에너빌리티)", "industry": "other"},
    # 한화 — 보은 화약 공장 또는 여수
    "880":   {"lat": 36.4900, "lon": 127.7300, "address": "충청북도 보은군 (한화 보은공장)", "industry": "other"},
    # 대한항공 인천공항 정비 격납고
    "3490":  {"lat": 37.4602, "lon": 126.4407, "address": "인천광역시 중구 공항로 271 (인천공항 KE 정비)", "industry": "other"},
    # 이마트 - 자체 물류센터 (서울보다는 광역, 본사로 유지하지만 명시)
    # → 그대로
    # 삼성물산 — 건설부문 사업장 다수, 본사로 유지
    # → 그대로
}

# Verified industrial sites (already correct, no change needed)
ALREADY_OK = {
    "5490":  "POSCO 포항 (35.998, 129.383)",
    "660":   "SK하이닉스 이천 (37.255, 127.485)",
    "5930":  "삼성전자 수원 (37.255, 127.051)",
    "4020":  "현대제철 인천 (37.490, 126.636)",
    "15760": "한전 본사 나주 (35.026, 126.785)",
    "373220":"LG엔솔 - 본사 (37.527, 126.928), 실제 오창 공장 별도",
    "34220": "LGD 본사 (37.528, 126.929), 실제 파주/구미 공장 별도",
}


def main():
    df = pd.read_csv(SITES)
    df["stock_code"] = df["stock_code"].astype(str)
    df["original_lat"] = df["lat"]
    df["original_lon"] = df["lon"]
    df["coord_source"] = "vworld_HQ"  # default

    fixed = 0
    for code, corr in CORRECTIONS.items():
        mask = df["stock_code"] == code
        if mask.any():
            df.loc[mask, "lat"] = corr["lat"]
            df.loc[mask, "lon"] = corr["lon"]
            df.loc[mask, "address"] = corr["address"]
            df.loc[mask, "coord_source"] = "manual_industrial_site"
            df.loc[mask, "industry"] = corr["industry"]
            print(f"  fixed {code}: {corr['address'][:40]}")
            fixed += 1

    # Save
    df.to_csv(SITES, index=False, encoding="utf-8-sig")
    print(f"\n[saved] {SITES} — {fixed} corrections applied")

    # Print final state
    print("\n=== 최종 site 분류 ===")
    print(df[["stock_code", "corp_name", "lat", "lon", "industry", "coord_source"]].to_string(index=False))


if __name__ == "__main__":
    main()
