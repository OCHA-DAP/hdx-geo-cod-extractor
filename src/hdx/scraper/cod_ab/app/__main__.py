from tqdm import tqdm

from . import checks, download, formats, metadata, scores
from .config import data_dir, logging
from .utils import get_arcgis_update, get_hdx_update, get_iso3_list

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entrypoint into module."""
    logger.info("Starting HDX Geo COD Extractor")
    iso3_list = get_iso3_list()
    pbar = tqdm(iso3_list)
    for iso3 in pbar:
        pbar.set_postfix_str(iso3)
        if iso3 == "PHL":
            continue
        iso3_dir = data_dir / iso3.lower()
        arcgis_update = get_arcgis_update(iso3)
        hdx_update = get_hdx_update(iso3)
        if arcgis_update >= hdx_update:
            iso3_dir.mkdir(exist_ok=True, parents=True)
            if False:
                metadata.main(iso3)
                download.main(iso3)
            checks.main(iso3)
            score = scores.main(iso3)
            if score == 1.0:
                formats.main(iso3)
                logger.info("Pass: %s", iso3)
            else:
                logger.info("Fail: %s", iso3)
    logger.info("Finished HDX Geo COD Extractor")


if __name__ == "__main__":
    main()
