import re
from logging import getLogger
from pathlib import Path
from subprocess import DEVNULL, CompletedProcess, run
from urllib.parse import urlencode

from tenacity import retry, stop_after_attempt, wait_fixed

from hdx.scraper.cod_ab.config import ATTEMPT, WAIT
from hdx.scraper.cod_ab.utils import generate_token

logger = getLogger(__name__)

POINT = 1
LINE = 2
POLYGON = 3


def ogr2ogr(url: str, file_path: Path, records: int | None) -> CompletedProcess[bytes]:
    """Uses OGR2OGR to download ESRI JSON from an ArcGIS server to local FlatGeobuf.

    The query parameter "f" (format) is set to return JSON (default is HTML), "where" is
    a required parameter with the value "1=1" to return all features, "outFields" is set
    to "*" specifying to return all fields (default is only first field),
    "orderByFields" is required for pagination to ensure that features are always
    ordered the same way and duplicates are not returned when paginating, and finally
    "resultRecordCount" is used to specify how many records to paginate through each
    time.

    OGR2OGR is set to overwrite the existing file if it exists (default is to throw an
    error). "-nln" sets the name of the layer to be the same as the filename (default is
    the name of the source layer, in this case "ESRIJSON"). The output option ("-oo")
    "FEATURE_SERVER_PAGING" is set to "YES" instructing the command to paginate through
    the server and not stop with the first query result.

    Args:
        url: Base URL of an ArcGIS Feature Service.
        file_path: Name of the downloaded layer.
        records: The number of records to fetch from the server per request during
        pagination.

    Returns:
        A subprocess completed process, including a returncode stating whether the run
        was successfun or not.
    """
    query: dict = {
        "f": "json",
        "where": "1=1",
        "outFields": "*",
        "orderByFields": "objectid",
        "token": generate_token(),
    }
    if records is not None:
        query["resultRecordCount"] = records
    dst_dataset = file_path.with_suffix(".fgb")
    src_dataset = f"{url}/query?{urlencode(query)}"
    return run(
        [
            "ogr2ogr",
            "-overwrite",
            *["-nln", file_path.stem],
            *["-oo", "FEATURE_SERVER_PAGING=YES"],
            *[dst_dataset, src_dataset],
        ],
        stderr=DEVNULL,
        check=False,
    )


def is_correct_geom_type(file_path: Path, geom_type: int) -> bool:
    """Uses OGR to check whether a downloaded file is a valid geometry type.

    During the download process, the ArcGIS server may return empty geometry. This check
    ensures data has been downloaded correctly.

    Args:
        file_path: Path of a OGR readable file.
        geom_type: geometry type as integer.

    Returns:
        True if the file is detected as a valid polygon, otherwise false.
    """
    if geom_type == POINT:
        regex = re.compile(r"\((Multi Point|Point)\)")
    elif geom_type == LINE:
        regex = re.compile(r"\((Multi Line String|Line String)\)")
    elif geom_type == POLYGON:
        regex = re.compile(r"\((Multi Polygon|Polygon)\)")
    result = run(
        ["ogrinfo", file_path.with_suffix(".fgb")],
        capture_output=True,
        check=False,
    )
    return bool(regex.search(result.stdout.decode("utf-8")))


@retry(stop=stop_after_attempt(ATTEMPT), wait=wait_fixed(WAIT))
def main(file_path: Path, url: str, geom_type: int) -> None:
    """Downloads ESRI JSON from an ArcGIS Feature Server and saves as GeoParquet.

    First, attempts to download ESRI JSON paginating through the layer with the value
    set by "maxRecordCount" (default behavior when "resultRecordCount" is unspecified).
    This request may fail due to memory issues on the server.

    Then, starting with "1000" and reducing by factors of "10", try to paginate through
    the layer. "1000" is a value that will succeed for most layers, however layers with
    excessively large geometries will require smaller sets of records to avoid
    overloading the server's memory. When all records have been obtained through
    pagination, save the result.

    If at the end of this loop, the function is unable to download a layer, it is likely
    that a network error has occured. The RuntimeError will trigger tenacity to retry
    the function again from the start.

    Args:
        file_path: name to use for saved layer.
        url: Base URL of an ArcGIS Feature Service.
        geom_type: geometry type as integer.

    Raises:
        RuntimeError: Raises an error with the filename of a layer unable to be
        downloaded.
    """
    for records in [None, 1000, 100, 10, 1]:
        result = ogr2ogr(url, file_path, records)
        if result.returncode == 0:
            break
    if not is_correct_geom_type(file_path, geom_type):
        raise RuntimeError(file_path)
