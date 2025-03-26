from re import match

from geopandas import GeoDataFrame

from app.config import misc_columns
from app.utils import get_name_columns, get_pcode_columns


def main(iso3: str, gdfs: list[GeoDataFrame]) -> list[dict]:
    """Check completeness of an admin boundary by checking the columns.

    Args:
        iso3: ISO3 code of the current location being checked.
        gdfs: List of GeoDataFrames, with the item at index 0 corresponding to admin
        level 0, index 1 to admin level 1, etc.

    Returns:
        List of check rows to be outputed as a CSV.
    """
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        name_columns = get_name_columns(gdf, admin_level)
        pcode_columns = get_pcode_columns(gdf, admin_level)
        ref_name_columns = [
            x for x in gdf.columns if match(rf"^adm{admin_level}_ref", x)
        ]
        valid_columns = name_columns + pcode_columns + misc_columns + ref_name_columns
        other_columns = [x for x in gdf.columns if x not in valid_columns]
        row = {
            "iso3": iso3,
            "level": admin_level,
            "ref_name_column_count": len(ref_name_columns),
            "ref_name_columns": ",".join(ref_name_columns),
            "other_column_count": len(other_columns),
            "other_columns": ",".join(other_columns),
        }
        check_results.append(row)
    return check_results
