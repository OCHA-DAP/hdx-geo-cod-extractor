from app.config import lines_dir, polygons_dir, services_url

from . import metadata, ogr2ogr


def main(iso3: str) -> None:
    """Entrypoint for the module."""
    indexes = metadata.polygons(iso3)
    for lvl, index in enumerate(indexes):
        url = f"{services_url}/{iso3.lower()}_COD/FeatureServer/{index}"
        file_path = polygons_dir / f"{iso3}_adm{lvl}".lower()
        ogr2ogr.main(file_path, url, 3)
    index = metadata.lines(iso3)
    url = f"{services_url}/{iso3}_COD/FeatureServer/{index}"
    file_path = lines_dir / f"{iso3}".lower()
    ogr2ogr.main(file_path, url, 2)
