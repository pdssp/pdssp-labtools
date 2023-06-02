from pathlib import Path

from definitions import Definitions
import loader
from builder import build_catalog
from ias import psup
from labtools.schemas import factory as metadata_factory

if __name__ == '__main__':  # sys.argv
    print("PDSSP Labtools")
    print('---')

    SOURCE_DATA_DIR = '/Users/nmanaud/workspace/pdssp/data/ias/source'
    YAML_DEFINITIONS_FILE = '/Users/nmanaud/workspace/pdssp/pdssp-labtools/data/definitions/ias/catalog.yaml'
    STAC_DATA_DIR = '/Users/nmanaud/workspace/pdssp/data/ias/stac'

    N_MAX_ITEMS = 100  # maximum number of items to process per collection

    print(f'SOURCE_DATA_DIR       = {SOURCE_DATA_DIR}')
    print(f'YAML_DEFINITIONS_FILE = {YAML_DEFINITIONS_FILE}')
    print(f'STAC_DATA_DIR         = {STAC_DATA_DIR}')
    print()
    loader.load_schemas([
        'labtools.schemas.pdssp_stac',
    ])
    loader.load_schemas([
        'labtools.ias.schemas.omega_c_proj',
        'labtools.ias.schemas.omega_cube',
        'labtools.ias.schemas.omega_map',
        'labtools.ias.schemas.vector_features'
    ])
    print(f'Loaded schemas: {metadata_factory.get_schema_names()}')
    print()

    # load definitions (note: acting as an element of a local data catalog service)
    definitions = Definitions(yaml_file=YAML_DEFINITIONS_FILE)

    # set defined collections to be processed (filtering for dev tests)
    # collections_ids = definitions.get_collections_ids()
    collections_ids = ['mex_omega_c_proj_ddr', 'mex_omega_cubes_rdr', 'features_datasets', 'mex_omega_global_maps_ddr']
    # collections_ids = ['mex_omega_c_proj_ddr']
    # collections_ids = ['mex_omega_cubes_rdr']
    # collections_ids = ['features_datasets']
    # collections_ids = ['mex_omega_global_maps_ddr']

    source_collections_files = []
    print('--- select collections to process')
    for collection_id in collections_ids:
        urn_collection_id = f'urn:pdssp:ias:collection:{collection_id}'  # temporary patch
        collection_definition = definitions.get_collection(urn_collection_id)
        source_collection_file = Path(SOURCE_DATA_DIR) / collection_definition.get_source_collection_file()
        source_collections_files.append(source_collection_file)
        print(collection_definition.id, source_collection_file)
    print()

    # # download source collection and data files for each collection defined in input catalog definition
    print('--- download source collections and data files')
    print('Skipped.')
    print()
    # for collection_id in collections_ids:
    #     collection_definition = definitions.get_collection(collection_id)
    #     collection_id = collection_definition.id
    #     url = collection_definition.source.url
    #     metadata_schema = collection_definition.source.metadata_schema
    #     target = collection_definition.ssys_targets[0].lower()
    #     source_collections_dir = Path(SOURCE_DATA_DIR) / collection_definition.path / collection_id
    #
    #     print(f'Download `{collection_id}` collection from `{url}` to `{source_collections_dir}`.')
    #     source_collection_file = psup.download_collection(collection_id, url, metadata_schema, output_dir=source_collections_dir, overwrite=False)
    #     if source_collection_file:
    #         psup.download_data_files(source_collection_file, overwrite=True)
    #     print(source_collection_file)
    #     print()

    print('--- build catalog')
    # test build catalog
    build_catalog(definitions, source_collections_files, stac_dir=STAC_DATA_DIR, n_max_items=N_MAX_ITEMS)
    # print('Skipped.')
    # print()

