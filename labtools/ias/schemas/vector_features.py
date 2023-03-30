from pydantic import BaseModel
from labtools.schemas import factory
from labtools.ias.psup import PSUP_Collection

SCHEMA_NAME = 'VECTOR_FEATURES'
TRANSFORMER_MODULE = 'labtools.ias.transformers.vector_features'

class Vector_Features_Record(BaseModel):
    download: str
    linktopubli: str
    vector_description: str
    vector_name: str
    vector_footprint: str
    vector_keywords: str

    def get_download_url(self):
        return self.download


def register() -> None:
    factory.register(SCHEMA_NAME, Vector_Features_Record, PSUP_Collection)


def get_transformer_module() -> str:
    return TRANSFORMER_MODULE

# {
#   "uri": "http://localhost:8282/pgismarsvector/records/8",
#   "download": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/marsdata/geojson/hyd_global_290615.json",
#   "linktopubli": "http://doi.org/10.1029/2012JE004145",
#   "vector_description": "\"Hydrated mineral sites\"",
#   "vector_id": "8",
#   "vector_name": "hyd_global_290615.json",
#   "vector_footprint": "((-180,-90),(-180,90),(180,90),(180,-90))",
#   "vector_keywords": ""
# }