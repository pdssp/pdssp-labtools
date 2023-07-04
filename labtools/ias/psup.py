import os
from contextlib import closing
# from urllib.request import urlretrieve
import requests
from pathlib import Path
import json
from pydantic import BaseModel
import shutil

import netCDF4

from labtools.schemas import factory

class PSUP_Collection(BaseModel):
    id: str
    schema_name: str
    n_products: int

def download_collection(collection_id, psup_url, metadata_schema, output_dir='source', overwrite=False):

    # set output source collection file name
    output_dir = Path(output_dir)
    basename = output_dir.stem
    source_collection_file = output_dir / f'{basename}.json'

    if source_collection_file.exists() and not overwrite:
        print(f'Output source collection file already exists: {source_collection_file!r}.')
        print()
        return source_collection_file

    # check connection and get the total number of products
    with closing(requests.get(psup_url, params=dict(limit=0))) as r:
        if r.ok:
            response = r.json()
            if 'total' in response.keys():
                n_products = response['total']
                max_n_products = 13000
                if n_products > max_n_products:
                    print(f'WARNING: Number of products higher than {max_n_products}: {n_products}')
            else:
                Exception('Invalid PSUP response: no "total" key found.')
        else:
            raise Exception(f'Invalid PSUP response.')

    with closing(requests.get(psup_url, params=dict(limit=n_products))) as r:
        if r.ok:
            response = r.json()
            if 'data' in response.keys():
                records = response['data']
            else:
                Exception('Invalid PSUP response: no "data" key found.')
        else:
            raise Exception(f'Invalid PSUP response.')

    # create output directory if does not exist
    Path.mkdir(output_dir, parents=True, exist_ok=True)

    # write source collection file, holding both collection and products metadata
    products_dict = {
        'collection': {
            'id': collection_id,
            'schema_name': metadata_schema,
            'n_products': n_products
        },
        'products': records
    }
    with open(source_collection_file, 'w') as f:
        json.dump(products_dict, f)

    return source_collection_file

def read_collection_metadata(source_collection_file):
    with open(source_collection_file, 'r') as f:
        json_dict = json.load(f)

    if 'collection' in json_dict.keys():
        collection_dict = json_dict['collection']
    else:
        raise Exception('Not a valid input PSUP source collection JSON file.')

    try:
        collection_metadata = PSUP_Collection(**collection_dict)
    except Exception as e:
        print(e)
        print(collection_dict)
        return None

    return collection_metadata


def read_products_metadata(source_collection_file):
    # retrieve metadata schema name
    collection_metadata = read_collection_metadata(source_collection_file)
    schema_name = collection_metadata.schema_name

    # read source collection file
    with open(source_collection_file, 'r') as f:
        json_dict = json.load(f)

    if 'products' in json_dict.keys():
        products_dicts = json_dict['products']
    else:
        raise Exception('Not a valid input PSUP source collection JSON file.')

    products = []
    for product_dict in products_dicts:
        try:
            product_metadata = factory.create_metadata_object(product_dict, schema_name, 'item')
            products.append(product_metadata)
        except Exception as e:
            print(e)
            print(product_dict)
            return

    return products


def download_data_files(source_collection_file, overwrite=False, n_max_items=None):
    products = read_products_metadata(source_collection_file)

    list_file = Path(source_collection_file).parent / 'list.txt'
    products_list = []
    if list_file.exists():
        with open(list_file) as f:
            products_list = [line.rstrip() for line in f]

    if products:
        if n_max_items:
            products = products[:n_max_items]
    else:
        print(f'No products found in {source_collection_file!r}.')
        return

    if not products:
        print(f'No products found in {source_collection_file!r}.')
        return

    for product_metadata in products:
        # schema_name = factory.get_schema_name(product_metadata)
        # transformer = transformer.create_transformer(schema_name)
        # # transformer = transformer.create_transformer(product_metadata)
        # url = transformer.get_download_link(product_metadata)
        url = product_metadata.get_download_url()

        product_fname = url.split('/')[-1]

        # set ouput data directory
        data_dir = Path(source_collection_file).parent / 'data'

        # create data directory if does not exist
        if not data_dir.exists():
            # shutil.rmtree(data_dir)\
            data_dir.mkdir()

        product_path = data_dir / product_fname
        if not product_path.exists() or overwrite:
            if not products_list:
                products_to_download = [product_fname]
            else:
                products_to_download = products_list
            if product_fname in products_to_download:
                print(f'Downloading from {url} ({product_metadata.nc_human_file_size:<10}) to {product_path} ...')
                try:
                    # urlretrieve(url, product_path)
                    r = requests.get(url, allow_redirects=True)
                    if r.status_code != 200:
                        raise ConnectionError(f'could not download {url}\nerror code: {r.status_code}')
                    product_path.write_bytes(r.content)

                    size_str = f"{os.stat(product_path).st_size / (1014*1024):.1f}"
                    print(f'DONE ({size_str} MB)')
                    print()
                except Exception as e:
                    print('ERROR')
                    print(e)
                    # os.remove(product_path)
                    # print(f'Removed {product_path} file.')
                    print()
        else:
            # check that NetCDF file is readable
            try:
                r = netCDF4.Dataset(product_path, 'r')
                r.close()
            except:
                print(f'WARNING: {product_path} not a readable NetCDF file.')
                # os.remove(product_path)
                # if not product_path.exists():
                #     print(f'Removed {product_path} file.')
                # print('EXISTS')
                # print()
