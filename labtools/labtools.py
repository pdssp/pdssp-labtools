from definitions import Definitions

def download_data():
    pass

def build_index():
    pass

def build_catalog():
    pass

if __name__ == '__main__':  # sys.argv
    print("PDSSP Labtools")

    definitions = Definitions(yaml_file='/Users/nmanaud/workspace/pdssp/pdssp-labtools/data/definitions/ias/catalog.yaml')

    catalog = definitions.catalogs[0]
    print(f'{catalog.id}/ (root)')
    for subcatalog_id in catalog.catalogs:
        subcatalog = definitions.get_catalog(subcatalog_id)
        print(f'  {subcatalog_id}/')
        for collection_id in subcatalog.collections:
            print(f'    - {collection_id}')




