from pathlib import Path

from geopandas import read_parquet
from shapely import make_valid
from shapely.ops import polylabel


def to_points(file_path: Path) -> None:
    """Uses OGR2OGR to turn a GeoPackage into GeoParquet.

    Args:
        file_path: Name of the downloaded layer.
    """
    src_dataset = file_path.with_suffix(".parquet")
    dst_dataset = src_dataset.with_stem(file_path.stem + "points")
    gdf = read_parquet(src_dataset)
    gdf.geometry = gdf.geometry.apply(
        lambda x: max(x.geoms, key=lambda a: a.area)
        if x.geom_type == "MultiPolygon"
        else x,
    )
    gdf.geometry = gdf.geometry.apply(
        lambda x: polylabel(make_valid(x), tolerance=1e-6),
    )
    gdf.to_parquet(
        dst_dataset,
        compression="zstd",
        geometry_encoding="geoarrow",
        write_covering_bbox=True,
    )
