"""STAC catalog builder"""
import pystac
import shutil
from pathlib import Path

from labtools.transformers import factory as transformer_factory
from labtools.definitions import Definitions, CatalogDefinition, get_urn_id
from labtools.ias import psup as psup

# from pydantic import BaseModel, Field
# from typing import Dict, List, Union, Optional


def create_stac_catalog(catalog_definition: CatalogDefinition) -> pystac.Catalog:
    return pystac.Catalog(
        id=catalog_definition.id,
        title=catalog_definition.title,
        description=catalog_definition.description,
        stac_extensions=catalog_definition.stac_extensions,
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


def build_catalog(definitions, source_collections_files, stac_dir):

    stac_dir = Path(stac_dir)
    if stac_dir.exists():
        shutil.rmtree(stac_dir)

    # create destination skeleton STAC catalog from catalog definitions
    root_stac_catalog = create_root_catalog(definitions)

    for source_collection_file in source_collections_files:
        # create STAC collection corresponding to input collection ID and add to STAC catalog
        source_collection_metadata = psup.read_collection_metadata(source_collection_file)
        collection_id = source_collection_metadata.id
        urn_collection_id = f'urn:pdssp:ias:collection:{collection_id}'  # temporary patch
        print(f'creating and adding STAC collection: {urn_collection_id}.')
        transformer = transformer_factory.create_transformer(source_collection_metadata.schema_name)
        collection_definition = definitions.get_collection(urn_collection_id)
        stac_collection = transformer.create_stac_collection(source_collection_metadata, definition=collection_definition)

        # read product metadata from source collection file
        data_path = str(Path(source_collection_file).parent)
        if urn_collection_id == 'urn:pdssp:ias:collection:mex_omega_cubes_rdr':  # temporary patch
            data_path = '/Users/nmanaud/workspace/pdssp/data/ias/source/mars/mex_omega_c_proj_ddr'
        products = psup.read_products_metadata(source_collection_file)
        for product_metadata in products[0:100]: #[12:22]:
            # item_definition = None
            # item_definition = definitions.get_item_definition(collection_id, item_id=item_id)
            stac_item = transformer.create_stac_item(product_metadata, definition=collection_definition, collection_id=collection_id, data_path=data_path)
            stac_collection.add_item(stac_item)

        # update collection extent from items
        stac_collection.update_extent_from_items()

        # add collection to the output STAC catalog
        # print(get_urn_id(collection_definition.path))
        # stac_catalog = root_stac_catalog.get_child(collection_definition.path)  # TODO: add and use a new `parent_catalog` property to CollectionDefinition class instead of `path`
        stac_catalog = root_stac_catalog.get_child(get_urn_id(collection_definition.path))
        stac_catalog.add_child(stac_collection)
        print()

    # save STAC catalog
    print()
    print(f'saving to: {str(stac_dir)}')
    Path.mkdir(stac_dir, parents=True, exist_ok=True)
    # stac_catalog.describe()
    root_stac_catalog.normalize_hrefs(str(stac_dir))
    root_stac_catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print('Done.')