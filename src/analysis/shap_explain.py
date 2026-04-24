"""SHAP-based explanation of anomaly detection (ADR-003 §6.6).

Uses TreeExplainer with feature_perturbation='interventional' (per roundtable requirement)
on Isolation Forest to decompose per-firm anomaly contributions.

Outputs:
- data/processed/shap_values.csv — per-firm feature contributions
- figs/fig_shap_summary.png — beeswarm plot
- figs/fig_shap_waterfall_top5.png — waterfall plots for top 5 anomalous firms
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import shap

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "visualization"))
from style import setup_style

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "data" / "processed" / "integrated_panel.parquet"
OUT = ROOT / "data" / "processed"
FIGS = ROOT / "figs"


def build_features(df: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame, list[str]]:
    feats = ["gir_scope1_tco2eq", "no2_mean", "so2_mean", "co_mean",
             "hcho_mean", "odiac_sum_tC_year", "era5_blh", "energy_tj"]
    feats = [f for f in feats if f in df.columns]
    labels = [
        "log_GIR", "NO₂", "SO₂", "CO", "HCHO",
        "ODIAC CO₂", "ERA5 BLH", "에너지 (TJ)"
    ][:len(feats)]

    d = df.copy()
    if "gir_scope1_tco2eq" in feats:
        d["gir_scope1_tco2eq"] = np.log1p(d["gir_scope1_tco2eq"])
    X = d[feats].values
    X = SimpleImputer(strategy="median").fit_transform(X)
    X_scaled = StandardScaler().fit_transform(X)
    return X_scaled, d[["stock_code", "corp_name", "year", "industry"]], labels


def main() -> None:
    setup_style()
    df = pd.read_parquet(PANEL)
    df = df[df["year"].between(2019, 2023)].copy()

    X, meta, labels = build_features(df)
    print(f"SHAP input: {X.shape}, features: {labels}")

    iso = IsolationForest(contamination=0.10, random_state=42, n_estimators=200)
    iso.fit(X)

    # SHAP on Isolation Forest tree ensemble
    # For sklearn IsolationForest, use TreeExplainer with algorithm='auto'
    try:
        explainer = shap.TreeExplainer(iso, feature_perturbation="interventional",
                                        data=shap.sample(X, min(100, len(X))))
        shap_values = explainer.shap_values(X)
    except Exception as e:
        print(f"[fallback] TreeExplainer failed ({e}), using KernelExplainer")
        explainer = shap.KernelExplainer(iso.decision_function,
                                          shap.sample(X, min(50, len(X))))
        shap_values = explainer.shap_values(X, nsamples=100)

    # Save SHAP values
    shap_df = pd.DataFrame(shap_values, columns=[f"shap_{l}" for l in labels])
    out_df = pd.concat([meta.reset_index(drop=True), shap_df], axis=1)
    out_df["iso_score"] = iso.decision_function(X)
    out_df["iso_anomaly"] = (iso.predict(X) == -1).astype(int)
    out_df.to_csv(OUT / "shap_values.csv", index=False, encoding="utf-8-sig")
    print(f"[saved] {OUT / 'shap_values.csv'}")

    # Summary beeswarm
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X, feature_names=labels, show=False,
                       max_display=len(labels))
    plt.tight_layout()
    fig_path = FIGS / "fig_shap_summary.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {fig_path}")

    # Waterfall for top 5 anomalies
    top5_idx = np.argsort(iso.decision_function(X))[:5]  # most anomalous
    fig, axes = plt.subplots(5, 1, figsize=(10, 25))
    for i, idx in enumerate(top5_idx):
        ax = axes[i] if len(top5_idx) > 1 else axes
        # Simple bar plot of SHAP contributions
        vals = shap_values[idx]
        order = np.argsort(np.abs(vals))[::-1]
        ax.barh([labels[j] for j in order], [vals[j] for j in order],
                color=["#D55E00" if v > 0 else "#0072B2" for v in vals[order]])
        ax.axvline(0, color="black", linewidth=0.5)
        corp = meta.iloc[idx]
        ax.set_title(f"{corp['corp_name']} ({corp['stock_code']}) × {corp['year']} "
                     f"| iso_score={iso.decision_function(X)[idx]:.3f}")
        ax.set_xlabel("SHAP value (contribution to anomaly score)")
    plt.tight_layout()
    fig_path = FIGS / "fig_shap_waterfall_top5.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[saved] {fig_path}")


if __name__ == "__main__":
    main()
