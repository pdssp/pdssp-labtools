from pydantic import BaseModel
from labtools.schemas import factory
from labtools.ias.psup import PSUP_Collection

SCHEMA_NAME = 'OMEGA_CUBE'
TRANSFORMER_MODULE = 'labtools.ias.transformers.omega_cube'

class OMEGA_Cube_Record(BaseModel):
    orbit_number: str
    cube_number: str
    download_sav: str
    sav_human_file_size: str
    download_nc: str
    nc_human_file_size: str
    solar_longitude: float
    easternmost_longitude: float
    westernmost_longitude: float
    maximum_latitude: float
    minimum_latitude: float
    data_quality_id: str
    martian_year: str
    pointing_mode: str
    l_channel_ok: str
    c_channel_ok: str
    vis_channel_ok: str
    trimmed_orbit_number: str

    def get_download_url(self):
        return self.download_nc

def register() -> None:
    factory.register(SCHEMA_NAME, OMEGA_Cube_Record, PSUP_Collection)

def get_transformer_module() -> str:
    return TRANSFORMER_MODULE

# {
#   "uri": "http://localhost:8282/ds/omega_data_cubes/records/1",
#   "id": "1",
#   "orbit_number": "0006",
#   "cube_number": "0",
#   "download_sav": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/omegacubes/cubes_L2/0006_0.sav",
#   "sav_human_file_size": "66.4 MB",
#   "download_nc": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/omegacubes/cubes_L2/0006_0.nc",
#   "nc_human_file_size": "63.5 MB",
#   "solar_longitude": "330.057",
#   "easternmost_longitude": "89.693",
#   "westernmost_longitude": "87.2129",
#   "maximum_latitude": "-42.246098",
#   "minimum_latitude": "-56.0966",
#   "data_quality_id": "3",
#   "martian_year": "26",
#   "pointing_mode": "NADIR",
#   "l_channel_ok": "t",
#   "c_channel_ok": "t",
#   "vis_channel_ok": "t",
#   "trimmed_orbit_number": "6"
# }