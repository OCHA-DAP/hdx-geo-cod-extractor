from app.config import ADMIN_LEVELS, checks_config, data_dir
from geopandas import read_parquet
from pandas import DataFrame

from . import (
    attribute_match,
    dates,
    geometry_gaps,
    geometry_overlaps_self,
    geometry_valid,
    geometry_within_parent,
    languages,
    table_names,
    table_other,
    table_pcodes,
)


def create_output(iso3: str, checks: list) -> None:
    """Create CSV from registered checks."""
    output = None
    for _, results in checks:
        rows = [row for result in results for row in result]
        partial = DataFrame(rows).convert_dtypes()
        if output is None or output.empty:
            output = partial
        else:
            output = output.merge(partial, on=["iso3", "level"], how="outer")
    if output is not None and not output.empty:
        dest = data_dir / iso3.lower() / f"{iso3.lower()}_checks.csv"
        output.to_csv(dest, encoding="utf-8-sig", index=False)


def main(iso3: str) -> None:
    """Summarizes and describes the data contained within downloaded boundaries.

    1. Create an iterable with each item containing the following (check_function,
    results_list).

    2. Iterate through ISO3 values, creating a list of GeoDataFrames containing admin
    levels 0-n.

    3. Iterate through the check functions, passing to them the results list for that
    check as well as boundary data needed for checking.

    4. When all checks have run against the ISO3's GeoDataFrames, they are released from
    memory and a new ISO3 is loaded in.

    5. After all the checks have been performed for all ISO3 values, join the check
    tables together by ISO3 and admin level.

    6. Output the final result as a single table: "data/tables/checks.csv".
    """
    checks = [
        (geometry_valid, []),
        (geometry_gaps, []),
        (geometry_overlaps_self, []),
        (geometry_within_parent, []),
        (attribute_match, []),
        (table_pcodes, []),
        (table_names, []),
        (dates, []),
        (languages, []),
        (table_other, []),
    ]
    gdfs = []
    levels = ADMIN_LEVELS
    if iso3 in checks_config["max_level"]:
        levels = checks_config["max_level"][iso3]
    for level in range(levels + 1):
        file_path = data_dir / iso3.lower() / f"{iso3.lower()}_admin{level}.parquet"
        if file_path.exists():
            gdf = read_parquet(file_path)
            gdfs.append(gdf)
    for function, results in checks:
        result = function.main(iso3, gdfs)
        results.append(result)
    create_output(iso3, checks)
