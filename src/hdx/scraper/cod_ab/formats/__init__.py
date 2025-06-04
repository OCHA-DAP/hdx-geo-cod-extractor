from pathlib import Path
from shutil import rmtree

from osgeo import gdal


def to_multilayer(src_dataset: Path, dst_dataset: Path, *, multi: bool) -> None:
    """Uses OGR2OGR to turn a GeoParquet into a generic layer."""
    if dst_dataset.suffixes[0] == ".shp":
        lco = {"ENCODING": "UTF-8"}
    elif dst_dataset.suffix == ".gdb":
        lco = {"TARGET_ARCGIS_VERSION": "ARCGIS_PRO_3_2_OR_LATER"}
    else:
        lco = {}
    if multi:
        output_options = {"output_layer": src_dataset.stem}
    else:
        dst_dataset.mkdir(exist_ok=True, parents=True)
        dst_dataset = (dst_dataset / src_dataset.stem).with_suffix(dst_dataset.suffix)
        output_options = {}
    gdal.Run(
        "vector",
        "convert",
        input=src_dataset,
        output=dst_dataset,
        overwrite=True,
        creation_options=lco,
        **output_options,
    )


def main(iso3: str, data_dir: Path) -> None:
    """Convert geometries into multiple formats."""
    for ext, multi in [
        ("gdb", True),
        ("shp.zip", True),
        ("geojson", False),
        ("xlsx", True),
    ]:
        for level in [*range(6), "lines"]:
            src_dataset = (
                data_dir / iso3.lower() / f"{iso3.lower()}_admin{level}.parquet"
            )
            dst_dataset = data_dir / iso3.lower() / f"{iso3.lower()}_cod_ab.{ext}"
            if src_dataset.exists():
                to_multilayer(src_dataset, dst_dataset, multi=multi)
        if dst_dataset.is_dir():
            zip_file = dst_dataset.with_suffix(dst_dataset.suffix + ".zip")
            zip_file.unlink(missing_ok=True)
            gdal.Run(
                "vsi",
                "sozip",
                "create",
                "--recursive",
                "--no-paths",
                input=zip_file,
                output=dst_dataset,
            )
            rmtree(dst_dataset, ignore_errors=True)
