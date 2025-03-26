from .checks.__main__ import main as checks
from .config import logging
from .download.__main__ import main as download
from .scores.__main__ import main as scores

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entrypoint into module."""
    logger.info("Starting HDX Geo COD Extractor")
    download()
    checks()
    scores()
    logger.info("Finished HDX Geo COD Extractor")


if __name__ == "__main__":
    main()
