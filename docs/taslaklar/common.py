"""Shared template for the synthetic-data mockups (X/Twitter 16:9 card)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

for f in font_manager.findSystemFonts():
    if "Inter" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": "Inter",
    "font.size": 9,
    "axes.edgecolor": "#c3c2b7",
    "axes.labelcolor": "#52514e",
    "xtick.color": "#898781",
    "ytick.color": "#898781",
    "axes.linewidth": 0.6,
})

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
NEUTRAL = "#f0efec"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
YELLOW = "#eda100"
WARNING = "#fab219"

# Diverging: brown (dried) <- gray -> blue (moistened). Equal steps per arm.
DRY_WET = LinearSegmentedColormap.from_list(
    "drywet",
    ["#6b4220", "#a8763f", "#d9bc95", NEUTRAL, "#9ec5f4", "#3987e5", "#184f95"],
)

W, H, DPI = 8.0, 4.5, 200  # 1600x900 px


def card(title, subtitle, source, note=None):
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=SURFACE)
    fig.text(0.035, 0.935, title, fontsize=14.5, fontweight="bold", color=INK, va="top")
    fig.text(0.035, 0.862, subtitle, fontsize=9, color=INK2, va="top")
    fig.text(0.035, 0.03, source, fontsize=7.5, color=MUTED, va="bottom")
    if note:
        fig.text(0.035, 0.065, note, fontsize=7, color=MUTED, va="bottom", style="italic")
    fig.text(0.965, 0.03, "mtg-irs", fontsize=7.5, color=MUTED, va="bottom", ha="right",
             fontweight="bold")
    # draft badge (label + color, never color alone)
    fig.text(0.965, 0.94, "DRAFT · SYNTHETIC DATA", fontsize=7.5, fontweight="bold",
             color=INK, ha="right", va="top",
             bbox=dict(boxstyle="round,pad=0.45", fc=WARNING, ec="none"))
    return fig


def watermark(fig):
    fig.text(0.45, 0.45, "SAMPLE DATA — not a real measurement", fontsize=26, color=INK,
             alpha=0.07, ha="center", va="center", rotation=12, fontweight="bold",
             zorder=100)


def smooth(a, k=9):
    """Separable box-ish smoothing without scipy."""
    ker = np.hanning(k + 2)[1:-1]
    ker /= ker.sum()
    a = np.apply_along_axis(lambda r: np.convolve(r, ker, mode="same"), 0, a)
    return np.apply_along_axis(lambda r: np.convolve(r, ker, mode="same"), 1, a)
