DataV
-----

This is an unofficial solution to draw map using Aliyun's DataV.GeoAtlas.

这是一个非官方的使用阿里云 DataV.GeoAtlas 绘制地图的解决方案。


## Examples

```python
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib.transforms import offset_copy
from matplotlib.font_manager import FontProperties

from datav import DataVGeoAtlasFeature

# Windows 下字体可以不用这么麻烦，直接 rc 设置 SimSun 即可
simsun = FontProperties(fname="/mnt/c/Windows/Fonts/simsun.ttc")

proj = ccrs.PlateCarree()
fig = plt.figure(figsize=(14, 7))
main_box = (80.5, 82, 40.25, 41)
ax_main = plt.subplot(1, 1, 1, projection=proj)
ax_main.set_extent(main_box, crs=ccrs.PlateCarree())
ax_main.add_feature(DataVGeoAtlasFeature(659002, facecolor="darkgreen", alpha=0.2))  # 阿拉尔
ax_main.add_feature(cfeature.LAKES)
ax_main.add_feature(cfeature.RIVERS)
site = (81.196, 40.624)
ax_main.plot(
    *site,
    marker="o",
    color="green",
    markersize=10,
    transform=ccrs.Geodetic(),
)
geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax_main)
text_transform = offset_copy(geodetic_transform, units="dots", x=-25)
ax_main.text(
    site[0],
    site[1] + 0.03,
    "试验站",
    transform=text_transform,
    fontproperties=simsun,
)
xmain = np.linspace(*main_box[:2], 4)
ymain = np.linspace(*main_box[2:], 4)
ax_main.gridlines(xlocs=xmain, ylocs=ymain, linestyle=":")
# set custom formatting for the tick labels
ax_main.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
ax_main.yaxis.set_major_formatter(LATITUDE_FORMATTER)
ax_main.yaxis.tick_right()
ax_main.set_xticks(xmain, crs=ccrs.PlateCarree())
ax_main.set_yticks(ymain, crs=ccrs.PlateCarree())

ax_inset = fig.add_axes([0, 0.6, 0.3, 0.35], projection=proj)
ax_inset.set_extent((73, 136, 2, 51))
ax_inset.add_feature(
    DataVGeoAtlasFeature(100000, full=True, facecolor="lightgreen", edgecolor="gray")
)
ax_inset.add_feature(DataVGeoAtlasFeature(650000, facecolor="limegreen"))
ax_inset.add_feature(DataVGeoAtlasFeature(652900, facecolor="green", edgecolor="none"))
ax_inset.add_feature(
    DataVGeoAtlasFeature(659002, facecolor="darkgreen", edgecolor="black")
)
xinset = np.linspace(73, 136, 5)
yinset = np.linspace(2, 51, 5)
ax_inset.gridlines(xlocs=xinset, ylocs=yinset, linestyle=":")
ax_inset.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
ax_inset.yaxis.set_major_formatter(LATITUDE_FORMATTER)
ax_inset.xaxis.tick_top()
# set inset tick labels
ax_inset.set_xticks(xinset, crs=ccrs.PlateCarree())
ax_inset.set_yticks(yinset, crs=ccrs.PlateCarree())

plt.savefig("research_site.png", dpi=800)
```

![Research site](research_site.png)

## Requirements

1. Cartopy (for ploting)
2. Geopandas (for parsing geojson)

## NOTE

Free For Educational Use. Respect Aliyun's license. 

仅供学习使用。遵守阿里云的协议。请合理使用地图数据。数据内容和本人无关。数据具体用途也和本人无关。请遵守相关法律规定。

## TODO

1. respect the HTTP header last-modified

   尊重 HTTP 请求头 last-modified

2. Chinese name alias for adcode

   使用中文名替代 adcode 查询

3. More features such as line

   从 GeoJSON 中提取更多可定制的 feature。
