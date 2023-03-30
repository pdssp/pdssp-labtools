"""Abstract STAC transformer."""
from typing import Any, Dict, List, Union, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel
from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection, SpatialExtent, TimeInterval, Extent, Range
from stac_pydantic.item import Item, ItemProperties, ItemCollection
from stac_pydantic.api.extensions.context import ContextExtension
from stac_pydantic.links import Link, Links
from stac_pydantic.shared import Asset, Provider, DATETIME_RFC339, StacCommonMetadata, NumType
from stac_pydantic.version import STAC_VERSION
from geojson.geometry import Geometry

import pystac
from pystac.extensions.scientific import ScientificExtension

from datetime import datetime

from labtools.schemas import factory as metadata_factory
from labtools.definitions import ItemDefinition, CollectionDefinition, CatalogDefinition

STAC_SCHEMA_NAME = 'PDSSP_STAC'


class InvalidModelObjectTypeError(Exception):
    """Custom error that is raised when invalid STAC object type is passed.
    """
    def __int__(self, object_type: str) -> None:
        self.object_type = object_type
        self.message = f"Invalid `{object_type}` type. Allowed object types are 'collection' or 'item'."
        super().__init__(self.message)


class AbstractTransformer(ABC):
    """Abstract source to STAC schemas metadata transformer.

    Default methods are implemented using optional item or/and collection definitions as source
    metadata for transformation.
    """

    def get_item_id(self, metadata: BaseModel, definition: ItemDefinition = None) -> str:
        item_id = ''
        if definition:
            item_id = definition.id
        return item_id

    def get_collection_id(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
        collection_id = ''
        if definition:
            collection_id = definition.id
        return collection_id

    def get_stac_version(self) -> str:
        return STAC_VERSION

    def get_item_links(self, metadata: BaseModel, definition: ItemDefinition = None) -> list[Link]:
        item_links = ''
        if definition:
            item_links = definition.links
        return item_links

    def get_item_assets(self, metadata: BaseModel, definition: ItemDefinition = None) -> Dict[str, Asset]:
        item_assets = []
        if definition:
            item_assets = definition.assets
        return item_assets

    def get_collection_links(self, metadata: BaseModel, definition: CollectionDefinition = None) -> list[Link]:
        collection_links = []
        if definition:
            collection_links = definition.links
        return collection_links

    def get_collection_assets(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Dict[str, Asset]:
        collection_assets = []
        if definition:
            collection_assets = definition.assets
        return collection_assets

    def get_stac_extensions(self, metadata: BaseModel, definition: Union[CollectionDefinition, CatalogDefinition] = None) -> list[str]:
        stac_extensions = []
        if definition:
            stac_extensions = definition.stac_extensions
        return stac_extensions

    def get_title(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
        title = ''
        if definition:
            title = definition.title
        return title

    def get_description(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
        description = ''
        if definition:
            description = definition.title
        return description

    def get_keywords(self, metadata: BaseModel, definition: CollectionDefinition = None) -> list[str]:
        keywords = ''
        if definition:
            keywords = definition.keywords
        return keywords

    def get_geometry(self, metadata: BaseModel, definition: ItemDefinition = None) -> Optional[Geometry]:
        geometry = None
        if definition:
            geometry = definition.geometry
        return geometry

    def get_extent(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Extent:
        extent = Extent(spatial=SpatialExtent(bbox=[[]]), temporal=TimeInterval(interval=[[]]))
        if definition:
            extent = definition.extent
        return extent

    def get_bbox(self, metadata: BaseModel, definition: ItemDefinition = None) -> list[list[float]]:
        bbox = [[]]
        if definition:
            bbox = definition.bbox
        return bbox

    def get_providers(self, metadata: BaseModel, definition: CollectionDefinition = None) -> list[Provider]:
        providers = []
        if definition:
            providers = definition.providers
        return providers

    def get_licence(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
        licence = ''
        if definition:
            licence = definition.license
        return licence

    def get_summaries(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Optional[Dict[str, Union[Range, List[Any], Dict[str, Any]]]]:
        summaries = None
        if definition:
            summaries = definition.summaries
        return summaries

    @abstractmethod
    def get_properties(self, metadata: BaseModel, definition: ItemDefinition = None) -> dict:
        pass

    @abstractmethod
    def get_ssys_properties(self, metadata: BaseModel, definition: ItemDefinition = None) -> BaseModel:
        raise NotImplementedError

    @abstractmethod
    def get_ssys_fields(self, metadata: BaseModel, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_sci_properties(self, metadata: BaseModel, definition: ItemDefinition = None) -> BaseModel:
        raise NotImplementedError

    @abstractmethod
    def get_sci_fields(self, metadata: BaseModel, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_processing_properties(self, metadata: BaseModel, definition: ItemDefinition = None) -> BaseModel:
        raise NotImplementedError

    @abstractmethod
    def get_processing_fields(self, metadata: BaseModel, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        raise NotImplementedError

    def get_extension_properties(self, stac_extension, metadata: BaseModel, definition: ItemDefinition = None) -> BaseModel:  # ExtensionItemProperties
        if stac_extension == 'ssys':
            return self.get_ssys_properties(metadata, definition=definition)
        elif stac_extension == 'sci':
            return self.get_sci_properties(metadata, definition=definition)
        elif stac_extension == 'processing':
            return self.get_processing_properties(metadata, definition=definition)
        else:
            raise Exception(f'Undefined {stac_extension} STAC extension.')

    def get_extension_fields(self, stac_extension, metadata: BaseModel, definition: Union[ItemDefinition, CollectionDefinition] = None) -> {}:
        if stac_extension == 'ssys':
            return self.get_ssys_fields(metadata, definition=definition)
        elif stac_extension == 'sci':
            return self.get_sci_fields(metadata, definition=definition)
        elif stac_extension == 'processing':
            return self.get_processing_fields(metadata, definition=definition)
        else:
            raise Exception(f'Undefined {stac_extension} STAC extension.')

    # def get_item_extension_fields(self, metadata: BaseModel, stac_extension, definition: ItemDefinition = None) -> dict:
    #     return {}
    #
    # def get_collection_extension_fields(self, metadata: BaseModel, stac_extension, definition: CollectionDefinition = None) -> dict:
    #     return {}

    def create_stac_item(self, metadata: BaseModel, definition=None, collection_id='') -> pystac.Item:

        schema_name = metadata_factory.get_schema_name(metadata)
        object_type = metadata_factory.get_object_type(metadata)
        if object_type.lower() != 'item':
            raise ValueError(f"Input metadata object not of 'item' type: {schema_name}, {object_type}.")

        stac_extensions = self.get_stac_extensions(metadata, definition=definition)
        stac_item_dict = {
            'type': 'Feature',  # REQUIRED
            'stac_version': self.get_stac_version(),  # REQUIRED
            'stac_extensions': stac_extensions,
            'id': self.get_item_id(metadata, definition=definition),  # REQUIRED
            'geometry': self.get_geometry(metadata, definition=definition),  # REQUIRED
            'bbox': self.get_bbox(metadata, definition=definition),  # REQUIRED
            'properties': self.get_properties(metadata, definition=definition, stac_extensions=stac_extensions),  # REQUIRED
            'links': self.get_item_links(metadata, definition=definition),  # REQUIRED
            'assets': self.get_item_assets(metadata, definition=definition),  # REQUIRED
            'collection': collection_id,
            'extra_fields': {}
        }
        # add STAC extensions extra fields
        for stac_extension in stac_extensions:
            stac_item_dict['extra_fields'].update(
                self.get_extension_fields(stac_extension, metadata, definition=definition))

        # attempt to create destination STAC Item metadata object (PDSSP_STAC schema)
        stac_item_metadata = metadata_factory.create_metadata_object(stac_item_dict, STAC_SCHEMA_NAME)

        # create PySTAC Item
        stac_item = pystac.Item(
            id=stac_item_metadata.id,
            stac_extensions=stac_extensions,
            geometry=stac_item_metadata.geometry,
            bbox=stac_item_metadata.bbox,
            datetime=stac_item_metadata.properties.datetime,  # datetime.fromisoformat(stac_item_metadata.properties['datetime']),
            properties=stac_item_metadata.properties,
            extra_fields=stac_item_metadata.extra_fields,  # eg: {'ssys:targets': stac_item_metadata.ssys_targets},
            collection=collection_id
        )

        # add assets to pySTAC item
        for key in stac_item_metadata.assets:
            asset_metadata = stac_item_metadata.assets[key]
            stac_item.add_asset(
                key=key,
                asset=pystac.Asset(
                    href=asset_metadata.href,
                    title=asset_metadata.title,
                    description=asset_metadata.description,
                    media_type=asset_metadata.type,
                    roles=asset_metadata.roles
                )
            )

        # # what should be the correct approach, using pystac extensions.
        # for stac_extension in stac_extensions:
        #     ssys_ext = SsysExtension.ext(stac_item, add_if_missing=True)
        #     processing_ext = ProcessingExtension.ext(stac_item, add_if_missing=True)
        #     sci_ext = ScientificExtension.ext(stac_item, add_if_missing=True)

        return stac_item

    def create_stac_collection(self, metadata: BaseModel, definition: CollectionDefinition = None) -> pystac.Collection:
        """Returns a STAC collection object given an input source metadata object, and optional associated definition."""

        schema_name = metadata_factory.get_schema_name(metadata)
        object_type = metadata_factory.get_object_type(metadata)
        if object_type.lower() != 'collection':
            raise ValueError(f"Input metadata object not of 'collection' type: {schema_name}, {object_type}.")

        stac_extensions = self.get_stac_extensions()

        stac_collection_dict = {
            'type': 'Collection',  # REQUIRED
            'stac_version': self.get_stac_version(),  # REQUIRED
            'stac_extensions': stac_extensions,
            'id': self.get_collection_id(metadata, definition=definition),  # REQUIRED
            'title': self.get_title(metadata, definition=definition),
            'description': self.get_description(metadata, definition=definition),  # REQUIRED
            'keywords': self.get_keywords(metadata, definition=definition),
            'licence': self.get_licence(metadata, definition=definition),  # REQUIRED
            'providers': self.get_providers(metadata, definition=definition),
            'extent': self.get_extent(metadata, definition=definition),  # REQUIRED
            'summaries': self.get_summaries(metadata, definition=definition),  # STRONGLY RECOMMENDED
            'links': self.get_collection_links(metadata, definition=definition),  # REQUIRED
            'assets': self.get_collection_assets(metadata, definition=definition),
            'extra_fields': {}
        }
        for stac_extension in stac_extensions:
            stac_collection_dict['extra_fields'].update(
                self.get_extension_fields(stac_extension, metadata, definition=definition))  # for example: { 'ssys_targets': ['Mars'] }

        # attempt to create destination STAC Collection metadata object (PDSSP_STAC schema)
        stac_collection_metadata = metadata_factory.create_metadata_object(stac_collection_dict, STAC_SCHEMA_NAME)

        # create STAC collection object from STAC metadata object
        stac_collection = pystac.Collection(
            id=stac_collection_metadata.id,
            stac_extensions=stac_collection_metadata.stac_extensions,
            title=stac_collection_metadata.title,
            description=stac_collection_metadata.description,
            extent=pystac.Extent(pystac.SpatialExtent(bboxes=[[]]), pystac.TemporalExtent(intervals=[[]])),
            license=stac_collection_metadata.licence,
            extra_fields=stac_collection_metadata.extra_fields  # {'ssys:targets': 'MARS'}
        )

        # # add STAC Scientific Extension
        # if 'sci' in stac_extensions:
        #     sci_ext = ScientificExtension.ext(stac_collection, add_if_missing=True)
        #     publications = []
        #     for publication_dict in definition.sci_publications:
        #         doi = ''
        #         if 'doi' in publication_dict.keys():
        #             doi = publication_dict['doi']
        #         publication = pystac.extensions.scientific.Publication(
        #             doi=doi,
        #             citation=publication_dict['citation']
        #         )
        #         publications.append(publication)
        #     sci_ext.publications = publications

        return stac_collection
