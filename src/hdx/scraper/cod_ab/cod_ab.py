#!/usr/bin/python
"""cod_ab scraper."""

import logging

from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError

logger = logging.getLogger(__name__)


class CodAb:
    def generate_dataset(self) -> Dataset | None:
        # To be generated
        dataset_name = None
        dataset_title = None
        dataset_time_period = None
        dataset_tags = None
        dataset_country_iso3 = None

        # Dataset info
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
            },
        )

        dataset.set_time_period(dataset_time_period)
        dataset.add_tags(dataset_tags)
        # Only if needed
        dataset.set_subnational(True)
        try:
            dataset.add_country_location(dataset_country_iso3)
        except HDXError:
            logger.error(f"Couldn't find country {dataset_country_iso3}, skipping")
            return None

        # Add resources here

        return dataset
