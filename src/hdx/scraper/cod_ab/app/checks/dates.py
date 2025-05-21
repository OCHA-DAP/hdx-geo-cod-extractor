from app.config import VALID_ON, VALID_TO
from geopandas import GeoDataFrame


def main(iso3: str, gdfs: list[GeoDataFrame]) -> list[dict]:
    """Checks for unique date values within dataset.

    There are two date fields within each COD-AB, "valid_on" and "valid_to". "valid_on"
    represents when this dataset was last changed throughout the data update lifecycle.
    If there are multiple unique values for dates within the dataset, they will be
    listed in separate output columns: "valid_on", "valid_on_1", "valid_on_2", etc.

    The following are a list of source and output columns:
    - source: "valid_on"
        - output: "valid_on_count", "valid_on", "valid_on_1", etc...

    Args:
        iso3: ISO3 code of the current location being checked.
        gdfs: List of GeoDataFrames, with the item at index 0 corresponding to admin
        level 0, index 1 to admin level 1, etc.

    Returns:
        List of results from this check to output as a CSV.
    """
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        row = {
            "iso3": iso3,
            "level": admin_level,
            "valid_on_type": None,
            "valid_on_count": 0,
            "valid_to_type": None,
            "valid_to_exists": 0,
            "valid_to_empty": 0,
        }
        try:
            gdf_valid_on = gdf[~gdf[VALID_ON].isna()][VALID_ON].drop_duplicates()
            row["valid_on_type"] = gdf[VALID_ON].dtype
            for index, value in enumerate(gdf_valid_on):
                row["valid_on_count"] += 1
                if index == 0:
                    row["valid_on"] = value
                else:
                    row[f"valid_on_{index}"] = value
        except KeyError:
            pass
        if VALID_TO in gdf.columns:
            row["valid_to_exists"] = 1
            row["valid_to_type"] = gdf[VALID_TO].dtype
            if gdf[VALID_TO].isna().all():
                row["valid_to_empty"] = 1
        check_results.append(row)
    return check_results
