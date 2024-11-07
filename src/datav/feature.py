from pathlib import Path

import cartopy.crs
import cartopy.io.shapereader as shapereader
from cartopy import config
from cartopy.feature import Feature
from cartopy.io import Downloader

from .downloader import DataVGeoAtlasDownloader

_DATAV_GEOATLAS_GEOM_CACHE = {}
"""
Caches a mapping between (name, category, scale) and a tuple of the
resulting geometries.

Provides a significant performance benefit (when combined with object id
caching in GeoAxes.add_geometries) when producing multiple maps of the
same projection.

"""


def datav_geoatlas(
    version: "str | int" = 3, adcode: int = 100000, full: bool = False
) -> Path:
    """
    Return the path to the requested DataV.GeoAtlas shapefile,
    downloading if necessary.

    To identify valid components for this function, either browse
    http://datav.aliyun.com/portal/school/atlas/area_selector, or if you know
    what you are looking for, go to GitHub to see the actual files which will
    be downloaded.
    """
    # get hold of the Downloader (typically a DataVGeoAtlasDownloader instance)
    # which we can then simply call its path method to get the appropriate
    # shapefile (it will download if necessary)
    downloader = Downloader.from_config(
        ("shapefiles", "datav_geoatlas", version, adcode, full)
    )
    format_dict = {
        "config": config,
        "version": "areas_v{}".format(version) if version in (2, 3) else version,
        "adcode": adcode,
        "full": "_full" if full else "",
    }
    return downloader.path(format_dict)


# add a generic DataV.GeoAtlas shapefile downloader to the config dictionary's
# 'downloaders' section.
config["downloaders"].setdefault(
    ("shapefiles", "datav_geoatlas"), DataVGeoAtlasDownloader.default_downloader()
)


class DataVGeoAtlasFeature(Feature):
    """
    A simple interface to Aliyun DataV.GeoAtlas shapefiles.

    See http://datav.aliyun.com/portal/school/atlas/area_selector

    """

    def __init__(self, adcode, full=False, version="areas_v3", **kwargs):
        """
        Parameters
        ----------
        adcode
            The address code of the dataset, i.e. either 100000 (national) or 650000
            (Xinjiang).
        full
            include the subregion or not, default False.
        version
            The dataset version, default `"areas_v3"`.

        Other Parameters
        ----------------
        **kwargs
            Keyword arguments to be used when drawing this feature.

        """
        super().__init__(cartopy.crs.PlateCarree(), **kwargs)

        self.adcode = adcode
        self.full = full
        self.version = version

    def geometries(self):
        """
        Returns an iterator of (shapely) geometries for this feature.

        """
        key = (self.version, self.adcode, self.full)
        if key not in _DATAV_GEOATLAS_GEOM_CACHE:
            path = datav_geoatlas(
                adcode=self.adcode, version=self.version, full=self.full
            )
            geometries = tuple(shapereader.Reader(path).geometries())
            _DATAV_GEOATLAS_GEOM_CACHE[key] = geometries
        else:
            geometries = _DATAV_GEOATLAS_GEOM_CACHE[key]

        return iter(geometries)
