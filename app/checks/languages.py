from geopandas import GeoDataFrame
from langcodes import tag_is_valid

from app.config import LANGUAGE_COUNT


def main(iso3: str, gdfs: list[GeoDataFrame]) -> list[dict]:
    """Checks for which languages are used within dataset.

    Datasets use the following pattern in their field names for identifying languages:
    "ADM{LEVEL}_{LANGUAGE_CODE}". For example, a dataset containing English, French,
    and Haitian Creole for admin level 1 would have the following field names:
    ADM1_EN, ADM1_FR, ADM1_HT. Regex is used to identify field names, this may pick up
    columns such as identification fields if they are named like ADM1_ID. However, this
    would be a valid column if it was used for Indonesian names.

    The following are a list of source and output columns:
    - source: "ADM{LEVEL}_{LANGUAGE_CODE}"
        - output: "language_count", "language_1", "language_2", "language_3", etc...

    Args:
        iso3: ISO3 code of the current location being checked.
        gdfs: List of GeoDataFrames, with the item at index 0 corresponding to admin
        level 0, index 1 to admin level 1, etc.

    Returns:
        List of results to output as a CSV.
    """
    check_results = []
    language_parent = None
    for admin_level, gdf in enumerate(gdfs):
        row = {
            "iso3": iso3,
            "level": admin_level,
            "language_count": 0,
            "language_mix": 0,
            "language_parent": language_parent,
            "language_invalid": 0,
        }
        for index in range(LANGUAGE_COUNT):
            lang_col = f"lang{index}" if index > 0 else "lang"
            lang_codes = gdf[~gdf[lang_col].isna()][lang_col].drop_duplicates()
            if len(lang_codes) > 1:
                row["language_mix"] += 1
            for lang_code in lang_codes:
                if tag_is_valid(lang_code):
                    row["language_count"] += 1
                else:
                    row["language_invalid"] += 1
                row[f"language_{index}"] = lang_code
        language_parent = row["language_count"]
        check_results.append(row)
    return check_results
