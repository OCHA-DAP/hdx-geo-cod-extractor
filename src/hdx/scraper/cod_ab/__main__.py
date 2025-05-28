#!/usr/bin/python
"""Top level script.

Calls other functions that generate datasets that this script then creates in HDX.
"""

import logging
from os.path import dirname, expanduser, join
from shutil import rmtree

from hdx.data.user import User
from hdx.facades.infer_arguments import facade
from hdx.utilities.path import wheretostart_tempdir_batch
from tqdm import tqdm

from hdx.scraper.cod_ab import checks, download, formats, metadata, scores
from hdx.scraper.cod_ab.cod_ab import generate_dataset
from hdx.scraper.cod_ab.config import DEBUG, data_dir
from hdx.scraper.cod_ab.utils import (
    get_arcgis_update,
    get_hdx_update,
    get_iso3_list,
)

logger = logging.getLogger(__name__)

_USER_AGENT_LOOKUP = "hdx-scraper-cod-ab"
_UPDATED_BY_SCRIPT = "HDX Scraper: COD-AB"
PASS = 1.0


def main() -> None:
    """Generate datasets and create them in HDX."""
    if not User.check_current_user_organization_access("ocha-fiss", "create_dataset"):
        raise PermissionError(
            "API Token does not give access to OCHA FISS organisation!",
        )

    with wheretostart_tempdir_batch(folder=_USER_AGENT_LOOKUP) as info:
        iso3_list = get_iso3_list()
        pbar = tqdm(iso3_list)
        for iso3 in pbar:
            pbar.set_postfix_str(iso3)
            iso3_dir = data_dir / iso3.lower()
            arcgis_update = get_arcgis_update(iso3)
            hdx_update = get_hdx_update(iso3)
            if arcgis_update >= hdx_update:
                iso3_dir.mkdir(exist_ok=True, parents=True)
                meta_dict = metadata.main(iso3)
                if DEBUG and not iso3_dir.exists():
                    download.main(iso3)
                    formats.main(iso3)
                    checks.main(iso3)
                score = scores.main(iso3)
                if (
                    score == PASS
                    and meta_dict
                    and meta_dict.get("all", {}).get("date_established")
                    and meta_dict.get("all", {}).get("date_reviewed")
                ):
                    dataset = generate_dataset(meta_dict, iso3)
                    if not dataset:
                        continue
                    dataset.update_from_yaml(
                        path=join(
                            dirname(__file__), "config", "hdx_dataset_static.yaml"
                        ),
                    )
                    dataset.create_in_hdx(
                        remove_additional_resources=True,
                        match_resource_order=False,
                        hxl_update=False,
                        updated_by_script=_UPDATED_BY_SCRIPT,
                        batch=info["batch"],
                    )
                    logger.info("Pass: %s", iso3)
                else:
                    logger.info("Fail: %s", iso3)
                if not DEBUG:
                    rmtree(iso3_dir, ignore_errors=True)


if __name__ == "__main__":
    facade(
        main,
        hdx_site="dev",
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=_USER_AGENT_LOOKUP,
        project_config_yaml=join(
            dirname(__file__), "config", "project_configuration.yaml"
        ),
    )
