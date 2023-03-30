from pydantic import BaseModel
from labtools.schemas import factory
from labtools.ias.psup import PSUP_Collection

SCHEMA_NAME = 'OMEGA_C_PROJ'
TRANSFORMER_MODULE = 'labtools.ias.transformers.omega_c_proj'

class OMEGA_C_Proj_Record(BaseModel):
    orbit_number: str
    cube_number: str
    download_sav: str
    sav_human_file_size: str
    download_nc: str
    nc_human_file_size: str
    start_date: str
    end_date: str
    solar_longitude: float
    easternmost_longitude: float
    westernmost_longitude: float
    maximum_latitude: float
    minimum_latitude: float
    data_quality_id: str

    def get_download_url(self):
        return self.download_sav

def register() -> None:
    factory.register(SCHEMA_NAME, OMEGA_C_Proj_Record, PSUP_Collection)

def get_transformer_module() -> str:
    return TRANSFORMER_MODULE

# {
#   "uri": "http://localhost:8282/ds/omega_c_channel/records/1",
#   "id": "1",
#   "orbit_number": "18",
#   "cube_number": "0",
#   "download_sav": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/omegacubes/cubes_L3/0018_0.sav",
#   "sav_human_file_size": "9.5 MB",
#   "download_nc": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/omegacubes/cubes_L3/0018_0.nc",
#   "nc_human_file_size": "9.3 MB",
#   "start_date": "2004-01-14T00:19:12.032",
#   "end_date": "2004-01-14T00:23:03.059",
#   "solar_longitude": "333.063",
#   "easternmost_longitude": "322.961",
#   "westernmost_longitude": "318.133",
#   "maximum_latitude": "-54.5625",
#   "minimum_latitude": "-60.0",
#   "data_quality_id": "3"
# }