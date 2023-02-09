"""STAC catalog generator module for IAS data products collections.
"""

from pathlib import Path
import netCDF4
import numpy as np
from geojson import Polygon
import pystac
from datetime import datetime
import requests
from contextlib import closing
# from tqdm import tqdm
from urllib.request import urlretrieve

INPUT_DATA_DIR = '/Users/nmanaud/workspace/pdssp/idoc_data'
OUTPUT_STAC_DIR = './catalogs'


def omega_c_channel_proj_footprint(netcdf_path) -> Polygon:
    """Returns the GeoJSON Geometry of a OMEGA_C_Channel_Proj NetCDF data product.
    """
    nc_dataset = netCDF4.Dataset(netcdf_path, 'r')
    alt = nc_dataset.variables['altitude']
    latitudes = nc_dataset.variables['latitude']
    longitudes = nc_dataset.variables['longitude']

    top_pts = []
    right_pts = []
    bottom_pts = []
    left_pts = []

    for i in range(alt.shape[0]):
        m = np.where(alt[i,:].mask == False)
        if len(m[0]) > 0:
            top_pts.append((i,m[0][0]))
            bottom_pts.append((i,m[0][-1]))

    for j in range(alt.shape[1]):
        m = np.where(alt[:, j].mask == False)
        if len(m[0]) > 0:
            left_pts.append((m[0][0], j))
            right_pts.append((m[0][-1], j))

    bottom_pts.reverse()
    left_pts.reverse()

    poly_pts = []
    for top_pt in top_pts:
        poly_pts.append(top_pt)
    last_poly_pt = poly_pts[-1]
    for right_pt in right_pts:
        if right_pt[1] > last_poly_pt[1]:
            if right_pt not in top_pts:
                poly_pts.append(right_pt)
    last_poly_pt = poly_pts[-1]
    for bottom_pt in bottom_pts:
        if bottom_pt[0] < last_poly_pt[0]:
            if bottom_pt not in right_pts:
                poly_pts.append(bottom_pt)
    last_poly_pt = poly_pts[-1]
    for left_pt in left_pts:
        if bottom_pt[1] < last_poly_pt[1]:
            if (left_pt not in bottom_pts) and (left_pt not in top_pts):  # top_pts
                poly_pts.append(left_pt)

    poly_geopts = []  # (lon, lat)
    for poly_pt in poly_pts:
        lon = float(longitudes[poly_pt[1]].data)
        lat = float(latitudes[poly_pt[0]].data)
        poly_geopts.append((lon,lat))
    poly_geopts.append(poly_geopts[0])  # close polygon

    return Polygon([poly_geopts])


def omega_c_channel_proj_metadata(netcdf_path):
    nc_dataset = netCDF4.Dataset(netcdf_path, 'r')
    return {
        'id': Path(netcdf_path).stem,
        'stac_extensions': ['ssys'],
        'bbox': None,
        'datetime': datetime.fromisoformat(nc_dataset.variables['start_time'].getValue()),
        'properties': {},
        'collection': 'omega-c-channel-proj',
        'ssys:targets': ['Mars']
    }

def load_colletion_index(collection_id):
    """Returns"""
    records =[]
    psup_url = ''
    if collection_id == 'omega_c_channel_proj':
        psup_url = 'http://psup.ias.u-psud.fr/ds/omega_c_channel/records'

    with closing(requests.get(psup_url)) as r:
        if r.ok:
            response = r.json()
            if 'data' in response.keys():
                records = response['data']
            else:
                Exception('Invalid PSUP response: no "data" key found.')
        else:
            raise Exception(f'Invalid PSUP response.')

    for record in records:
        # update record with product id, derived from data download path
        product_id = Path(record['download_nc']).stem
        if product_id:
            record['id'] = product_id

    return records

# def download_data(url, path):
#     response = requests.get(url, stream=True)
#     from urllib.request import urlretrieve
#     urlretrieve
#     with open(path, "wb") as handle:
#         for data in tqdm(response.iter_content()):
#             handle.write(data)

# def genstac(input_data_dir, output_stac_dir='catalogs'):
def genstac(collection_index, output_stac_dir='catalogs'):
    """Generate a STAC catalog containing one collection, associated to input data directory.
    """
    # Data files to be processed can come from an index file, or resulting from a glob search
    # for NetCDF data products.
    # TODO: must be generalised later to all OMEGA collections
    # print('>',input_data_dir)
    # data_files = list(Path(input_data_dir).glob('**/*.nc'))
    # print(data_files)

    catalog_dict = {
        'id': 'pdssp-lab-catalog',
        'title': 'PDSSP Lab STAC Catalog',
        'description': '',
        'stac_extensions': ['ssys'],
        'ssys:target': ['Mars']
    }

    collection_dict = {
        'id': 'omega_c_channel_proj',
        'stac_extensions': ['ssys'],
        'title': 'OMEGA observations acquired with the C channels, projected',
        'description': 'These data cubes have been specifically selected and filtered for'
                       ' studies of the surface mineralogy between 1 and 2.5 microns.',
        'license': 'Licence TBD',
        'ssys:targets': ['Mars']
    }

    stac_catalog = pystac.Catalog(
        id=catalog_dict['id'],
        title=catalog_dict['title'],
        description=catalog_dict['description'],
        stac_extensions=catalog_dict['stac_extensions'],
        extra_fields={'ssys:targets': catalog_dict['ssys:target']}
    )

    stac_collection = pystac.Collection(
        id=collection_dict['id'],
        stac_extensions=collection_dict['stac_extensions'],
        title=collection_dict['title'],
        description=collection_dict['description'],
        extent=pystac.Extent(pystac.SpatialExtent(bboxes=[[]]), pystac.TemporalExtent(intervals=[[]])),
        license=collection_dict['license'],
        extra_fields={'ssys:targets': collection_dict['ssys:targets']}
    )

    # write STAC item
    for product in collection_index:
        data_file = product['local_path']
        item_metadata = omega_c_channel_proj_metadata(data_file)
        bbox = [
            (float(product['westernmost_longitude'])+ 180.0) % 360.0 - 180.0,
            float(product['minimum_latitude']),
            (float(product['easternmost_longitude'])+ 180.0) % 360.0 - 180.0,
            float(product['maximum_latitude'])
        ]
        stac_item = pystac.Item(
            id=item_metadata['id'],
            stac_extensions=item_metadata['stac_extensions'],
            geometry=omega_c_channel_proj_footprint(data_file),
            bbox=bbox,
            datetime=item_metadata['datetime'],
            properties=product,  # item_metadata['properties'],
            extra_fields={'ssys:targets': item_metadata['ssys:targets']},
            collection=item_metadata['collection']
        )
        print(stac_item)
        stac_collection.add_item(stac_item)

    # update collection extent and add to catalog
    stac_collection.update_extent_from_items()
    stac_catalog.add_child(stac_collection)

    # save catalog
    output_stac_dir = str(Path(output_stac_dir) / collection_dict['id'])
    print(output_stac_dir)
    stac_catalog.normalize_hrefs(output_stac_dir)
    stac_catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)

if __name__ == '__main__':
    # if '-f' in sys.argv[1:]:
    #     force = True
    # else:
    #     force = False

    # set collection ID / directory to process
    collection_id = 'omega_c_channel_proj'
    #
    collection_data_dir = Path(INPUT_DATA_DIR) / 'mars' / collection_id
    # if not collection_data_dir.exists():
    #     print(f'ERROR: Input data collection directory not found: {collection_data_dir}')
    # else:
    #     genstac(str(collection_data_dir))

    collection_index = load_colletion_index(collection_id)
    collection_index = collection_index[100:102]  # limit number of products to process
    for product in collection_index:
        product_fname =  f'{product["id"]}.nc'
        product_path = collection_data_dir / product_fname
        if not product_path.exists():
            # download data file
            print(f'Downloading {product_fname} ({product["nc_human_file_size"]}) ...')
            urlretrieve(product['download_nc'], product_path)
        product['local_path'] = str(product_path)

    # print(collection_index[0])
    genstac(collection_index)

    pass