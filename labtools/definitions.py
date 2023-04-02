"""Catalog definition module."""

from typing import Any, Dict, List, Union, Optional
from pydantic import BaseModel, Field
import yaml
from pathlib import Path
import copy

from stac_pydantic import Collection, Catalog, Item
from stac_pydantic.shared import Asset, Provider
from stac_pydantic.item import ItemProperties
from stac_pydantic.links import Link

import labtools.schemas.pdssp_stac as pdssp_stac

from datetime import datetime

# TODO: rename most 'collection' to 'collection_definition', and 'catalog' to 'catalog_definition' variable/method names.

STAC_EXTENSIONS_URLS = {
    'ssys': 'https://raw.githubusercontent.com/thareUSGS/ssys/main/json-schema/schema.json',
    'sci': 'https://stac-extensions.github.io/scientific/v1.0.0/schema.json',
    'processing': 'https://stac-extensions.github.io/processing/v1.1.0/schema.json'
}

def get_stac_extension_prefix(stac_extension_url):
    for stac_extension_prefix in STAC_EXTENSIONS_URLS.keys():
        if stac_extension_url == STAC_EXTENSIONS_URLS[stac_extension_prefix]:
            return stac_extension_prefix
    raise Exception(f'Undefined {stac_extension_url!r} STAC extension url. Allowed extensions: {list(STAC_EXTENSIONS_URLS.keys())}.')

def get_stac_extension_url(stac_extension_prefix):
    if stac_extension_prefix in STAC_EXTENSIONS_URLS.keys():
        return STAC_EXTENSIONS_URLS[stac_extension_prefix]
    else:
        raise Exception(f'Undefined {stac_extension_prefix!r} STAC extension prefix. Allowed extensions: {list(STAC_EXTENSIONS_URLS.keys())}.')


class SourceDefinition(BaseModel):
    url: str
    metadata_schema: Optional[str] = Field(alias='schema')


class ItemDefinition(Item):
    id: str
    data_url: Optional[str]
    extensions: Optional[list[str]]
    sci_publications: Optional[list[pdssp_stac.PDSSP_STAC_SciPublication]]
    properties: Optional[ItemProperties]
    assets: Optional[Dict[str, Asset]] = {}
    links: Optional[list[Link]] = []

class CollectionDefinition(Collection):
    id: str
    source: SourceDefinition
    title: str
    description: str
    extensions: list[str]
    processing_level: str
    ssys_targets: list[str]  #= Field(None, alias='ssys:targets')
    sci_publications: list[pdssp_stac.PDSSP_STAC_SciPublication]

    items: Optional[list[ItemDefinition]]
    """Items definitions"""

    links: Optional[list[Link]]

    path: str
    """Parent catalog path relative to root catalog definition path."""

    def get_source_collection_file(self):
        return Path(self.path) / self.id / f'{self.id}.json'


class CatalogDefinition(Catalog):
    id: str
    title: str
    description: str
    extensions: list[str]
    providers: Optional[list[Provider]]  # used as default for child catalogs and/or collections
    ssys_targets: list[str]  #= Field(None, alias='ssys:targets')

    catalogs: list[str]
    """List of catalog ids."""

    collections: list[str]
    """List of collection ids."""

    path: str
    """Catalog path relative to root catalog."""


class InvalidYAMLDefinition(Exception):
    """Invalid YAML definition error."""


class Definitions:
    """Definitions class responsible for loading and parsing an input YAML Catalog Definition file into
    accessible catalog and collection definitions.

    Input catalog is assumed to be the root catalog.
    """
    def __init__(self, yaml_file=''):
        self.catalogs = [] # : list[CatalogDefinition]
        self.collections = [] #: list[CollectionDefinition]
        self.path = yaml_file
        if yaml_file:
            self.load_root_catalog(yaml_file)

    def catalog_tree(self):
        """[WIP] Returns a string representation of the catalog structure definition.
        """
        s = ''
        catalog = self.catalogs[0]
        s += f'{catalog.id}/ (root)\n'
        for subcatalog_id in catalog.catalogs:
            subcatalog = self.get_catalog(subcatalog_id)
            s += f'  {subcatalog_id}/\n'
            for collection_id in subcatalog.collections:
                s += f'    - {collection_id}\n'
        return s

    def load_root_catalog(self, yaml_file: str) -> None:
        # parse YAML registry (root) catalog file
        yaml_catalog_dict = self.parse_yaml_catalog_file(yaml_file)
        self.add_catalog(yaml_catalog_dict)
        self.catalogs.reverse()
        self.collections.reverse()

    def create_catalog_definition(self, yaml_catalog_dict, parent_catalog_definition: CatalogDefinition = None) -> CatalogDefinition:
        """Returns a CatalogDefinition object for a given input YAML catalog dictionary.
        """

        # set 'stac_extensions' from extension prefix in `extensions` YAML dict
        stac_extensions_prefixes = yaml_catalog_dict['extensions']
        stac_extensions = []
        for stac_extension_prefix in stac_extensions_prefixes:
            stac_extensions.append(get_stac_extension_url(stac_extension_prefix))
        yaml_catalog_dict.update({'stac_extensions': stac_extensions})

        # set default 'links'
        if 'links' not in yaml_catalog_dict.keys():
            yaml_catalog_dict.update({'links': []})

        # set default 'providers'
        if 'providers' not in yaml_catalog_dict.keys():
            if parent_catalog_definition:
                yaml_catalog_dict.update({'providers': parent_catalog_definition.providers})
            else:
                yaml_catalog_dict.update({'providers': []})

        # set default 'ssys_targets'
        if 'ssys_targets' not in yaml_catalog_dict.keys():
            yaml_catalog_dict.update({'ssys_targets': []})

        # set default 'sci_publications'
        if 'sci_publications' not in yaml_catalog_dict.keys():
            yaml_catalog_dict.update({'sci_publications': []})

        # set child catalogs and collections IDs
        catalogs = []
        collections = []
        if 'catalogs' in yaml_catalog_dict.keys():
            catalogs = yaml_catalog_dict['catalogs']
        if 'collections' in yaml_catalog_dict.keys():
            collections = yaml_catalog_dict['collections']
        yaml_catalog_dict.update({'catalogs': catalogs})
        yaml_catalog_dict.update({'collections': collections})

        # set catalog path relative to root catalog
        if 'path' not in yaml_catalog_dict.keys():
            relpath = '.'
            if parent_catalog_definition:
                relpath = parent_catalog_definition.path
            yaml_catalog_dict.update({'path': relpath})

        return CatalogDefinition(**yaml_catalog_dict)

    def create_collection_definition(self, yaml_collection_dict, parent_catalog_definition: CatalogDefinition = None) -> CollectionDefinition:
        """Returns a CollectionDefinition object for input YAML collection dictionary."""

        # set 'stac_extensions' from extension prefix in `extensions` YAML dict
        stac_extensions_prefixes = yaml_collection_dict['extensions']
        stac_extensions = []
        for stac_extension_prefix in stac_extensions_prefixes:
            stac_extensions.append(get_stac_extension_url(stac_extension_prefix))
        yaml_collection_dict.update({'stac_extensions': stac_extensions})

        # set default 'links'
        if 'links' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'links': []})

        # set default 'keywords'
        if 'keywords' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'keywords': []})

        # set default 'extent'
        if 'extent' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'extent': {'spatial': {'bbox': [[]]}, 'temporal': {'interval': [[]]}}})

        # set default 'license'
        if 'license' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'license': 'Undefined'})

        # set default 'providers'
        if 'providers' not in yaml_collection_dict.keys():
            if parent_catalog_definition:
                yaml_collection_dict.update({'providers': parent_catalog_definition.providers})
            else:
                yaml_collection_dict.update({'providers': []})

        # set default 'ssys_targets'
        if 'ssys_targets' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'ssys_targets': []})

        # set default 'processing_level'
        if 'processing_level' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'processing_level': ''})

        # set default 'sci_publications'
        if 'sci_publications' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'sci_publications': []})

        # set default 'sci_publications'
        if 'items' not in yaml_collection_dict.keys():
            yaml_collection_dict.update({'items': []})

        # set collection path relative to root catalog
        relpath = '.'
        if parent_catalog_definition:
            relpath = parent_catalog_definition.path
        yaml_collection_dict.update({'path': relpath})
        # print(yaml_collection_dict)
        return CollectionDefinition(**yaml_collection_dict)

    def add_catalog(self, yaml_catalog_dict, parent_catalog_definition: CatalogDefinition = None):
        #print(f'catalog_relpath = {relpath}')
        # raise exception if required YAML `catalog` attributes are missing
        for yaml_attr in ['id', 'title', 'description']:
            if yaml_attr not in yaml_catalog_dict.keys():
                raise Exception(f'Missing YAML catalog `{yaml_attr}` attribute: {yaml_catalog_dict}')

        # create and add catalog to registry
        catalog_definition = self.create_catalog_definition(yaml_catalog_dict, parent_catalog_definition=parent_catalog_definition)

        # inherit providers from parent catalog if defined.
        if not catalog_definition.providers:
            if parent_catalog_definition:
                catalog_definition.providers = parent_catalog_definition.providers

        # inherit links from parent catalog if defined.
        if not catalog_definition.links:
            if parent_catalog_definition:
                catalog_definition.links = parent_catalog_definition.links

        relpath = '.'
        if 'path' in yaml_catalog_dict.keys():
            relpath = yaml_catalog_dict['path']

        # set default YAML `catalogs` attribute value to empty list if missing
        catalogs_ids = []
        for catalog_definition_file in catalog_definition.catalogs:  # path relative to catalog definition YAML file path, eg: 'moccas/catalog.yaml'
            catalog_definition_file_relpath = Path(relpath, catalog_definition_file)  # path relative to root catalog path, eg: 'mars/moccas/catalog.yaml'
            catalog_definition_file_abspath = str(Path(Path(self.path).parent, catalog_definition_file_relpath))  # eg: /Users/nmanaud/workspace/pdssp/pdssp-labtools/data/definitions/ias/mars/moccas/catalog.yaml

            yaml_subcatalog_dict = self.parse_yaml_catalog_file(catalog_definition_file_abspath)
            yaml_subcatalog_dict.update({'path': str(catalog_definition_file_relpath.parent)})

            self.add_catalog(yaml_subcatalog_dict, parent_catalog_definition=catalog_definition)
            if self.last_added_catalog_id():
                catalogs_ids.append(self.last_added_catalog_id())
            else:
                raise InvalidYAMLDefinition('Invalid YAML collection catalog: {catalog_dict}')

        # set default YAML `collections` attribute value to empty list if missing
        collections_ids = []
        for catalog_definition_file in catalog_definition.collections:
            catalog_definition_file_relpath = Path(relpath, catalog_definition_file)
            catalog_definition_file_abspath = str(Path(Path(self.path).parent, catalog_definition_file_relpath))
            yaml_collection_dict = self.parse_yaml_collection_file(catalog_definition_file_abspath)
            self.add_collection(yaml_collection_dict, parent_catalog_definition=catalog_definition)  # str(collections_relpath.parent)
            if self.last_added_collection_id():
                collections_ids.append(self.last_added_collection_id())
            else:
                raise InvalidYAMLDefinition(f'Invalid YAML collection definition: {yaml_collection_dict}')

        # Update and add catalog and collection definitions
        catalog_definition.catalogs = catalogs_ids
        catalog_definition.collections = collections_ids

        self.catalogs.append(catalog_definition)

    def add_collection(self, yaml_collection_dict, parent_catalog_definition: CatalogDefinition):
        # raise exception if required YAML `collection` attributes are missing
        for yaml_attr in ['id', 'title', 'description', 'source']:
            if yaml_attr not in yaml_collection_dict.keys():
                raise Exception(f'Missing YAML collection `{yaml_attr}` attribute in: {yaml_collection_dict}')

        # create and add catalog to registry
        collection_definition = self.create_collection_definition(yaml_collection_dict, parent_catalog_definition=parent_catalog_definition)

        # inherit providers from parent catalog if defined.
        if not collection_definition.providers:
            if parent_catalog_definition:
                collection_definition.providers = parent_catalog_definition.providers

        # add collection definition
        self.collections.append(collection_definition)

    def parse_yaml_catalog_file(self, yaml_catalog_relpath):
        with open(yaml_catalog_relpath, mode='r') as file:
            yaml_catalog_dict = (yaml.safe_load(file))
        catalog_dict = {}
        if 'catalog' in yaml_catalog_dict.keys():
            catalog_dict = yaml_catalog_dict['catalog']
        return catalog_dict

    def parse_yaml_collection_file(self, yaml_collection_relpath):
        with open(yaml_collection_relpath, mode='r') as file:
            yaml_collection_dict = (yaml.safe_load(file))
        collection_dict = {}
        if 'collection' in yaml_collection_dict.keys():
            collection_dict = yaml_collection_dict['collection']
        return collection_dict

    def last_added_catalog_id(self):
        last_added_catalog_id = ''
        if self.catalogs:
            last_added_catalog_id = self.catalogs[-1].id
        return last_added_catalog_id

    def last_added_collection_id(self):
        last_added_collection_id = ''
        if self.collections:
            last_added_collection_id = self.collections[-1].id
        return last_added_collection_id

    def get_item_definition(self, collection_id, item_id=None) -> Optional[ItemDefinition]:
        """Returns a generic item definition inheriting from the definition of given collection ID.
        """
        # get parent collection definition
        collection_definition = self.get_collection(collection_id)

        if item_id:
            for item_definition in collection_definition.items:
                if item_definition.id == item_id:
                    return item_definition
            print(f'Definition of item {item_id!r} in {collection_id!r} not found.')
            return None

        # create item definition object
        item_definition = ItemDefinition(
            id='*',
            stac_version=collection_definition.stac_version,
            properties={'datetime': datetime.now()},
            assets={},
            links=collection_definition.links,
            extensions=collection_definition.extensions,
            stac_extensions=collection_definition.stac_extensions,
            data_url=''
        )
        return item_definition

    def get_collections_ids(self, id='', path='') -> list[str]:
        collections_ids = []
        for collection in self.collections:
            if (id in collection.id) and (path in collection.path):
                collections_ids.append(collection.id)
        return collections_ids

    def get_collections(self, id='', path='') -> list[CollectionDefinition]:
        matching_collections = []
        for collection in self.collections:
            if (id in collection.id) and (path in collection.path):
                matching_collections.append(collection)
        return matching_collections

    def get_collection(self, id) -> Optional[CollectionDefinition]:
        for collection in self.collections:
            if collection.id == id:
                return collection
        return None

    def get_catalogs_ids(self, id='', path='') -> list[str]:
        catalogs_ids = []
        for catalog in self.catalogs:
            if (id in catalog.id) and (path in catalog.path):
                catalogs_ids.append(catalog.id)
        return catalogs_ids

    def get_catalogs(self, id='', path='') -> list[CatalogDefinition]:
        matching_catalogs = []
        for catalog in self.catalogs:
            if (id in catalog.id) and (path in catalog.path):
                matching_catalogs.append(catalog)
        return matching_catalogs

    def get_catalog(self, id) -> Optional[CatalogDefinition]:
        for catalog in self.catalogs:
            if catalog.id == id:
                return catalog
        return None

    def get_root_catalog(self) -> Optional[CatalogDefinition]:
        catalogs = self.get_catalogs(path='.')
        if catalogs:
            return catalogs[0]
        else:
            raise Exception('Root STAC catalog definition not found.')