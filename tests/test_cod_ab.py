from os.path import join
from pathlib import Path

from hdx.utilities.dateparse import parse_date
from hdx.utilities.path import temp_dir

from hdx.scraper.cod_ab import checks, download, formats, metadata, scores
from hdx.scraper.cod_ab.cod_ab import generate_dataset
from hdx.scraper.cod_ab.utils import (
    get_arcgis_update,
    get_hdx_update,
    get_iso3_list,
)


class TestCODAB:
    def test_cod_ab(
        self,
        configuration,
        read_dataset,
        fixtures_dir,
        input_dir,
        config_dir,
    ):
        with temp_dir(
            "Test_cod_ab",
            delete_on_success=True,
            delete_on_failure=False,
        ) as tempdir:
            data_dir = Path(tempdir)

            iso3_list = get_iso3_list()
            assert iso3_list == []

            iso3 = "CAF"
            arcgis_update = get_arcgis_update(iso3)
            assert arcgis_update == ""

            hdx_update = get_hdx_update(iso3)
            assert hdx_update == ""

            meta_dict = metadata.main(iso3, data_dir)
            assert meta_dict == {}

            # TODO: add some assertions here
            download.main(iso3, data_dir)
            formats.main(iso3, data_dir)
            checks.main(iso3, data_dir)
            score = scores.main(iso3, data_dir)
            assert score == 1.0

            dataset = generate_dataset(
                meta_dict, iso3, data_dir, parse_date("2025-01-01")
            )
            dataset.update_from_yaml(
                path=join(config_dir, "hdx_dataset_static.yaml"),
            )
            assert dataset == {
                "name": "cod-ab-caf",
                "title": "Central African Republic - Subnational Administrative Boundaries",
                "dataset_date": "[2020-12-01T00:00:00 TO 2024-03-01T23:59:59]",
                "tags": [
                    {
                        "name": "administrative boundaries-divisions",
                        "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                    },
                    {
                        "name": "gazetteer",
                        "vocabulary_id": "b891512e-9516-4bf5-962a-7a289772a2a1",
                    },
                ],
                "groups": [{"name": "caf"}],
                "owner_org": "eabb59ef-4082-4c7a-9c08-0f57eed970d8",
                "dataset_source": "Agency for Technical Cooperation and Development(ACTED)",
                "caveats": "",
                "notes": "Central African Republic administrative level 0-4 boundaries (COD-AB) dataset.  \n  \nThese administrative boundaries were established in 2020.  \n  \nThis COD-AB was most recently reviewed for accuracy and necessary changes in March 2024. The COD-AB does not require any updates.  \n  \nSourced from Agency for Technical Cooperation and Development(ACTED).  \n  \nThis COD-AB is suitable for database or GIS linkage to the Central African Republic population statistics ([COD-PS](https://data.humdata.org/dataset/cod-ps-caf) dataset.  \n  \nAn edge-matched (COD-EM) version of this COD-AB is available on HDX [here](https://data.humdata.org/dataset/cod-em-caf).  \n  \nAdministrative level 1 contains 17 feature(s). The normal administrative level 1 feature type is 'Prefecture'.  \n  \nAdministrative level 2 contains 72 feature(s). The normal administrative level 2 feature type is 'Sub-prefecture'.  \n  \nAdministrative level 3 contains 175 feature(s). The normal administrative level 3 feature type is 'Commune'.  \n  \nAdministrative level 4 contains 202 feature(s). The normal administrative level 4 feature type is 'Locality'.  \n  \nThis metadata was last updated on May 30, 2025.",
                "cod_level": "cod-enhanced",
                "dataset_preview": "resource_id",
                "license_id": "cc-by-igo",
                "methodology": "Other",
                "methodology_other": "Prepared by UN-OCHA",
                "package_creator": "HDX Data Systems Team",
                "private": False,
                "maintainer": "maxmalynowsky",
                "data_update_frequency": 365,
                "subnational": "1",
            }

            resources = dataset.get_resources()
            assert resources == [
                {
                    "name": "caf_cod_ab.xlsx",
                    "description": "Central African Republic administrative level 0-4 gazetteer",
                    "format": "xlsx",
                    "resource_type": "file.upload",
                    "url_type": "upload",
                },
                {
                    "name": "caf_cod_ab.shp.zip",
                    "description": "Central African Republic administrative level 0-4 zipped shapefile",
                    "format": "shp",
                    "resource_type": "file.upload",
                    "url_type": "upload",
                },
                {
                    "name": "caf_cod_ab.geojson.zip",
                    "description": "Central African Republic administrative level 0-4 GeoJSON",
                    "format": "geojson",
                    "resource_type": "file.upload",
                    "url_type": "upload",
                },
                {
                    "name": "caf_cod_ab.gdb.zip",
                    "description": "Central African Republic administrative level 0-4 Geodatabase",
                    "format": "geodatabase",
                    "resource_type": "file.upload",
                    "url_type": "upload",
                },
            ]
