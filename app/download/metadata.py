import re

from app.config import services_url
from app.utils import client_get, generate_token

p2 = re.compile(r"[a-z]{3}_admin\d$")
p3 = re.compile(r"[a-z]{3}_adminlines$")


def polygons(iso3: str) -> list[int]:
    """Get the layer index from the ArcGIS server."""
    params = {"f": "json", "token": generate_token()}
    service_name = f"{iso3}_COD"
    layers_url = f"{services_url}/{service_name}/FeatureServer"
    layers = client_get(layers_url, params=params).json()["layers"]
    return [x["id"] for x in layers if p2.search(x["name"])]


def lines(iso3: str) -> int:
    """Get the layer index from the ArcGIS server."""
    params = {"f": "json", "token": generate_token()}
    service_name = f"{iso3}_COD"
    layers_url = f"{services_url}/{service_name}/FeatureServer"
    layers = client_get(layers_url, params=params).json()["layers"]
    return next(x["id"] for x in layers if p3.search(x["name"]))
