from geopandas import GeoDataFrame

from .table_names_utils import (
    get_invalid_chars,
    get_languages,
    has_double_spaces,
    has_numbers,
    has_strippable_spaces,
    is_invalid,
    is_invalid_adm0,
    is_lower,
    is_punctuation,
    is_upper,
)
from hdx.scraper.cod_ab.utils import is_empty


def main(iso3: str, gdfs: list[GeoDataFrame]) -> list[dict]:
    """Check completeness of an admin boundary by checking the columns."""
    check_results = []
    for admin_level, gdf in enumerate(gdfs):
        langs = get_languages(gdf)
        name_columns_all = [
            column
            for column in gdf.columns
            for level in range(admin_level + 1)
            if column.startswith(f"adm{level}_name")
        ]
        name_columns = [
            column
            for column in gdf.columns
            for level in range(admin_level + 1)
            if column == f"adm{level}_name"
            or (column.startswith(f"adm{level}_name") and column[-1] < str(len(langs)))
        ]
        name_columns_adm0 = [
            column
            for column in name_columns
            if column == "adm0_name"
            or (column.startswith("adm0_name") and column[-1] < str(len(langs)))
        ]
        names = gdf[name_columns]
        invalid_chars_set = set()
        name_no_valid = []
        name_invalid = []
        name_invalid_adm0 = []
        for index, lang in enumerate(langs):
            name_column = f"_name{index}" if index > 0 else "_name"
            name_columns_lang = [
                column for column in name_columns if column.endswith(name_column)
            ]
            name_columns_lang_adm0 = [
                column for column in name_columns_adm0 if column.endswith(name_column)
            ]
            invalid_chars_set.update(
                {
                    names[col]
                    .map(lambda x, lang=lang: get_invalid_chars(lang, x, iso3))
                    .sum()
                    for col in name_columns_lang
                },
            )
            name_no_valid.extend(
                [
                    names[col]
                    .map(lambda x, lang=lang: is_punctuation(lang, x, iso3))
                    .sum()
                    for col in name_columns_lang
                ],
            )
            name_invalid.extend(
                [
                    names[col].map(lambda x, lang=lang: is_invalid(lang, x, iso3)).sum()
                    for col in name_columns_lang
                ],
            )
            name_invalid_adm0.extend(
                [
                    names[col]
                    .map(lambda x, lang=lang: is_invalid_adm0(lang, x, iso3))
                    .any()
                    for col in name_columns_lang_adm0
                ],
            )
        invalid_chars = "".join(invalid_chars_set)
        row = {
            "iso3": iso3,
            "level": admin_level,
            "name_column_levels": sum(
                [
                    any(
                        bool(column.startswith(f"adm{level}_name"))
                        for column in gdf.columns
                    )
                    for level in range(admin_level + 1)
                ],
            ),
            "name_column_count": len(name_columns_all),
            "name_cell_count": max(names.size, 1),
            "name_empty": (names.isna() | names.map(is_empty)).sum().sum(),
            "name_empty_column": (names.isna() | names.map(is_empty)).all().sum(),
            "name_duplicated": names.duplicated().sum().sum(),
            "name_spaces_strip": sum(
                [names[col].map(has_strippable_spaces).sum() for col in name_columns],
            ),
            "name_spaces_double": sum(
                [names[col].map(has_double_spaces).sum() for col in name_columns],
            ),
            "name_upper": sum(
                [names[col].map(is_upper).sum() for col in name_columns],
            ),
            "name_upper_column": sum(
                [names[col].map(is_upper).all() for col in name_columns],
            ),
            "name_lower": sum(
                [names[col].map(is_lower).sum() for col in name_columns],
            ),
            "name_lower_column": sum(
                [names[col].map(is_lower).all() for col in name_columns],
            ),
            "name_numbers": sum(
                [names[col].map(has_numbers).sum() for col in name_columns],
            ),
            "name_numbers_column": sum(
                [names[col].map(has_numbers).all() for col in name_columns],
            ),
            "name_no_valid": sum(name_no_valid),
            "name_invalid": sum(name_invalid),
            "name_invalid_adm0": sum(name_invalid_adm0),
            "name_invalid_char_count": len({*list(invalid_chars)}),
            "name_invalid_chars": ",".join(
                sorted({f"U+{ord(x):04X}" for x in invalid_chars}),
            ),
        }
        check_results.append(row)
    return check_results
