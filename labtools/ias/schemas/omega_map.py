from pydantic import BaseModel
from labtools.schemas import factory
from labtools.ias.psup import PSUP_Collection

SCHEMA_NAME = 'OMEGA_MAP'
TRANSFORMER_MODULE = 'labtools.ias.transformers.omega_map'

class OMEGA_Map_Record(BaseModel):
    preview: str
    download: str
    raster_description: str
    raster_name: str
    raster_ldescription: str
    linktopubli: str
    raster_keywords: str

    def get_download_url(self):
        return self.download


def register() -> None:
    factory.register(SCHEMA_NAME, OMEGA_Map_Record, PSUP_Collection)


def get_transformer_module() -> str:
    return TRANSFORMER_MODULE

# {
#   "uri": "http://localhost:8282/pgismarsraster/records/33",
#   "preview": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/marsdata/omega/png/albedo_filled_reduce.png",
#   "download": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/marsdata/omega/fits/albedo_filled.fits",
#   "raster_description": "\"OMEGA Albedo Filled\"",
#   "raster_name": "albedo_filled.fits",
#   "raster_ldescription": "\"60 ppd global map of Solar Albedo from OMEGA data fileld with TES 20 ppd solar albedo global maps (Putzig and Mellon, 2007b) (21600x10800 pixels). This map is 100% filled. Variable name is \"albedo\". \"latitude\" and \"longitude\" indicate the coordinates of the centers of the pixels. Reference : Vincendon et al., Icarus, 2015\"",
#   "linktopubli": "http://doi.org/10.1016/j.icarus.2014.10.029",
#   "raster_id": "33",
#   "raster_keywords": "{\"albedo\",\"filled\",\"global\"}"
# }