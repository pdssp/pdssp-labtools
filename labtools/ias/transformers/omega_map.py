"""Transformer module for OMEGA_MAP metadata."""
from typing import Any, Dict, List, Union, Optional

from labtools.ias.schemas.omega_map import (
    SCHEMA_NAME,
    OMEGA_Map_Record,
    PSUP_Collection
)
from labtools.schemas.pdssp_stac import (
    PDSSP_STAC_Item,
    PDSSP_STAC_Collection,
    PDSSP_STAC_Asset,
    PDSSP_STAC_Properties
)

from labtools.schemas.pdssp_stac import (
    PDSSP_STAC_SsysProperties,
    PDSSP_STAC_ProcessingProperties,
    PDSSP_STAC_SciProperties,
)

from labtools.definitions import ItemDefinition, CollectionDefinition
from labtools.transformers.transformer import AbstractTransformer, InvalidModelObjectTypeError
from labtools.transformers import factory as transformer_factory
from labtools.schemas import factory as metadata_factory
from labtools.utils import utc_to_iso, bbox, bbox_polygon
from labtools.ias.netcdf import get_netcdf_footprint, get_netcdf_properties

from datetime import datetime
from pathlib import Path
from geojson import Polygon
import json


class OMEGA_MAP_STAC_Transformer(AbstractTransformer):

    def get_item_id(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> str:
        return Path(metadata.raster_name).stem

    def get_collection_id(self, metadata: PSUP_Collection, definition: CollectionDefinition = None) -> str:
        return metadata.id

    # def get_stac_version(self, metadata: BaseModel) -> str:
    #     pass

    # def get_item_links(self, metadata: BaseModel, definition: ItemDefinition = None) -> list[Link]:
    #     pass

    def get_item_assets(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> Dict[str, PDSSP_STAC_Asset]:
        item_assets = {
            'fits_data_file': PDSSP_STAC_Asset(
                href=metadata.download,
                title='FITS data file',  #self.get_item_id(metadata, definition=definition),
                # description='FITS data file',
                type='application/fits',
                roles=['data']
            ),
            'fits_preview_file': PDSSP_STAC_Asset(
                href=metadata.preview,
                title='Preview PNG image file',  # self.get_item_id(metadata, definition=definition),
                # description='Preview PNG image file',
                type='image/png',
                roles=['thumbnail']
            )
        }
        return item_assets

    # def get_collection_links(self, metadata: OMEGA_Map_Record, definition: CollectionDefinition = None) -> list[PDSSP_STAC_Link]:
    #     return []
    #

    # def get_collection_assets(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Dict[str, Asset]:
    #     pass

    # def get_stac_extensions(self, metadata: BaseModel) -> list[str]:
    #     pass

    # def get_title(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
    #     pass

    # def get_description(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
    #     pass

    # def get_keywords(self, metadata: BaseModel, definition: CollectionDefinition = None) -> list[str]:
    #     pass

    def get_geometry(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None, data_path: str = None) -> Optional[Dict[str, Any]]:
        """Derives and returns footprint geometry from source data file.
        """
        geometry = {'coordinates': [[[-180, -90],
                                     [-180, 90],
                                     [180, 90],
                                     [180, -90],
                                     [-180, -90]]],
                    'type': 'Polygon'}
        return geometry

    # def get_extent(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Extent:
    #     pass

    def get_bbox(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> list[float]:
        geometry = self.get_geometry(metadata, definition=definition)
        return bbox(Polygon(geometry['coordinates']))

    # def get_providers(self, metadata: BaseModel, definition: CollectionDefinition = None) -> list[Provider]:
    #     pass

    # def get_license(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
    #     pass

    # def get_summaries(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Optional[Dict[str, Union[Range, List[Any], Dict[str, Any]]]]:
    #     pass

    def get_properties(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None, data_path: str = None) -> PDSSP_STAC_Properties:

        properties_dict = {
            'datetime': datetime.now(),
            'title': metadata.raster_description[1:-1] + ' Global Map',
            'description': metadata.raster_ldescription[1:-1],
            'created': None,
            'start_datetime': '2004-01-08T12:46:15.000',
            'end_datetime': '2010-08-20T00:46:05.000',
            # 'start_datetime': utc_to_iso(metadata.start_date, timespec='milliseconds'),
            # 'end_datetime': utc_to_iso(metadata.end_date, timespec='milliseconds'),
            'mission': 'Mars Express',
            'platform': 'MEX',
            'instruments': ['OMEGA'],
            'gsd': None,
            # extra Vector_Features_Record properties of interest
        }

        return PDSSP_STAC_Properties(**properties_dict)

    def get_ssys_properties(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> PDSSP_STAC_SsysProperties:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            ssys_properties_dict = {
                'ssys:targets': ['Mars']
            }
        else:
            raise InvalidModelObjectTypeError(object_type)

        return PDSSP_STAC_SsysProperties(**ssys_properties_dict)

    def get_ssys_fields(self, metadata: OMEGA_Map_Record, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            ssys_fields = {}
        elif object_type == 'collection':
            ssys_fields = { 'ssys:targets': [definition.ssys_targets] }
        else:
            raise InvalidModelObjectTypeError(object_type)
        return ssys_fields

    def get_sci_properties(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> Optional[PDSSP_STAC_SciProperties]:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            sci_publications = []
            for sci_publication in definition.sci_publications:
                sci_publications.append(sci_publication.dict())

            sci_properties_dict = {
                # 'sci:doi': '',
                # 'sci_citation': '',
                'sci:publications': sci_publications
            }
        else:
            raise InvalidModelObjectTypeError(object_type)
        return PDSSP_STAC_SciProperties(**sci_properties_dict)

    def get_sci_fields(self, metadata: OMEGA_Map_Record, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'collection':
            # set sci_publications as dict (so as to make it "serializable")
            sci_publications = []
            for sci_publication in definition.sci_publications:
                sci_publications.append(sci_publication.dict(exclude_none=True))
            sci_fields = {}
            if sci_publications:
                sci_fields = {
                    # 'sci:doi': '',
                    # 'sci_citation': '',
                    'sci:publications': sci_publications
                }
        elif object_type == 'item':
            sci_fields = {}
        else:
            raise InvalidModelObjectTypeError(object_type)
        return sci_fields

    def get_processing_properties(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> Optional[PDSSP_STAC_ProcessingProperties]:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            return None
        else:
            raise InvalidModelObjectTypeError(object_type)
        # return PDSSP_STAC_ProcessingProperties(**processing_properties_dict)

    def get_processing_fields(self, metadata: OMEGA_Map_Record, definition: ItemDefinition = None) -> dict:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'collection':
            processing_fields = {
                'processing:level': definition.processing_level
            }
        elif object_type == 'item':
            processing_fields = {}
        else:
            raise InvalidModelObjectTypeError(object_type)
        return processing_fields


def register() -> None:
    transformer_factory.register(SCHEMA_NAME, OMEGA_MAP_STAC_Transformer)
