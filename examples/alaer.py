import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib.transforms import offset_copy
from matplotlib.font_manager import FontProperties

from datav import DataVGeoAtlasFeature

# Windows 下字体可以不用这么麻烦，直接 rc 设置 SimSun 即可
simsun = FontProperties("Songti SC")

# 地图投影方式
proj = ccrs.PlateCarree()
fig = plt.figure(figsize=(14, 7))
# 经纬度的盒子, 分别是最小经度, 最大经度, 最小纬度, 最大纬度
main_box = (80.5, 82, 40.25, 41)
# 主Axes, 用来画具体的研究区域
ax_main = plt.subplot(1, 1, 1, projection=proj)
# 设置主ax的经纬度盒子和投影方式
ax_main.set_extent(main_box, crs=ccrs.PlateCarree())
# 添加 DataV 的图层, 也就是行政区域
ax_main.add_feature(DataVGeoAtlasFeature(659002, facecolor="darkgreen", alpha=0.2))
# 添加河流湖泊的图层
ax_main.add_feature(cfeature.LAKES)
ax_main.add_feature(cfeature.RIVERS)
# 试验站的具体经纬度
site = (81.196, 40.624)
ax_main.plot(
    *site,
    marker="o",
    color="green",
    markersize=10,
    transform=ccrs.Geodetic(),
)
# 生成 text 的转换(transform), 用于将试验站的名称标注在数据点旁边
geodetic_transform = ccrs.Geodetic()._as_mpl_transform(ax_main)
text_transform = offset_copy(geodetic_transform, units="dots", x=-25)
ax_main.text(
    site[0],
    site[1] + 0.03,  # 添加一个向北的偏移量, 让字不要挡着数据点
    "试验站",
    transform=text_transform,
    fontproperties=simsun,
)
# 添加经纬度的网格线
xmain = np.linspace(*main_box[:2], 4)
ymain = np.linspace(*main_box[2:], 4)
ax_main.gridlines(xlocs=xmain, ylocs=ymain, linestyle=":")
# set custom formatting for the tick labels
ax_main.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
ax_main.yaxis.set_major_formatter(LATITUDE_FORMATTER)
# 将纬度的标记翻到图片外面
ax_main.yaxis.tick_right()
ax_main.set_xticks(xmain, crs=ccrs.PlateCarree())
ax_main.set_yticks(ymain, crs=ccrs.PlateCarree())

# 绘制全国概况, 位置可酌情调整
ax_inset = fig.add_axes([0, 0.6, 0.3, 0.35], projection=proj)
# 经纬度盒子, 同上
ax_inset.set_extent((73, 136, 2, 51))
# 添加全国的行政区域
ax_inset.add_feature(
    DataVGeoAtlasFeature(100000, full=True, facecolor="lightgreen", edgecolor="gray")
)
# 新疆
ax_inset.add_feature(DataVGeoAtlasFeature(650000, facecolor="limegreen"))
# 阿克苏
ax_inset.add_feature(DataVGeoAtlasFeature(652900, facecolor="green", edgecolor="none"))
# 阿拉尔, 随着行政级别颜色逐渐加深
ax_inset.add_feature(
    DataVGeoAtlasFeature(659002, facecolor="darkgreen", edgecolor="black")
)
# 下方代码同上
xinset = np.linspace(73, 136, 5)
yinset = np.linspace(2, 51, 5)
ax_inset.gridlines(xlocs=xinset, ylocs=yinset, linestyle=":")
ax_inset.xaxis.set_major_formatter(LONGITUDE_FORMATTER)
ax_inset.yaxis.set_major_formatter(LATITUDE_FORMATTER)
ax_inset.xaxis.tick_top()
# set inset tick labels
ax_inset.set_xticks(xinset, crs=ccrs.PlateCarree())
ax_inset.set_yticks(yinset, crs=ccrs.PlateCarree())

# 保存图片, 可调整DPI, 越大越清晰
plt.savefig("research_site.png", dpi=800)
