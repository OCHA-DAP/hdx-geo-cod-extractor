from .checks.__main__ import main as checks
from .config import logging
from .download.__main__ import main as download
from .scores.__main__ import main as scores
from .utils import get_arcgis_update, get_hdx_update, get_iso3_list

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entrypoint into module."""
    logger.info("Starting HDX Geo COD Extractor")
    iso3_list = get_iso3_list()
    for iso3 in iso3_list:
        arcgis_update = get_arcgis_update(iso3)
        hdx_update = get_hdx_update(iso3)
        if arcgis_update > hdx_update:
            download(iso3)
            checks(iso3)
            score = scores(iso3)
            if score == 1.0:
                print("pass")
            else:
                print("fail")
    logger.info("Finished HDX Geo COD Extractor")


if __name__ == "__main__":
    main()
