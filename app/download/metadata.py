import re

from app.config import services_url
from app.utils import client_get, generate_token

p1 = re.compile(r"[A-Z]{3}_COD$")
p2 = re.compile(r"[a-z]{3}_admin\d$")
p3 = re.compile(r"[a-z]{3}_adminlines$")


def polygons() -> dict["str", list[int]]:
    """Get the layer index from the ArcGIS server.

    Returns:
        dict: example: { "BFA": [2, 3, 4], "HND": [3, 4, 5] }
    """
    params = {"f": "json", "token": generate_token()}
    services = client_get(services_url, params=params).json()["services"]
    service_names = [x["name"].split("/")[1] for x in services if p1.search(x["name"])]
    layer_index = {}
    for service_name in service_names:
        iso3 = service_name[:3].upper()
        layers_url = f"{services_url}/{service_name}/FeatureServer"
        layers = client_get(layers_url, params=params).json()["layers"]
        polygon_ids = [x["id"] for x in layers if p2.search(x["name"])]
        layer_index[iso3] = polygon_ids
    return layer_index


def lines() -> dict["str", list[int]]:
    """Get the layer index from the ArcGIS server.

    Returns:
        dict: example: { "BFA": 1, "HND": 2 }
    """
    params = {"f": "json", "token": generate_token()}
    services = client_get(services_url, params=params).json()["services"]
    service_names = [x["name"].split("/")[1] for x in services if p1.search(x["name"])]
    layer_index = {}
    for service_name in service_names:
        iso3 = service_name[:3].upper()
        layers_url = f"{services_url}/{service_name}/FeatureServer"
        layers = client_get(layers_url, params=params).json()["layers"]
        line_id = [x["id"] for x in layers if p3.search(x["name"])]
        layer_index[iso3] = line_id[0]
    return layer_index
