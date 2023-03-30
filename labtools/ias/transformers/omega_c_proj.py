"""Transformer module for PSUP_OMEGA_C_PROJ metadata."""

from labtools.ias.schemas.omega_c_proj import (
    SCHEMA_NAME,
    OMEGA_C_Proj_Record,
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

from typing import Any, Dict, List, Union, Optional
from pathlib import Path


class OMEGA_C_PROJ_STAC_Transformer(AbstractTransformer):

    def get_item_id(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> str:
        return Path(metadata.download_nc).stem
        # return f'L3_{int(metadata.orbit_number):04}_{int(metadata.cube_number)}'

    def get_collection_id(self, metadata: PSUP_Collection, definition: CollectionDefinition = None) -> str:
        #assert metadata.id == definition.id
        return definition.id

    # def get_stac_version(self, metadata: BaseModel) -> str:
    #     pass

    # def get_item_links(self, metadata: BaseModel, definition: ItemDefinition = None) -> list[Link]:
    #     pass

    def get_item_assets(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> Dict[str, PDSSP_STAC_Asset]:
        item_assets = {
            'nc_data_file': PDSSP_STAC_Asset(
                href=metadata.download_nc,
                title=self.get_item_id(metadata, definition=definition),
                description='NetCDF4 data file',
                type='application/netcdf',
                roles=['data']
            ),
            'sav_data_file': PDSSP_STAC_Asset(
                href=metadata.download_sav,
                title=self.get_item_id(metadata, definition=definition),
                description='IDL SAV data file',
                type='application/octet-stream',
                roles=['data']
            )
        }
        return item_assets

    # def get_collection_links(self, metadata: OMEGA_C_Proj_Record, definition: CollectionDefinition = None) -> list[PDSSP_STAC_Link]:
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

    # def get_geometry(self, metadata: BaseModel, definition: ItemDefinition = None) -> Optional[Geometry]:
    #     pass

    # def get_extent(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Extent:
    #     pass

    def get_bbox(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> list[float]:
        return [
            (float(metadata.westernmost_longitude) + 180.0) % 360.0 - 180.0,
            float(metadata.minimum_latitude),
            (float(metadata.easternmost_longitude) + 180.0) % 360.0 - 180.0,
            float(metadata.maximum_latitude)
        ]

    # def get_providers(self, metadata: BaseModel, definition: CollectionDefinition = None) -> list[Provider]:
    #     pass

    # def get_licence(self, metadata: BaseModel, definition: CollectionDefinition = None) -> str:
    #     pass

    # def get_summaries(self, metadata: BaseModel, definition: CollectionDefinition = None) -> Optional[Dict[str, Union[Range, List[Any], Dict[str, Any]]]]:
    #     pass

    def get_properties(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None, stac_extensions=None) -> dict:
        properties = stac.PDSSP_STAC_Properties(
            datetime=utc_to_iso(metadata.UTC_start_time, timespec='milliseconds'),
            created=utc_to_iso(metadata.Product_creation_time, timespec='milliseconds'),
            start_datetime=utc_to_iso(metadata.UTC_start_time, timespec='milliseconds'),
            end_datetime=utc_to_iso(metadata.UTC_stop_time, timespec='milliseconds'),
            platform=metadata.ihid,
            instruments=[metadata.iid],
            gsd=metadata.Map_scale
        )

        properties_dict = properties.dict(exclude_unset=True)
        for stac_extension in stac_extensions:
            properties_dict.update(self.get_extension_properties(stac_extension, metadata))

        return properties_dict

    def get_ssys_properties(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> PDSSP_STAC_SsysProperties:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            ssys_properties_dict = {
                'ssys:targets': ['Mars']
            }
        else:
            raise InvalidModelObjectTypeError(object_type)

        return PDSSP_STAC_SsysProperties(**ssys_properties_dict)

    def get_ssys_fields(self, metadata: OMEGA_C_Proj_Record, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            ssys_fields = {}
        elif object_type == 'collection':
            ssys_fields = { 'ssys:targets': [definition.ssys_targets] }
        else:
            raise InvalidModelObjectTypeError(object_type)
        return ssys_fields

    def get_sci_properties(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> PDSSP_STAC_SciProperties:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'item':
            sci_properties_dict = {}
        else:
            raise InvalidModelObjectTypeError(object_type)
        return sci_properties_dict

    def get_sci_fields(self, metadata: OMEGA_C_Proj_Record, definition: Union[ItemDefinition, CollectionDefinition] = None) -> dict:
        object_type = metadata_factory.get_object_type(metadata)
        if object_type == 'collection':
            sci_fields = {
                # 'sci:doi': '',
                # 'sci_citation': '',
                'sci_publications': definition.sci_publications
            }
        else:
            raise InvalidModelObjectTypeError(object_type)
        return sci_fields

    def get_processing_properties(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> PDSSP_STAC_ProcessingProperties:
        raise NotImplementedError

    def get_processing_fields(self, metadata: OMEGA_C_Proj_Record, definition: ItemDefinition = None) -> dict:
        raise NotImplementedError

def register() -> None:
    transformer_factory.register(SCHEMA_NAME, OMEGA_C_PROJ_STAC_Transformer)
