import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.patches import Patch
from common import *

out = sys.argv[1]
rng = np.random.default_rng(11)

layers = ["~250 hPa", "~300 hPa", "~400 hPa", "~500 hPa", "~600 hPa", "~700 hPa", "~850 hPa", "yere yakın"]
nL, nT = len(layers), 48  # 48 half-hour scans = 24 h
t = np.arange(nT) / 2.0   # hours since 21:00 yesterday
z = np.arange(nL)          # 0 = top

# moist anomaly descending from upper layers (~6 h) to lower layers (~20 h);
# dry ahead of it; diurnal heating signal near the surface
front_t = 5.0 + z * 2.1
A = np.tanh((t[None, :] - front_t[:, None]) / 2.2)
A = A - A.mean(axis=1, keepdims=True)
diurnal = np.zeros_like(A)
diurnal[-2:, :] = -0.5 * np.clip(np.sin((t - 12) / 24 * 2 * np.pi * 2), 0, None)[None, :]
A = 3.2 * A / np.abs(A).max() + diurnal + 0.35 * rng.normal(size=A.shape)
A = np.clip(A, -4, 4)

cloud = np.zeros(nT, bool)
cloud[37:41] = True  # a cloud band passes: no IR measurement below cloud top
cloud_top = 2        # cloud top near ~400 hPa -> layers below hidden

fig = card(
    "Ankara üstünde son 24 saat: nem yukarıdan aşağıya indi",
    "Su buharı kanallarında, her katmanın 24 saatlik ortalamasından sapma · her sütun bir 30 dakikalık tarama",
    "Veri: EUMETSAT MTG-S1 IRS (L1, LAC4) · Ankara çevresi 20 km ortalama",
    note="Yükseklikler yaklaşık: kanalın duyarlı olduğu seviye, havanın nemine göre kayar.",
)
ax = fig.add_axes([0.11, 0.19, 0.66, 0.58])
ax.set_facecolor(SURFACE)
levels = np.linspace(-4, 4, 9)
norm = BoundaryNorm(levels, DRY_WET.N)
data = np.ma.array(A, mask=np.zeros_like(A, bool))
data.mask[cloud_top + 1:, cloud] = True
ax.pcolormesh(np.arange(nT + 1), np.arange(nL + 1), data, cmap=DRY_WET, norm=norm,
              edgecolors=SURFACE, linewidth=0.6)
# hidden-by-cloud cells
for i in np.where(cloud)[0]:
    ax.add_patch(plt.Rectangle((i, cloud_top + 1), 1, nL - cloud_top - 1, facecolor="#c3c2b7",
                               edgecolor="#898781", hatch="/////", lw=0, alpha=0.9))
ax.set_ylim(nL, 0)
ax.set_yticks(np.arange(nL) + 0.5)
ax.set_yticklabels(layers, fontsize=7.5)
hours = np.arange(0, nT + 1, 6)
ax.set_xticks(hours)
ax.set_xticklabels(["21:00\ndün", "00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00\nbugün"], fontsize=7.5)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)


# guide along the descending signal
xs = (front_t * 2)
ax.plot(xs, z + 0.5, color=INK, lw=0.9, ls=(0, (3, 2)))
ax.annotate("Nemli hava yukarıdan aşağıya\ninerek yaklaşıyor: cephe geliyor",
            xy=(xs[3], 3.5), xytext=(1, 6.6), fontsize=7.5, color=INK,
            bbox=dict(boxstyle="round,pad=0.35", fc=SURFACE, ec="#c3c2b7", lw=0.5),
            arrowprops=dict(arrowstyle="-", lw=0.6, color=INK))

cax = fig.add_axes([0.80, 0.62, 0.16, 0.035])
sm = plt.cm.ScalarMappable(norm=norm, cmap=DRY_WET)
cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[-4, 0, 4])
cb.ax.set_xticklabels(["daha\nkuru", "ortalama", "daha\nnemli"], fontsize=7.5, color=INK2)
cb.outline.set_visible(False)
cb.ax.tick_params(length=0)
fig.text(0.80, 0.685, "Ortalamaya göre", fontsize=8.5, fontweight="bold", color=INK)
fig.legend(handles=[Patch(facecolor="#c3c2b7", edgecolor="#898781", hatch="/////",
                          label="Bulutun altı, görülemiyor")],
           loc="upper left", bbox_to_anchor=(0.795, 0.48), frameon=False, fontsize=7.5,
           labelcolor=INK2, handlelength=1.4)

watermark(fig)
fig.savefig(out, dpi=DPI, facecolor=SURFACE)
print("saved", out)
