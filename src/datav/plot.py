import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from matplotlib import colormaps
from matplotlib.colors import LinearSegmentedColormap
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, RationalQuadratic, WhiteKernel


def plot_Q(
    Q,
    extent=None,
    shape: tuple[int, int] = (300, 300),
    kernel=None,
    ax=None,
    mask=None,
    gaussian_process_kwargs=None,
):
    """Plot admixture proportions Q.

    Arguments
    ---------
    Q : geopandas.GeoDataFrame
        Admixture proportions.
    extent : (minx, miny, maxx, maxy)
        Extent of the plot. Default is None. If None, the extent is set to
        bounds with 5% margin.
    shape : tuple
        Shape of the interpolated grid. Default is (300, 300).
    kernel : sklearn.gaussian_process.kernels.Kernel
        Kernel for Gaussian process regression. Default is a sum of
        RationalQuadratic, RBF, and WhiteKernel.
    ax : matplotlib.axes.Axes
        Axes for plotting. Default is None.
    mask : geopandas.GeoDataFrame, geopandas.GeoSeries, shapely.(Multi)Polygon, list-like
        Polygon to clip the plot. Typically, this is the land mask.
    """
    if gaussian_process_kwargs is None:
        gaussian_process_kwargs = {}
    if "kernel" not in gaussian_process_kwargs:
        # Kriging kernel
        gaussian_process_kwargs["kernel"] = (
            RationalQuadratic(alpha=0.1, length_scale=1.0)
            + RBF(length_scale=1.0)
            + WhiteKernel(noise_level=0.1)
        )
    if ax is None:
        ax = plt.axes(projection=ccrs.PlateCarree())
    if mask is None:
        mask = gpd.GeoSeries(cfeature.LAND.geometries(), crs="EPSG:4326")
    if extent is None:
        minx, miny, maxx, maxy = Q.total_bounds
        marginx = 0.05 * (maxx - minx)
        marginy = 0.05 * (maxy - miny)
        extent = (minx - marginx, miny - marginy, maxx + marginx, maxy + marginy)
    (minx, miny, maxx, maxy) = extent
    coords = {
        "q": [q for q in Q.columns if q != "geometry"],
        "x": np.linspace(minx, maxx, shape[0]),
        "y": np.linspace(miny, maxy, shape[1]),
    }
    X, Y = np.meshgrid(coords["x"], coords["y"])
    points = gpd.GeoSeries.from_xy(X.ravel(), Y.ravel(), crs="EPSG:4326").clip(mask)
    points_mask = np.zeros(shape, dtype=bool)
    points_mask[points.index % shape[0], points.index // shape[0]] = True
    coo = np.vstack([Q.geometry.x, Q.geometry.y])
    coo_pred = np.vstack([X.ravel(), Y.ravel()])
    pred = []
    for q in coords["q"]:
        Z = Q[q].values
        gp = GaussianProcessRegressor(**gaussian_process_kwargs)
        gp.fit(coo.T, Z)
        Q_pred = gp.predict(coo_pred.T).reshape(shape)
        Q_pred = np.clip(Q_pred, 0, 1)
        pred.append(Q_pred)
    da = xr.DataArray(np.stack(pred), dims=["q", "x", "y"], coords=coords)
    # Normalize
    da = da / da.sum(dim="q")

    max_idx = da.argmax(dim="q")

    cm = colormaps["tab10"](np.linspace(0, 1, len(coords["q"])))
    colors = {q: cm[i] for i, q in enumerate(coords["q"])}
    for q in coords["q"]:
        cmap = LinearSegmentedColormap.from_list("cmap", ["#F5F5F5", colors[q]])
        m = (max_idx == q) & points_mask
        da.sel(q=q).where(m).plot.contourf(
            x="x",
            y="y",
            ax=ax,
            cmap=cmap,
            add_colorbar=False,
        )
