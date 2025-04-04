from pandas import DataFrame, ExcelWriter, Timestamp
from xlsxwriter import Workbook
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

from app.config import table_dir
from app.utils import read_csv


def format_between(
    cell_format: Format,
    min_val: float,
    max_val: float,
) -> dict[str, str | float | Format]:
    """Returns a configuration used for conditional formatting between values in Excel.

    Args:
        cell_format: What formatting to apply when the two conditions below are true.
        min_val: Minimum value for conditional formatting to apply to.
        max_val: Maximum value for conditional formatting to apply to.

    Returns:
        Configuration for Excel conditional formatting.
    """
    return {
        "type": "cell",
        "criteria": "between",
        "minimum": min_val,
        "maximum": max_val,
        "format": cell_format,
    }


def format_equals(
    cell_format: Format,
    value: str | float,
) -> dict[str, str | float | Format]:
    """Returns a configuration used for conditional formatting equal to value in Excel.

    Args:
        cell_format: What formatting to apply when the condition below are true.
        value: Value for conditional formatting to apply to.

    Returns:
        Configuration for Excel conditional formatting.
    """
    return {
        "type": "cell",
        "criteria": "equal to",
        "value": value,
        "format": cell_format,
    }


def style(
    last_row: int,
    last_col: int,
    workbook: Workbook,
    worksheet: Worksheet,
) -> None:
    """Apply red / orange / yellow styling to excel values falling between value ranges.

    The first few columns of the output include location names and iso3 codes.
    - status_col: zero-index location of the COD status (Enhanced / Standard)
    - first_col: zero-index location where decimal data begins.

    - Decimals are formatted as percentages.
    - Red formatting is applied for values: 0-33%
    - Orange formatting is applied for values: 33-67%
    - Yellow formatting is applied for values: 67-100%

    Args:
        last_row: Index of last row in Excel (0-indexed).
        last_col: Index of last column in Excel (0-indexed).
        workbook: Excel workbook instance.
        worksheet: Excel worksheet instance.
    """
    first_row = 1
    status_col = 2
    first_col = 3
    format_percent = workbook.add_format({"num_format": "0%"})
    format_rd = workbook.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
    format_or = workbook.add_format({"bg_color": "#FFCC99", "font_color": "#3F3F76"})
    format_yl = workbook.add_format({"bg_color": "#FFEB9C", "font_color": "#9C6500"})
    between_rd = format_between(format_rd, 0, 0.333)
    between_or = format_between(format_or, 0.333, 0.667)
    between_yl = format_between(format_yl, 0.667, 0.999)
    equal_rd = format_equals(format_rd, '"Not Available"')
    equal_or = format_equals(format_or, '"Standard"')
    worksheet.set_column(first_col, last_col, None, format_percent)
    worksheet.conditional_format(first_row, first_col, last_row, last_col, between_rd)
    worksheet.conditional_format(first_row, first_col, last_row, last_col, between_or)
    worksheet.conditional_format(first_row, first_col, last_row, last_col, between_yl)
    worksheet.conditional_format(first_row, status_col, last_row, status_col, equal_rd)
    worksheet.conditional_format(first_row, status_col, last_row, status_col, equal_or)
    worksheet.autofit()


def aggregate(checks: DataFrame) -> DataFrame:
    """Summarize scores by averaging scores from each admin level.

    Args:
        checks: Resulting DataFrame created by scoring functions.

    Returns:
        Dataframe grouped and averaged by ISO3.
    """
    checks = checks.drop(columns=["level"])
    checks = checks.groupby("iso3").mean()
    checks["score"] = checks.mean(axis=1)
    checks = checks.round(3)
    return checks.sort_values(by=["score", "iso3"])


def main(checks: DataFrame) -> None:
    """Aggregates scores and outputs to an Excel workbook with red/amber/green coloring.

    1. Groups and averages the scores generated in this module and outputs as a CSV.

    2. Applied styling to the dataset generated in step 1 and saves as Excel.

    3. Adds all CSVs generated in previous modules to the Excel workbook.

    4. Adds a final sheet specifying which date the workbook was generated on.

    Args:
        metadata: metadata DataFrame.
        checks: checks DataFrame.
    """
    scores = aggregate(checks)
    scores.to_csv(table_dir / "scores.csv", encoding="utf-8-sig")
    scores = scores.fillna(0).sort_values(by=["score", "iso3"])
    with ExcelWriter(table_dir / "cod_ab_data_quality.xlsx") as writer:
        scores.to_excel(writer, sheet_name="cod_ab_data_quality", index=False)
        if isinstance(writer.book, Workbook):
            style(
                len(scores.index),
                len(scores.columns) - 1,
                writer.book,
                writer.sheets["cod_ab_data_quality"],
            )
        for sheet in ["scores", "checks"]:
            df1 = read_csv(table_dir / f"{sheet}.csv", datetime_to_date=True)
            df1.to_excel(writer, sheet_name=sheet, index=False)
            writer.sheets[sheet].autofit()
        df_date = DataFrame([{"date": Timestamp.now().date()}])
        df_date.to_csv(table_dir / "date.csv", index=False)
        df_date.to_excel(writer, sheet_name="date", index=False)
        writer.sheets["date"].autofit()
