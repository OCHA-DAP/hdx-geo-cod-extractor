import re
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from defusedxml.ElementTree import fromstring
from geopandas import GeoDataFrame
from httpx import Client, Response
from pandas import DataFrame, to_datetime
from tenacity import retry, stop_after_attempt, wait_fixed

from .config import (
    ARCGIS_PASSWORD,
    ARCGIS_SERVER,
    ARCGIS_USERNAME,
    ATTEMPT,
    TIMEOUT,
    WAIT,
    services_url,
)


@retry(stop=stop_after_attempt(ATTEMPT), wait=wait_fixed(WAIT))
def client_get(
    url: str,
    timeout: int = TIMEOUT,
    params: dict | None = None,
) -> Response:
    """HTTP GET with retries, waiting, and longer timeouts."""
    with Client(http2=True, timeout=timeout) as client:
        return client.get(url, params=params)


def read_csv(file_path: Path | str, *, datetime_to_date: bool = False) -> DataFrame:
    """Pandas read CSV with columns converted to the best possible dtypes.

    Args:
        file_path: CSV file path to read.
        datetime_to_date: Convert datetime to date, needed for export to Excel.

    Returns:
        Pandas DataFrame with converted dtypes.
    """
    df_csv = pd.read_csv(
        file_path,
        keep_default_na=False,
        na_values=["", "#N/A"],
    ).convert_dtypes()
    for col in df_csv.select_dtypes(include=["string"]):
        try:
            df_csv[col] = to_datetime(df_csv[col], format="ISO8601")
            if datetime_to_date:
                df_csv[col] = df_csv[col].dt.date
        except ValueError:
            pass
    return df_csv


def generate_token() -> str:
    """Generate a token for ArcGIS Server."""
    url = f"{ARCGIS_SERVER}/portal/sharing/rest/generateToken"
    data = {
        "username": ARCGIS_USERNAME,
        "password": ARCGIS_PASSWORD,
        "referer": f"{ARCGIS_SERVER}/portal",
        "f": "json",
    }
    with Client(http2=True) as client:
        r = client.post(url, data=data).json()
        return r["token"]


def get_iso3_list() -> list[str]:
    """Gets a list of ISO3 codes available on the FIS ArcGIS server."""
    params = {"f": "json", "token": generate_token()}
    services = client_get(services_url, params=params).json()["services"]
    p = re.compile(r"^Hosted\/cod_[a-z]{3}_ab_standardized$")
    return [
        x["name"][11:14].upper()
        for x in services
        if x["type"] == "FeatureServer" and p.search(x["name"])
    ]


def get_hdx_metadata(iso3: str) -> dict[str, Any]:
    """Get HDX metadata associated with a COD on HDX."""
    url = "https://data.humdata.org/api/3/action/package_show"
    params = {"id": f"cod-ab-{iso3.lower()}"}
    return client_get(url, TIMEOUT, params).json().get("result")


def get_hdx_update(iso3: str) -> str:
    """Get the date an HDX dataset was last updated."""
    return get_hdx_metadata(iso3)["last_modified"][:10]


def get_arcgis_update(iso3: str) -> str:
    """Get the date an ArcGIS Server service was last updated."""
    text = client_get(
        f"{services_url}/cod_{iso3.lower()}_ab_standardized/FeatureServer/info/metadata",
        TIMEOUT,
        {"token": generate_token()},
    ).text
    root = fromstring(text)
    date = root.findtext("Esri/CreaDate")
    if date:
        return f"{date[:4]}-{date[4:6]}-{date[6:8]}"
    return ""


def is_empty(string: str) -> bool:
    """Checks if string is empty."""
    return str(string).strip() == ""


def get_name_columns(gdf: GeoDataFrame, admin_level: int) -> list[str]:
    """Get all name columns for a GeoDataFrame of a specific admin level."""
    return [
        column
        for column in gdf.columns
        for level in range(admin_level + 1)
        if column.startswith(f"adm{level}_name")
    ]


def get_pcode_columns(gdf: GeoDataFrame, admin_level: int) -> list[str]:
    """Get all P-Code columns for a GeoDataFrame of a specific admin level."""
    return [
        column
        for column in gdf.columns
        for level in range(admin_level + 1)
        if column == f"adm{level}_pcode"
    ]


def get_epsg_ease(min_lat: float, max_lat: float) -> Literal[6931, 6932, 6933]:
    """Gets the code for appropriate Equal-Area Scalable Earth grid based on lat."""
    latitude_poles = 80
    latitude_equator = 0
    epsg_ease_north = 6931
    epsg_ease_south = 6932
    epsg_ease_global = 6933
    if max_lat >= latitude_poles and min_lat >= latitude_equator:
        return epsg_ease_north
    if min_lat <= -latitude_poles and max_lat <= latitude_equator:
        return epsg_ease_south
    return epsg_ease_global
