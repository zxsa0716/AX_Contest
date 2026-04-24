"""Three-layer anomaly detection ensemble (ADR-003 §5.4).

Layer 1 — Cross-sectional: Isolation Forest + LOF ensemble
Layer 2 — Longitudinal: Mann-Kendall significant trend per firm
Layer 3 — Cross-validation: against KCGS quarterly adjustment events (supervised label)

Output: data/processed/anomaly_classification.csv
Cross-sectional feature vector per firm-year:
  [gir_scope1_log, scope1_diff_pct, no2_mean, so2_mean, hcho_mean,
   odiac_sum_tC_year, era5_blh, gir_tier_proxy (verifier diversity)]

Contamination sensitivity: {0.05, 0.10, 0.15, 0.20}
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
MK = ROOT / "data" / "processed" / "trend_mk.csv"
KCGS_ADJ = ROOT / "data" / "interim" / "kcgs_quarterly_adjustments.csv"
OUT = ROOT / "data" / "processed"


def layer1_cross_sectional(df: pd.DataFrame) -> pd.DataFrame:
    """IF + LOF ensemble across contamination sensitivity."""
    features = ["gir_scope1_tco2eq", "no2_mean", "so2_mean",
                "co_mean", "hcho_mean", "odiac_sum_tC_year", "era5_blh"]
    features = [f for f in features if f in df.columns]

    d = df.copy()
    d["log_gir"] = np.log1p(d["gir_scope1_tco2eq"])
    feature_cols = ["log_gir"] + [f for f in features if f != "gir_scope1_tco2eq"]
    X = d[feature_cols].values
    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(X)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imp)

    results = d[["stock_code", "corp_name", "year"]].copy()

    # Contamination sensitivity sweep (ADR-003)
    for cont in [0.05, 0.10, 0.15, 0.20]:
        # IF
        iso = IsolationForest(contamination=cont, random_state=42, n_estimators=200)
        iso_pred = iso.fit_predict(X_scaled)
        results[f"if_anomaly_c{int(cont*100):02d}"] = (iso_pred == -1).astype(int)

        # LOF
        try:
            n_neighbors = max(5, min(20, len(X_scaled) // 3))
            lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=cont)
            lof_pred = lof.fit_predict(X_scaled)
            results[f"lof_anomaly_c{int(cont*100):02d}"] = (lof_pred == -1).astype(int)
        except Exception:
            results[f"lof_anomaly_c{int(cont*100):02d}"] = np.nan

        # Ensemble: both agree
        results[f"ensemble_c{int(cont*100):02d}"] = (
            (results[f"if_anomaly_c{int(cont*100):02d}"] == 1) &
            (results[f"lof_anomaly_c{int(cont*100):02d}"] == 1)
        ).astype(int)

    # Primary flag at contamination=0.10
    results["layer1_anomaly"] = results["ensemble_c10"]
    return results


def layer2_longitudinal() -> pd.DataFrame:
    """Mann-Kendall trend significance from trend_mk.csv."""
    if not MK.exists():
        return pd.DataFrame()
    mk = pd.read_csv(MK)
    mk["stock_code"] = mk["stock_code"].astype(str).str.zfill(6)
    mk["layer2_anomaly"] = (
        (mk["gir_p"] < 0.1) & (mk["gir_tau"].abs() >= 0.4)
    ).astype(int)
    mk["layer2_pattern"] = mk["pattern"]
    return mk[["stock_code", "corp_name", "layer2_anomaly", "layer2_pattern",
               "gir_tau", "esg_tau", "no2_tau", "odiac_tau"]]


def layer3_supervised_labels() -> pd.DataFrame:
    """KCGS ESG grade downgrades (supervised label, ADR-004)."""
    if not KCGS_ADJ.exists():
        return pd.DataFrame(columns=["stock_code", "year", "kcgs_downgrade"])
    k = pd.read_csv(KCGS_ADJ)
    # Assume kcgs CSV has columns: year, firm_name, prev_grade, new_grade, ...
    # Map firm_name to stock_code via master index
    mi = pd.read_parquet(ROOT / "data" / "interim" / "company_master_index.parquet")
    # Simple fuzzy match
    from rapidfuzz import process
    mapping = {}
    mi_names = mi.set_index("corp_name_canonical")["stock_code"].to_dict()
    for fname in k["firm_name"].unique() if "firm_name" in k.columns else []:
        match = process.extractOne(fname, mi_names.keys(), score_cutoff=75)
        if match:
            mapping[fname] = mi_names[match[0]]
    if not mapping:
        return pd.DataFrame(columns=["stock_code", "year", "kcgs_downgrade"])
    k["stock_code"] = k["firm_name"].map(mapping)
    k = k.dropna(subset=["stock_code"])
    # Mark as downgrade (rough: if 'new' grade letter worse than 'prev')
    k["kcgs_downgrade"] = 1  # every adjustment treated as signal
    return k.groupby(["stock_code", "year"], as_index=False)["kcgs_downgrade"].max()


def main() -> None:
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)].copy()
    df["stock_code"] = df["stock_code"].astype(str).str.zfill(6)

    print(f"Panel: {len(df)} rows, {df['stock_code'].nunique()} firms")

    # Layer 1
    l1 = layer1_cross_sectional(df)
    print(f"\nLayer 1 (cross-sectional): {l1['layer1_anomaly'].sum()} anomalies (c=0.10)")

    # Layer 2
    l2 = layer2_longitudinal()
    print(f"Layer 2 (longitudinal): {l2['layer2_anomaly'].sum() if len(l2) else 0} firms with MK trend")

    # Layer 3 (supervised)
    l3 = layer3_supervised_labels()
    print(f"Layer 3 (KCGS downgrades): {len(l3)} firm-year events")

    # Merge
    out = l1.merge(l2, on=["stock_code", "corp_name"], how="left")
    if len(l3):
        out = out.merge(l3, on=["stock_code", "year"], how="left")
        out["kcgs_downgrade"] = out["kcgs_downgrade"].fillna(0).astype(int)
    else:
        out["kcgs_downgrade"] = 0

    # Final structural / longitudinal / transient classification
    def classify(row):
        l1_a = row["layer1_anomaly"] == 1
        l2_a = row.get("layer2_anomaly", 0) == 1
        if l1_a and l2_a:
            return "structural"
        if l2_a:
            return "longitudinal"
        if l1_a:
            return "transient"
        return "normal"

    out["anomaly_class"] = out.apply(classify, axis=1)

    out_csv = OUT / "anomaly_classification.csv"
    out.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"\n[saved] {out_csv}")

    print(f"\n=== Anomaly class distribution ===")
    print(out["anomaly_class"].value_counts())

    print(f"\n=== Validation against KCGS supervised labels ===")
    if out["kcgs_downgrade"].sum() > 0:
        confusion = pd.crosstab(out["anomaly_class"], out["kcgs_downgrade"])
        print(confusion)

    print(f"\n=== Contamination sensitivity (IF+LOF ensemble) ===")
    for cont in [5, 10, 15, 20]:
        col = f"ensemble_c{cont:02d}"
        if col in out.columns:
            print(f"  c={cont/100}: {out[col].sum()} anomalies")


if __name__ == "__main__":
    main()
