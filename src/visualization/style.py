"""Publication-quality matplotlib/seaborn style for AX contest report.

Korean fonts: Noto Sans KR (if installed) or Malgun Gothic (Windows default).
Palette: Okabe-Ito colorblind-safe.
"""
from __future__ import annotations

import platform
import matplotlib as mpl
import matplotlib.pyplot as plt

# Okabe-Ito palette (colorblind-safe)
OKABE_ITO = {
    "black":   "#000000",
    "orange":  "#E69F00",
    "skyblue": "#56B4E9",
    "green":   "#009E73",
    "yellow":  "#F0E442",
    "blue":    "#0072B2",
    "red":     "#D55E00",
    "pink":    "#CC79A7",
    "gray":    "#999999",
}

# Pattern colors (Patterns A/B/C/D/E)
PATTERN_COLORS = {
    "A_consistent_up":   OKABE_ITO["green"],
    "A_consistent_down": OKABE_ITO["blue"],
    "B_esg_suspect":     OKABE_ITO["orange"],
    "C_gir_suspect":     OKABE_ITO["pink"],
    "D_both_suspect":    OKABE_ITO["red"],
    "E_no_trend":        OKABE_ITO["gray"],
    "mixed":             OKABE_ITO["yellow"],
}

# Industry colors
INDUSTRY_COLORS = {
    "steel":         OKABE_ITO["red"],
    "petrochem":     OKABE_ITO["orange"],
    "power_coal":    OKABE_ITO["black"],
    "semiconductor": OKABE_ITO["skyblue"],
    "finance":       OKABE_ITO["gray"],
    "other":         OKABE_ITO["pink"],
}


def setup_style() -> None:
    """Apply global matplotlib style."""
    plt.rcParams.update({
        # Fonts
        "font.family": "Malgun Gothic" if platform.system() == "Windows" else "Noto Sans CJK KR",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "figure.titlesize": 13,
        # Figure
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        # Grid & spines
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linewidth": 0.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        # Lines
        "lines.linewidth": 1.5,
        "lines.markersize": 5,
        # Unicode minus
        "axes.unicode_minus": False,
    })
