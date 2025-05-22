#!/usr/bin/python
"""cod_ab scraper."""

import logging

from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.data.resource import Resource

from hdx.scraper.cod_ab.config import data_dir

logger = logging.getLogger(__name__)


class CodAb:
    def generate_dataset(self, metadata: dict, iso3: str) -> Dataset | None:
        # To be generated
        dataset_name = f"{iso3.lower()}-cod-ab-2"
        dataset_title = f"{iso3} - Subnational Administrative Boundaries"
        dataset_description = (
            f"{iso3} - Subnational Administrative Boundaries from FIS server"
        )
        dataset_time_start = metadata["all"]["date_established"]
        dataset_time_end = metadata["all"]["date_reviewed"]
        dataset_tags = ["administrative boundaries-divisions"]
        dataset_country_iso3 = iso3

        # Dataset info
        dataset = Dataset(
            {
                "name": dataset_name,
                "title": dataset_title,
                "description": dataset_description,
                "notes": "",
            },
        )

        dataset.set_time_period(dataset_time_start, dataset_time_end)
        dataset.add_tags(dataset_tags)
        # Only if needed
        dataset.set_subnational(True)
        try:
            dataset.add_country_location(dataset_country_iso3)
        except HDXError:
            logger.error(f"Couldn't find country {dataset_country_iso3}, skipping")
            return None

        # Add resources here
        for ext, format_type in [
            ("gdb.zip", "Geodatabase"),
            ("shp.zip", "zipped shapefile"),
            ("geojson.zip", "GeoJSON"),
            ("xlsx", "XLSX"),
        ]:
            resource = Resource(
                {
                    "name": f"{iso3} {format_type}",
                    "description": f"{iso3} {format_type}",
                }
            )
            resource.set_file_to_upload(
                data_dir / iso3.lower() / f"{iso3.lower()}_cod_ab.{ext}"
            )
            resource.set_format(format_type)
            resource.set_date_data_updated(dataset_time_end)
            dataset.add_update_resource(resource)

        return dataset
