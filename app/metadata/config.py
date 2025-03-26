from os import getenv
from urllib.parse import quote

ISO3 = "Location"
LVL = "Administrative level"
KEY = "Metadata type"
VALUE = "Metadata"

metadata_workbook = getenv("COD_META_WORKBOOK")
metadata_sheet = quote(getenv("COD_META_SHEET", ""))
metadata_url = f"https://docs.google.com/spreadsheets/d/{metadata_workbook}/gviz/tq?tqx=out:csv&sheet={metadata_sheet}"

na_values = ["#REF!"]

meta_long_columns = [ISO3, LVL, KEY, VALUE]

ignored_columns = [
    "header",
    "live_featureserver",
    "live_mapserver",
    "live_lines_featureserver",
    "live_lines_mapserver",
]

rename_columns = {
    "boundaries_established": "date_established",
    "cod_ab_quality_level": "cod_ab_quality_checked",
    "cod_ab_review_conclusion": "cod_ab_requires_improvement",
    "cod_ab_review_date": "date_reviewed",
    "cod_em": "cod_em_available",
    "cod_ps_compatibility": "cod_ps_match",
    "cod_ps": "cod_ps_available",
    "deepest_complete": "level_complete",
    "deepest_level": "level_deepest",
    "ideal_depth": "level_ideal",
    "note": "notes",
    "ocha_country_status": "ocha_operational_country",
}
integer_columns = ["level_ideal", "level_complete", "feature_count", "level_deepest"]

invisible_chars = [
    "U+0009",
    "U+000A",
    "U+000D",
    "U+00A0",
    "U+200C",
    "U+200E",
    "U+200F",
    "U+FEFF",
]

apostrophe_chars = ["U+0060", "U+2019", "U+2032"]

quote_chars = ["U+201C", "U+201D"]
