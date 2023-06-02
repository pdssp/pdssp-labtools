import json
from pystac.validation import validate_dict
from pystac.validation import validate_all
from pathlib import Path

if __name__ == '__main__':
    STAC_DATA_DIR = '/Users/nmanaud/workspace/pdssp/data/ias/stac/'

    item_json_files = [
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:mex_omega_c_proj_ddr/OMEGA_L3_0018_0_CPROJ/OMEGA_L3_0018_0_CPROJ.json'),
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:mex_omega_cubes_rdr/OMEGA_L2_0018_0/OMEGA_L2_0018_0.json'),
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:mex_omega_global_maps_ddr/albedo_r1080_equ_map/albedo_r1080_equ_map.json'),
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:features_datasets/hyd_global_290615/hyd_global_290615.json')
    ]

    collection_json_files = [
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:mex_omega_c_proj_ddr/collection.json'),
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:mex_omega_cubes_rdr/collection.json'),
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:mex_omega_global_maps_ddr/collection.json'),
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/urn:pdssp:ias:collection:features_datasets/collection.json')
    ]

    catalog_json_files = [
        Path(STAC_DATA_DIR + 'urn:pdssp:ias:body:mars/catalog.json'),
        Path(STAC_DATA_DIR + 'catalog.json')
    ]

    for item_json_file in item_json_files:
        if item_json_file.exists():
            print(f'Validating {item_json_file} ...')
            with open(item_json_file) as f:
                js = json.load(f)
            try:
                validate_dict(js)
            except Exception as e:
                print(e)
            print()

    for collection_json_file in collection_json_files:
        if collection_json_file.exists():
            print(f'Validating {collection_json_file} ...')
            with open(collection_json_file) as f:
                js = json.load(f)
            try:
                validate_dict(js)
            except Exception as e:
                print(e)
            print()

    for catalog_json_file in catalog_json_files:
        if catalog_json_file.exists():
            print(f'Validating {catalog_json_file} ...')
            with open(catalog_json_file) as f:
                js = json.load(f)
            try:
                validate_dict(js)
            except Exception as e:
                print(e)
            print()
