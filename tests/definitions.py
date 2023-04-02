from labtools.definitions import Definitions, CollectionDefinition

root_catalog_definition_file = '/Users/nmanaud/workspace/pdssp/pdssp-labtools/data/definitions/ias/catalog.yaml'

definitions = Definitions(yaml_file=root_catalog_definition_file)
# collection_definition_dict = definitions.parse_yaml_collection_file('./collection.yaml')
# collection_definition = definitions.create_collection_definition(collection_definition_dict, '')

# catalog_definition_dict = definitions.parse_yaml_catalog_file('./catalog.yaml')
# catalog_definition = definitions.create_catalog_definition(catalog_definition_dict, '')

collection_def = definitions.get_collection('mex_omega_global_maps_ddr')