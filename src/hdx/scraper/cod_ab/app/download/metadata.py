import re

from app.config import services_url
from app.utils import client_get, generate_token

p1 = re.compile(r"[a-z]{3}_admin\d$")
p2 = re.compile(r"[a-z]{3}_adminlines$")
p3 = re.compile(r"[a-z]{3}_admincentroids$")


def polygons(iso3: str) -> list[int]:
    """Get the layer index from the ArcGIS server."""
    params = {"f": "json", "token": generate_token()}
    service_name = f"cod_{iso3.lower()}_ab_standardized"
    layers_url = f"{services_url}/{service_name}/FeatureServer"
    layers = client_get(layers_url, params=params).json()["layers"]
    return [
        x["id"] for x in sorted(layers, key=lambda x: x["name"]) if p1.search(x["name"])
    ]


def lines(iso3: str) -> list[int]:
    """Get the layer index from the ArcGIS server."""
    params = {"f": "json", "token": generate_token()}
    service_name = f"cod_{iso3.lower()}_ab_standardized"
    layers_url = f"{services_url}/{service_name}/FeatureServer"
    layers = client_get(layers_url, params=params).json()["layers"]
    return [
        x["id"] for x in sorted(layers, key=lambda x: x["name"]) if p2.search(x["name"])
    ]


def points(iso3: str) -> list[int]:
    """Get the layer index from the ArcGIS server."""
    params = {"f": "json", "token": generate_token()}
    service_name = f"cod_{iso3.lower()}_ab_standardized"
    layers_url = f"{services_url}/{service_name}/FeatureServer"
    layers = client_get(layers_url, params=params).json()["layers"]
    return [
        x["id"] for x in sorted(layers, key=lambda x: x["name"]) if p3.search(x["name"])
    ]
