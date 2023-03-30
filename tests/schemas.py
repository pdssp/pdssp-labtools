from labtools.schemas import factory
from labtools import loader

loader.load_schemas([
    'labtools.schemas.pdssp_stac',
])
loader.load_schemas([
    'labtools.ias.schemas.omega_c_proj',
    'labtools.ias.schemas.omega_cube',
    'labtools.ias.schemas.omega_map',
    'labtools.ias.schemas.vector_features'
])
print(f'Loaded schemas: {factory.get_schema_names()}')
print()

metadata_dict = {
  "uri": "http://localhost:8282/ds/omega_c_channel/records/1",
  "id": "1",
  "orbit_number": "18",
  "cube_number": "0",
  "download_sav": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/omegacubes/cubes_L3/0018_0.sav",
  "sav_human_file_size": "9.5 MB",
  "download_nc": "http://psup.ias.u-psud.fr/sitools/datastorage/user/storage/omegacubes/cubes_L3/0018_0.nc",
  "nc_human_file_size": "9.3 MB",
  "start_date": "2004-01-14T00:19:12.032",
  "end_date": "2004-01-14T00:23:03.059",
  "solar_longitude": "333.063",
  "easternmost_longitude": "322.961",
  "westernmost_longitude": "318.133",
  "maximum_latitude": "-54.5625",
  "minimum_latitude": "-60.0",
  "data_quality_id": "3"
}
metadata = factory.create_metadata_object(metadata_dict, 'OMEGA_C_PROJ', 'item')
schema_name, object_type = factory.get_metadata_info(metadata)
print(metadata)
print(schema_name, object_type)
print()

metadata_dict = {
    "id": "features-datasets",
    "schema_name": "VECTOR_FEATURES",
    "n_products": 7
  }
metadata = factory.create_metadata_object(metadata_dict, 'VECTOR_FEATURES', 'collection')
schema_name, object_type = factory.get_metadata_info(metadata)
print(metadata)
print(schema_name, object_type)