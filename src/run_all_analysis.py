"""Run all analysis in order after ESG parser completes.

Usage: .venv/Scripts/python.exe src/run_all_analysis.py

Order:
1. build_integrated_panel.py — merge all sources → integrated_panel.parquet
2. compute_discrepancy_metrics.py — Mann-Kendall per firm → trend_mk.csv
3. anomaly_detection.py — 3-layer ensemble → anomaly_classification.csv
4. heckman_selection.py — 2-stage regression → heckman_results.csv
5. shap_explain.py — SHAP decomposition → shap_values.csv + figs
6. results_summary.py — markdown tables → report/tables/
7. fig_*.py — regenerate all figures
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")

STEPS = [
    ("Integrated panel build",   "src/analysis/build_integrated_panel.py"),
    ("Mann-Kendall trends",      "src/analysis/compute_discrepancy_metrics.py"),
    ("Anomaly detection",        "src/analysis/anomaly_detection.py"),
    ("Heckman 2-stage",          "src/analysis/heckman_selection.py"),
    ("SHAP explain",             "src/analysis/shap_explain.py"),
    ("Results summary tables",   "src/analysis/results_summary.py"),
    ("GIR overview figures",     "src/visualization/fig_gir_overview.py"),
    ("Satellite/ODIAC figures",  "src/visualization/fig_satellite_vs_gir.py"),
    ("Trend/pattern figures",    "src/visualization/fig_trends_patterns.py"),
]


def run_step(label: str, script: str) -> bool:
    print(f"\n{'='*60}\n[{label}] {script}\n{'='*60}")
    try:
        r = subprocess.run([PY, str(ROOT / script)], capture_output=True,
                           text=True, timeout=1200)
        if r.returncode == 0:
            # Show last 10 lines
            tail = "\n".join(r.stdout.splitlines()[-10:])
            print(tail)
            print(f"[ok] {label}")
            return True
        else:
            print(f"[FAIL] {label}\nSTDERR:\n{r.stderr[-500:]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] {label}")
        return False


def main() -> None:
    results = []
    for label, script in STEPS:
        ok = run_step(label, script)
        results.append((label, ok))

    print(f"\n\n{'='*60}\nFINAL STATUS\n{'='*60}")
    for label, ok in results:
        icon = "✓" if ok else "✗"
        print(f"  {icon} {label}")


if __name__ == "__main__":
    main()
