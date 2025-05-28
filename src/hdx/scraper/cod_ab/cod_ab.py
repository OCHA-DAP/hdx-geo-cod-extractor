#!/usr/bin/python
"""cod_ab scraper."""

import logging
from os.path import join

from hdx.data.dataset import Dataset
from hdx.data.organization import Organization
from hdx.data.resource import Resource
from hdx.location.country import Country

from hdx.scraper.cod_ab.config import data_dir

logger = logging.getLogger(__name__)


def generate_dataset(metadata: dict, iso3: str) -> Dataset | None:
    country_name = Country.get_country_name_from_iso3(iso3)
    if not country_name:
        logger.error(f"Country not found for {iso3}")
        return None
    dataset_name = f"{iso3.lower()}-cod-ab"
    dataset_title = f"{country_name} - Subnational Administrative Boundaries"
    dataset = Dataset(
        {
            "name": dataset_name,
            "title": dataset_title,
        },
    )

    dataset_time_start = metadata["all"]["date_established"]
    dataset_time_end = metadata["all"]["date_reviewed"]
    dataset.set_time_period(dataset_time_start, dataset_time_end)

    dataset_tags = ["administrative boundaries-divisions", "gazetteer"]
    dataset.add_tags(dataset_tags)

    dataset.add_country_location(iso3)

    orig_org = metadata["contributor"]
    org = Organization.autocomplete(orig_org)
    if len(org) != 1:
        logger.error(f"Matching organization not found for {orig_org}")
        return None
    dataset.set_organization(org[0])

    dataset["source"] = metadata["source"]
    dataset["caveats"] = ""  # TODO: fill in caveats (are these static or dynamic?)
    dataset["notes"] = compile_notes(metadata)

    # Add resources
    for ext, format_type in [
        ("gdb.zip", "Geodatabase"),
        ("shp.zip", "Shapefile"),
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
            join(data_dir, iso3.lower(), f"{iso3.lower()}_cod_ab.{ext}")
        )
        resource.set_format(format_type)
        dataset.add_update_resource(resource)
        if format_type == "Shapefile":
            resource.enable_dataset_preview()

    dataset.preview_resource()

    return dataset


# TODO: write function to compile notes from COD metadata
def compile_notes(metadata: dict) -> str:
    return ""
