from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict, List, Union, Optional

from definitions import Definitions, CatalogDefinition
from ias import psup as psup
import loader

from labtools.schemas import factory as metadata_factory
from labtools.transformers import factory as transformer_factory

def download_data():
    pass

def build_index():
    pass


import pystac


def create_stac_catalog(catalog_definition: CatalogDefinition) -> pystac.Catalog:
    return pystac.Catalog(
        id=catalog_definition.id,
        title=catalog_definition.title,
        description=catalog_definition.description,
        stac_extensions=catalog_definition.extensions,
        extra_fields={'ssys:targets': catalog_definition.ssys_targets}
    )


def add_sub_catalogs(stac_catalog: pystac.Catalog, definitions: Definitions):

    # get expected sub-catalogs IDs for input STAC catalog ID
    catalog_definition = definitions.get_catalog(stac_catalog.id)
    sub_catalogs_ids = catalog_definition.catalogs

    # check whether or not all expected sub-catalogs have been added to the input STAC catalog
    sub_catalogs_added = False
    for sub_catalogs_id in sub_catalogs_ids:
        stac_sub_catalog = stac_catalog.get_child(sub_catalogs_id)  # if exists, it means that it has been added
        if not stac_sub_catalog:
            sub_catalog_definition = definitions.get_catalog(sub_catalogs_id)
            stac_sub_catalog = create_stac_catalog(sub_catalog_definition)
            stac_catalog.add_child(stac_sub_catalog)
            print(f'added {stac_sub_catalog.id!r} to {stac_catalog.id!r}.')
            return stac_sub_catalog, sub_catalogs_added
            # return add_sub_catalogs(stac_sub_catalog, definitions)

    # get parent STAC catalog of input STAC catalog
    parent_stac_catalog = stac_catalog.get_parent()

    stac_catalog = parent_stac_catalog
    if stac_catalog.id == definitions.get_root_catalog().id:
        sub_catalogs_added = True

    return stac_catalog, sub_catalogs_added


def create_root_catalog(definitions: Definitions) -> pystac.Catalog:
    """Create STAC catalog skeleton given an input catalog definition."""

    # check input catalog definition
    # ...

    # get root catalog
    catalog_definition = definitions.get_root_catalog()
    stac_catalog = create_stac_catalog(catalog_definition)
    sub_catalogs_added = False
    while not sub_catalogs_added: # sub-catalogs not added (stac_catalog.add_children())
        # print(stac_catalog)
        stac_catalog, sub_catalogs_added = add_sub_catalogs(stac_catalog, definitions)
        # moving out of the loop when sub_catalogs_added is True; the stac_catalog object
        # is expected to be the root STAC catalog.

    return stac_catalog


import shutil


def build_catalog(definitions, source_collections_files, stac_dir):

    stac_dir = Path(stac_dir)
    if stac_dir.exists():
        shutil.rmtree(stac_dir)

    # create destination skeleton STAC catalog from catalog definitions
    stac_catalog = create_root_catalog(definitions)

    for source_collection_file in source_collections_files:
        # create STAC collection corresponding to input collection ID and add to STAC catalog
        source_collection_metadata = psup.read_collection_metadata(source_collection_file)
        collection_id = source_collection_metadata.id
        print(f'create and add STAC collection {collection_id}.')
        transformer = transformer_factory.create_transformer(source_collection_metadata.schema_name)
        collection_definition = definitions.get_collection(collection_id)
        stac_collection = transformer.create_stac_collection(source_collection_metadata, definition=collection_definition)

        products = psup.read_products_metadata(source_collection_file)
        for product_metadata in products:
            item_definition = None  # definitions.get_item(item_id)
            stac_item = transformer.create_stac_item(product_metadata, definition=item_definition, collection_id=collection_id)
            stac_collection.add_item(stac_item)

        # update collection extent from items
        stac_collection.update_extent_from_items()

        # add collection to the output STAC catalog
        stac_catalog.add_child(stac_collection)

    # save STAC catalog
    print()
    Path.mkdir(stac_dir, parents=True, exist_ok=True)
    stac_catalog.describe()
    stac_catalog.normalize_hrefs(str(stac_dir))
    stac_catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)


# class SourceCollection(BaseModel):
#     id: str
#     url: str
#     path: str
#     metadata_schema: str

if __name__ == '__main__':  # sys.argv
    print("PDSSP Labtools")
    print()
    SOURCE_DATA_DIR = '/Users/nmanaud/workspace/pdssp/data/ias/source'
    YAML_DEFINITIONS_FILE = '/Users/nmanaud/workspace/pdssp/pdssp-labtools/data/definitions/ias/catalog.yaml'
    STAC_DATA_DIR = '/Users/nmanaud/workspace/pdssp/data/ias/stac'

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

    # load definitions (note: acting as an element of a local data catalog service)
    definitions = Definitions(yaml_file=YAML_DEFINITIONS_FILE)

    print(definitions.catalog_tree())

    # set defined collections to be processed (filtering for dev tests)
    # collections_ids = definitions.get_collections_ids()
    collections_ids = [ 'mex_omega_c_proj_ddr' ]
    source_collections_files = []
    for collection_id in collections_ids:
        collection_definition = definitions.get_collection(collection_id)
        print(collection_definition.id)
        source_collection_file = Path(SOURCE_DATA_DIR) / collection_definition.get_source_collection_file()
        source_collections_files.append(source_collection_file)

    # # download source collection and data files for each collection defined in input catalog definition
    # collections = definitions.get_collections()
    # for collection in collections:
    #     collection_id = collection.id
    #     url = collection.source.url
    #     metadata_schema = collection.source.metadata_schema
    #     target = collection.ssys_targets[0].lower()
    #     source_collections_dir = Path(SOURCE_DATA_DIR) / collection.path / collection_id
    #
    #     print(f'Download `{collection_id}` collection from `{url}` to `{source_collections_dir}`.')
    #     source_collection_file = psup.download_collection(collection_id, url, metadata_schema, output_dir=source_collections_dir, overwrite=False)
    #     if source_collection_file:
    #         psup.download_data_files(source_collection_file)
    #     print(source_collection_file)
    #     print()

    print('--- build catalog')
    # test build catalog
    build_catalog(definitions, source_collections_files, stac_dir=STAC_DATA_DIR)


