from pandas import DataFrame

from hdx.scraper.cod_ab.config import romanized_languages


def main(checks: DataFrame) -> DataFrame:
    """Function for scoring languages used within dataset.

    Gives a perfect score if at least 1 language column is detected and all language
    codes are valid.

    Args:
        checks: checks DataFrame.

    Returns:
        Checks DataFrame with additional columns for scoring.
    """
    scores = checks[["iso3", "level"]].copy()
    scores["languages"] = (
        checks["language_count"].ge(1)
        & checks["language_invalid"].eq(0)
        & checks["language_0"].isin(romanized_languages)
        & (
            checks["language_parent"].isna()
            | checks["language_count"].le(checks["language_parent"])
        )
    )
    return scores
