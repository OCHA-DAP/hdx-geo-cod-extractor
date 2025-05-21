#!/usr/bin/python
"""Top level script.

Calls other functions that generate datasets that this script then creates in HDX.
"""

import logging
from os.path import dirname, expanduser, join

from hdx.data.user import User
from hdx.facades.infer_arguments import facade
from hdx.utilities.path import (
    wheretostart_tempdir_batch,
)

from hdx.scraper.cod_ab.cod_ab import CodAb

logger = logging.getLogger(__name__)

_USER_AGENT_LOOKUP = "hdx-scraper-cod-ab"
_UPDATED_BY_SCRIPT = "HDX Scraper: COD-AB"


def main() -> None:
    """Generate datasets and create them in HDX.

    Args:
        save (bool): Save downloaded data. Defaults to True.
        use_saved (bool): Use saved data. Defaults to False.

    Returns:
        None
    """
    if not User.check_current_user_organization_access(
        "ocha-fiss",
        "create_dataset",
    ):
        raise PermissionError(
            "API Token does not give access to <insert org title> organisation!",
        )

    # TODO: Add logic to download the CODs

    with wheretostart_tempdir_batch(folder=_USER_AGENT_LOOKUP) as info:
        cod_ab = CodAb()
        dataset = cod_ab.generate_dataset()
        dataset.update_from_yaml(
            path=join(dirname(__file__), "config", "hdx_dataset_static.yaml"),
        )
        dataset.create_in_hdx(
            remove_additional_resources=True,
            match_resource_order=False,
            hxl_update=False,
            updated_by_script=_UPDATED_BY_SCRIPT,
            batch=info["batch"],
        )


if __name__ == "__main__":
    facade(
        main,
        hdx_site="dev",
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yaml"),
        user_agent_lookup=_USER_AGENT_LOOKUP,
        project_config_yaml=join(
            dirname(__file__),
            "config",
            "project_configuration.yaml",
        ),
    )
