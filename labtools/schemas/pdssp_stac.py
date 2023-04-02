""""PDSSP STAC schema.

Wrapper around Pydantic models for STAC Catalogs, Collections, Items (and the STAC API spec) overwriting STAC models
fields if necessary to compliant with specific data catalog producer/provider requirements. For example, a null geometry
might not be acceptable.

https://github.com/stac-utils/stac-pydantic

"""
from typing import Any, Dict, List, Union, Optional
from pydantic import BaseModel, Field, Extra

from labtools.schemas import factory

from stac_pydantic.catalog import Catalog
from stac_pydantic.collection import Collection, SpatialExtent, TimeInterval, Extent, Range
from stac_pydantic.item import Item, ItemProperties, ItemCollection
from stac_pydantic.api.extensions.context import ContextExtension
from stac_pydantic.links import Link, Links
from stac_pydantic.shared import Asset, Provider, DATETIME_RFC339, StacCommonMetadata, NumType
from stac_pydantic.version import STAC_VERSION

SCHEMA_NAME = 'PDSSP_STAC'
TRANSFORMER_MODULE = 'labtools.transformers.pdssp_stac'
STAC_EXTENSIONS = ['ssys', 'processing']

class PDSSP_STAC_SpatialExtent(SpatialExtent):
    # bbox: list[list[float]]
    # """Potential spatial extents covered by the Collection."""
    pass


class PDSSP_STAC_TimeInterval(TimeInterval):
    # interval: list[list[str]]
    # """Potential temporal extents covered by the Collection."""
    pass


class PDSSP_STAC_Extent(Extent):
    # spatial: PDSSP_STAC_SpatialExtent
    # """Potential spatial extents covered by the Collection."""
    # temporal: PDSSP_STAC_TemporalExtent
    # """Potential temporal extents covered by the Collection."""
    pass


class PDSSP_STAC_Provider(Provider):
    # name: str
    # """The name of the organization or the individual."""
    # description: Optional[str]
    # """Multi-line description to add further provider information such as processing details for processors and
    # producers, hosting details for hosts or basic contact information. CommonMark 0.29 syntax MAY be used for
    # rich text representation."""
    # roles: Optional[list[str]]
    # """Roles of the provider. Any of licensor, producer, processor or host."""
    pass



class PDSSP_STAC_Link(Link):
    # href: str
    # """The actual link in the format of an URL. Relative and absolute links are both allowed."""
    # rel: str
    # """ Relationship between the current document and the linked document."""
    # type: # Optional[str]
    # """Media type of the referenced entity."""
    # title: Optional[str]
    # """A human readable title to be used in rendered displays of the link."""
    pass


class PDSSP_STAC_Collection(Collection):
    # #type: str
    # stac_version: str = STAC_VERSION
    # stac_extensions: Optional[list[str]]
    # id: str
    # title: Optional[str]
    # description: str
    # keywords: Optional[list[str]]
    # licence: str
    # providers: Optional[list[PDSSP_STAC_Provider]]
    # extent: PDSSP_STAC_Extent
    # summaries: Optional[dict]
    # links: Optional[list[PDSSP_STAC_Link]]  # WARNING: NOT optional following STAC standard -> created automatically by PySTAC.
    # assets: Optional[dict]  ## Map<string, PDSSP_STAC_Asset>: dictionary of asset objects that can be downloaded, each with a unique key
    extra_fields: Optional[dict]


class PDSSP_STAC_Asset(Asset):
    # href: str
    # title: Optional[str]
    # description: Optional[str]
    # #type: Optional[str]
    # roles: Optional[list[str]]
    pass


class PDSSP_STAC_Properties(ItemProperties, extra=Extra.allow): # STAC Common Metadata
    # title: Optional[str] #
    # description: Optional[str]
    # datetime: str  # ISO 8601 format
    # created: Optional[str]  # ISO 8601 format
    # updated: Optional[str]  # ISO 8601 format
    # start_datetime: Optional[str]  # ISO 8601 format
    # end_datetime: Optional[str]  # ISO 8601 format
    # license: Optional[str]
    # platform: Optional[str] # PDS instrument_host_id
    # instruments: Optional[list[str]] # PDS instrument_id
    # constellation: Optional[str]  # ?
    # mission: Optional[str]   # PDS mission_id
    # gsd: Optional[float]
    # ssys_targets: Optional[list[str]] = Field(None, alias='ssys:targets')
    # ssys_solar_longitude: Optional[float]
    # ssys_instrument_host: Optional[str]
    start_datetime: Optional[str] = Field(None, alias="start_datetime")
    end_datetime: Optional[str] = Field(None, alias="end_datetime")
    pdssp_solar_longitude: Optional[float] = Field(None, alias="pdssp:solar_longitude")
    pdssp_solar_distance: Optional[float] = Field(None, alias="pdssp:solar_distance")
    pdssp_incidence_angle: Optional[float] = Field(None, alias="pdssp:incidence_angle")
    pdssp_emission_angle: Optional[float] = Field(None, alias="pdssp:emission_angle")
    pdssp_phase_angle: Optional[float] = Field(None, alias="pdssp:phase_angle")


class PDSSP_STAC_Item(Item):
    ## type: str
    # stac_version: str = STAC_VERSION
    # stac_extensions: Optional[list[str]]
    # id: str
    # geometry: object  # GeoJSON Geometry
    # bbox: Union[list[float], None]
    properties: PDSSP_STAC_Properties
    # links: Optional[list[PDSSP_STAC_Link]]  # WARNING: NOT optional following STAC standard -> created automatically by PySTAC.
    # assets: dict  ## Map<string, PDSSP_STAC_Asset>: dictionary of asset objects that can be downloaded, each with a unique key.
    # collection: Optional[str]
    extra_fields: Optional[dict]


### EXTENSIONS


# class PDSSP_STAC_Extension_ItemProperties(BaseModel):
#     pass

class PDSSP_STAC_SsysProperties(BaseModel):
    ssys_targets: Optional[list[str]] = Field(..., alias="ssys:targets")


class PDSSP_STAC_SciPublication(BaseModel):
    doi: Optional[str] = Field(..., alias="doi")
    citation: Optional[str] = Field(..., alias="citation")


class PDSSP_STAC_SciProperties(BaseModel):
    sci_doi: Optional[str] = Field(alias="sci:doi")
    sci_citation: Optional[str] = Field(alias="sci:citation")
    sci_publications: Optional[list[PDSSP_STAC_SciPublication]] = Field(..., alias="sci:publications")


class PDSSP_STAC_ProcessingProperties(BaseModel):
    processing_expression: Optional[object] = Field(..., alias='processing:expression')
    processing_lineage: Optional[str] = Field(..., alias='processing:lineage')
    processing_level: Optional[str] = Field(..., alias='processing:level')
    processing_facility: Optional[str] = Field(..., alias='processing:facility')
    processing_software: Optional[dict] = Field(..., alias='processing:software')


def register() -> None:
    factory.register(SCHEMA_NAME, PDSSP_STAC_Item, PDSSP_STAC_Collection)


def get_transformer_module() -> str:
    return TRANSFORMER_MODULE