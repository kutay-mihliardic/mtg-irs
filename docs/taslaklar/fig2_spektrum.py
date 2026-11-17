import sys
import numpy as np
import matplotlib.pyplot as plt
from common import *

out = sys.argv[1]
rng = np.random.default_rng(3)

# IRS sampling: LWIR 680-1210 cm-1, MWIR 1600-2250 cm-1, 0.625 cm-1
nu_l = np.arange(680, 1210, 0.625)
nu_m = np.arange(1600, 2250, 0.625)


def lines(nu, centers, width, depth):
    o = np.zeros_like(nu)
    for c, d in zip(centers, depth):
        o += d / (1 + ((nu - c) / width) ** 2)
    return o


def emission_height(nu, moist):
    """Synthetic 'height the channel sees' (km)."""
    h = np.full_like(nu, 0.0)
    # CO2 15 um band: high near 680, falling to surface by ~770
    co2 = 15 * np.exp(-((nu - 667) / 45) ** 2)
    c = rng.uniform(680, 790, 70)
    co2 += lines(nu, c, 0.6, 4 * np.exp(-((c - 667) / 60) ** 2) + 0.3)
    h += co2
    # water vapour continuum + weak lines in the window (more if moist)
    h += moist * (0.15 + 1.0 * np.exp(-((nu - 780) / 60) ** 2) + 2.0 * np.clip((nu - 1100) / 110, 0, 1) ** 2)
    c = rng.uniform(780, 1210, 60)
    h += moist * lines(nu, c, 0.5, rng.uniform(0.3, 1.5, 60))
    # ozone 9.6 um
    h += 5.5 * np.exp(-((nu - 1042) / 22) ** 2) * (0.7 + 0.3 * np.abs(np.sin(nu * 0.9)))
    # water vapour 6.3 um band
    wv = np.exp(-((nu - 1595) / 260) ** 2) * (np.clip(nu - 1580, 0, None) > 0)
    c = rng.uniform(1600, 2000, 160)
    wv_lines = lines(nu, c, 0.7, rng.uniform(0.5, 2.5, 160))
    h += (3.5 + 3.8 * moist) * wv + wv_lines * (0.5 + 0.5 * moist) * (nu < 2000)
    # partial window 2000-2150 with CO / N2O lines, then CO2 4.3 um edge
    c = rng.uniform(2050, 2240, 50)
    h += lines(nu, c, 0.6, rng.uniform(0.3, 2.0, 50)) * (nu > 2000)
    h += 11 * np.clip((nu - 2180) / 70, 0, 1) ** 2.2
    return h


def temp_profile(h, ts):
    t = np.where(h < 11, ts - 6.5 * h, ts - 6.5 * 11)
    t = np.where(h > 20, ts - 6.5 * 11 + 1.6 * (h - 20), t)
    return t


WIN = {}
cities = [("Istanbul", 13.0, 1.0, BLUE), ("Van", -3.0, 0.15, ORANGE)]

fig = card(
    "One pixel, 1953 channels: the atmosphere's fingerprint",
    "Each channel 'hears' a different height in the atmosphere. Plotted: the temperature each channel sees (°C) · 21:00 TRT",
    "Data: EUMETSAT MTG-S1 IRS (L1, LAC4) · brightness temperature, ~4 km pixel",
    note="IRS does not measure the 1210–1600 cm⁻¹ range.",
)
gs = fig.add_gridspec(1, 2, left=0.075, right=0.965, top=0.66, bottom=0.17,
                      width_ratios=[len(nu_l), len(nu_m)], wspace=0.04)
axl = fig.add_subplot(gs[0])
axm = fig.add_subplot(gs[1], sharey=axl)

bands_l = [(680, 760, "CO₂", "15 µm"),
           (790, 980, "Window", "11 µm"),
           (1000, 1075, "Ozone", "9.6 µm"),
           (1090, 1210, "Window", "8.7 µm")]
bands_m = [(1600, 1990, "Water vapour", "6.3 µm"),
           (2030, 2160, "Partial window", "4.8 µm"),
           (2175, 2250, "N₂O·CO₂", "4.5 µm")]

for ax, nu, bands in [(axl, nu_l, bands_l), (axm, nu_m, bands_m)]:
    ax.set_facecolor(SURFACE)
    for i, (a, b, name, sub) in enumerate(bands):
        ax.axvspan(a, b, color=NEUTRAL, zorder=0, lw=0)
        ax.text((a + b) / 2, 1.06, name, transform=ax.get_xaxis_transform(), ha="center",
                va="bottom", fontsize=7.3, fontweight="bold", color=INK2)
        ax.text((a + b) / 2, 1.015, sub, transform=ax.get_xaxis_transform(), ha="center",
                va="bottom", fontsize=6.5, color=MUTED)
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=7.5)
    for name, ts, moist, col in cities:
        bt = temp_profile(emission_height(nu, moist), ts) + rng.normal(0, 0.25, nu.size)
        if nu[0] < 1000:
            WIN[name] = np.median(bt[(nu > 850) & (nu < 950)])
        ax.plot(nu, bt, color=col, lw=0.75, label=name, zorder=3 if col == BLUE else 2)
    ax.set_xlim(nu[0], nu[-1])

axm.tick_params(labelleft=False)
axm.spines["left"].set_visible(False)
axl.set_ylim(-68, 22)
axl.set_ylabel("Temperature seen by the channel (°C)", fontsize=8)
fig.text(0.52, 0.105, "Wavenumber (cm⁻¹)", ha="center", fontsize=8, color=INK2)

axl.set_xticks([700, 800, 900, 1000, 1100])
axm.set_xticks([1700, 1800, 1900, 2000, 2100, 2200])

# direct labels + legend (2 series)
axl.text(840, WIN["Istanbul"] + 3, "Istanbul (moist, mild)", color=INK, fontsize=7.5, fontweight="bold")
axl.text(840, WIN["Van"] - 7, "Van (dry, cold)", color=INK, fontsize=7.5, fontweight="bold")
fig.legend(handles=axl.get_lines()[:2], loc="upper left", bbox_to_anchor=(0.03, 0.83), ncol=2,
           frameon=False, fontsize=7.5, handlelength=1.5, labelcolor=INK2)

axl.annotate("CO₂ band centre sees\nthe stratosphere: −56 °C", xy=(684, -55), xytext=(790, -60),
             fontsize=7, color=INK, va="center",
             arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
axl.annotate(f"Window channels see the air near the ground:\nIstanbul ≈ {WIN['Istanbul']:+.0f} °C, Van ≈ {WIN['Van']:+.0f} °C".replace("-", "−"),
             xy=(930, WIN["Van"]), xytext=(790, -33), fontsize=7, color=INK, ha="left",
             bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec="#c3c2b7", lw=0.5),
             arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))
axm.annotate("In moist air, water-vapour channels\nsee higher up, i.e. colder air",
             xy=(1840, -40), xytext=(1610, 4), fontsize=7, color=INK,
             bbox=dict(boxstyle="round,pad=0.3", fc=SURFACE, ec="#c3c2b7", lw=0.5),
             arrowprops=dict(arrowstyle="-", lw=0.5, color=INK))

watermark(fig)
fig.savefig(out, dpi=DPI, facecolor=SURFACE)
print("saved", out)
