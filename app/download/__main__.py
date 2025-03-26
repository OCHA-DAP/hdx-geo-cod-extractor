from app.config import lines_dir, polygons_dir, services_url

from . import metadata, ogr2ogr


def main() -> None:
    """Entrypoint for the module."""
    polygons = metadata.polygons()
    for iso3, indexes in polygons.items():
        for lvl, index in enumerate(indexes):
            url = f"{services_url}/{iso3.lower()}_COD/FeatureServer/{index}"
            file_path = polygons_dir / f"{iso3}_adm{lvl}".lower()
            ogr2ogr.main(file_path, url, 3)
    lines = metadata.lines()
    for iso3, index in lines.items():
        url = f"{services_url}/{iso3}_COD/FeatureServer/{index}"
        file_path = lines_dir / f"{iso3}".lower()
        ogr2ogr.main(file_path, url, 2)


if __name__ == "__main__":
    main()
