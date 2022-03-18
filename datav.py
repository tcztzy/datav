import os
from typing import Union

import cartopy.crs
from cartopy import config
from cartopy.feature import Feature
from cartopy.io import Downloader, shapereader

_DATAV_GEOATLAS_GEOM_CACHE = {}
"""
Caches a mapping between (name, category, scale) and a tuple of the
resulting geometries.

Provides a significant performance benefit (when combined with object id
caching in GeoAxes.add_geometries) when producing multiple maps of the
same projection.

"""


def datav_geoatlas(
    version: Union[str, int] = 3, adcode: int = 100000, full: bool = False
):
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


class DataVGeoAtlasDownloader(Downloader):
    """
    Specialise :class:`cartopy.io.Downloader` to download the geojson
    DataV.GeoAtlas shapefiles and extract them to the defined location
    (typically user configurable).

    The keys which should be passed through when using the ``format_dict``
    are typically ``category``, ``resolution`` and ``name``.
    """

    FORMAT_KEYS = ("config", "version", "adcode", "full")

    _DATAV_GEOATLAS_URL_TEMPLATE = (
        "https://geo.datav.aliyun.com/{version}/bound/{adcode}{full}.json"
    )

    def __init__(
        self,
        url_template=_DATAV_GEOATLAS_URL_TEMPLATE,
        target_path_template=None,
        pre_downloaded_path_template="",
    ):
        # adds some GeoAtlas defaults to the __init__ of a Downloader
        Downloader.__init__(
            self, url_template, target_path_template, pre_downloaded_path_template
        )

    @staticmethod
    def default_downloader():
        """
        Return a generic, standard, DataVGeoAtlasDownloader instance.

        Typically, a user will not need to call this staticmethod.

        To find the path template of the DataVGeoAtlasDownloader:

            >>> dnldr = DataVGeoAtlasDownloader.default_downloader()
            >>> print(dnldr.target_path_template)
            {config[data_dir]}/shapefiles/datav_geoatlas/{version}/\
geoatlas_{adcode}{full}.json

        """
        default_spec = (
            "shapefiles",
            "datav_geoatlas",
            "{version}",
            "geoatlas_{adcode}{full}.json",
        )
        target_path_template = os.path.join("{config[data_dir]}", *default_spec)
        pre_path_template = os.path.join(
            "{config[pre_existing_data_dir]}", *default_spec
        )
        return DataVGeoAtlasDownloader(
            target_path_template=target_path_template,
            pre_downloaded_path_template=pre_path_template,
        )


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
            The address code of the dataset, i.e. either 100000 (national) or 650000 (Xinjiang).
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
