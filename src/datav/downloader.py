import os

from cartopy.io import Downloader


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
