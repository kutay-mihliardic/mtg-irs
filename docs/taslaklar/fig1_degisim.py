import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from common import *

out = sys.argv[1]
rng = np.random.default_rng(7)

lon = np.arange(-14, 50, 0.2)
lat = np.arange(30, 64, 0.2)
LON, LAT = np.meshgrid(lon, lat)


def g(x0, y0, sx, sy, a, rot=0.0):
    c, s = np.cos(rot), np.sin(rot)
    dx, dy = LON - x0, LAT - y0
    u, v = c * dx + s * dy, -s * dx + c * dy
    return a * np.exp(-(u / sx) ** 2 - (v / sy) ** 2)


# moistening band ahead of a trough (Aegean -> W Anatolia -> Black Sea),
# drying behind it over the Balkans / Italy
field = (g(27.5, 38.5, 9, 2.6, 3.4, rot=0.75) + g(33, 42.5, 6, 2.2, 2.0, rot=0.5)
         + g(18, 43, 7, 3, -2.8, rot=0.6) + g(5, 47, 8, 4, 1.4) + g(-5, 40, 6, 4, -1.5)
         + g(40, 37.5, 5, 3, -1.6) + g(14, 56, 9, 4, 1.2))
nz = smooth(smooth(rng.normal(size=field.shape), 25), 25)
field += 0.55 * nz / nz.std()
field = np.clip(field, -4, 4)

cloud = (g(25, 45, 3.5, 1.6, 1, rot=0.7) + g(30.5, 40.6, 2.0, 1.1, 1, rot=0.8)
         + g(8, 50, 5, 2, 1) + g(-8, 55, 4, 3, 1) + g(36, 44.5, 2.5, 1.0, 1))
cn = smooth(rng.normal(size=cloud.shape), 13)
cloud += 0.18 * cn / cn.std()
cloudmask = cloud > 0.55

# lightning: clustered at the moist edge, outside the deepest cloud core
n = 140
cx = np.r_[rng.normal(28.6, 0.9, n // 2), rng.normal(31.0, 0.7, n // 4), rng.normal(26.0, 0.6, n // 4)]
cy = np.r_[rng.normal(37.9, 0.6, n // 2), rng.normal(39.6, 0.5, n // 4), rng.normal(36.6, 0.4, n // 4)]

fig = card(
    "Son 3 saatte Batı Anadolu'da orta katman nemlendi",
    "Orta katmana (~500 hPa) duyarlı su buharı sinyalindeki değişim · 18:00 → 21:00 TSİ",
    "Veri: EUMETSAT MTG-S1 IRS (L1, LAC4) · bulut maskesi: MTG FCI · yıldırım: MTG LI",
    note="Ölçek: su buharı kanallarında parlaklık sıcaklığı değişimi, ±4 K. Bulutlu alanlarda ölçüm yok.",
)
proj = ccrs.LambertConformal(central_longitude=18, central_latitude=46, standard_parallels=(35, 55))
ax = fig.add_axes([0.035, 0.115, 0.69, 0.70], projection=proj)
ax.set_extent([-10, 46, 33, 60], crs=ccrs.PlateCarree())
ax.set_facecolor(SURFACE)
ax.spines["geo"].set_edgecolor("#c3c2b7")
ax.spines["geo"].set_linewidth(0.6)

levels = np.linspace(-4, 4, 9)
norm = BoundaryNorm(levels, DRY_WET.N)
ax.pcolormesh(LON, LAT, field, cmap=DRY_WET, norm=norm, transform=ccrs.PlateCarree(),
              shading="auto", rasterized=True)
ax.contourf(LON, LAT, cloudmask.astype(float), levels=[0.5, 1.5], colors=["#c3c2b7"],
            alpha=0.85, transform=ccrs.PlateCarree())
cs = ax.contourf(LON, LAT, cloudmask.astype(float), levels=[0.5, 1.5], colors="none",
                 hatches=["/////"], transform=ccrs.PlateCarree())
cs.set_edgecolor("#898781")
cs.set_linewidth(0)

ax.add_feature(cfeature.COASTLINE.with_scale("50m"), edgecolor=INK2, linewidth=0.45)
ax.add_feature(cfeature.BORDERS.with_scale("50m"), edgecolor=MUTED, linewidth=0.35)
rec = [r for r in shpreader.Reader(shpreader.natural_earth("50m", "cultural", "admin_0_countries")).records()
       if r.attributes["ADM0_A3"] == "TUR"][0]
ax.add_geometries([rec.geometry], ccrs.PlateCarree(), facecolor="none", edgecolor=INK, linewidth=1.3)

ax.scatter(cx, cy, s=9, c=YELLOW, edgecolors=INK, linewidths=0.35, transform=ccrs.PlateCarree(), zorder=5)

ax.annotate("Ege ve Batı Anadolu:\nnem arttı, yıldırımlar\nnemlenen kuşağın kenarında",
            xy=(28.8, 38.4), xycoords=ccrs.PlateCarree()._as_mpl_transform(ax),
            xytext=(0.40, 0.10), textcoords="axes fraction", fontsize=7.5, color=INK, ha="center",
            bbox=dict(boxstyle="round,pad=0.35", fc=SURFACE, ec="#c3c2b7", lw=0.5),
            arrowprops=dict(arrowstyle="-", color=INK, lw=0.6, shrinkB=2), zorder=6)

# colour bar with words (public) + legend
cax = fig.add_axes([0.785, 0.56, 0.17, 0.035])
sm = plt.cm.ScalarMappable(norm=norm, cmap=DRY_WET)
cb = fig.colorbar(sm, cax=cax, orientation="horizontal", ticks=[-4, 0, 4])
cb.ax.set_xticklabels(["kurudu", "değişim\nyok", "nemlendi"], fontsize=7.5, color=INK2)
cb.outline.set_visible(False)
cb.ax.tick_params(length=0)
fig.text(0.775, 0.62, "Nem değişimi (3 saat)", fontsize=8.5, fontweight="bold", color=INK)

handles = [Patch(facecolor="#c3c2b7", edgecolor="#898781", hatch="/////", label="Bulutlu, görülemiyor"),
           Line2D([], [], marker="o", ls="none", mfc=YELLOW, mec=INK, mew=0.4, ms=4.5,
                  label="Yıldırım, son 1 saat")]
fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.768, 0.43), frameon=False,
           fontsize=7.5, labelcolor=INK2, handlelength=1.4)
fig.text(0.775, 0.25, "Türkiye kalın sınırla\nişaretli.", fontsize=7, color=MUTED, va="top")

watermark(fig)
fig.savefig(out, dpi=DPI, facecolor=SURFACE)
print("saved", out)
