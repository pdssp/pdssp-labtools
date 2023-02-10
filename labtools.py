"""STAC catalog generator module for IAS data products collections.
"""
# TODO: Must be generalised to all IDOC Mars/OMEGA collections

from pathlib import Path
import netCDF4
import numpy as np
from geojson import Polygon
import pystac
from datetime import datetime
import requests
from contextlib import closing
from urllib.request import urlretrieve
import shutil

from pystac.extensions.scientific import ScientificExtension

INPUT_DATA_DIR = '/Users/nmanaud/workspace/pdssp/idoc_data'
OUTPUT_STAC_DIR = './catalogs'

def load_colletion_index(collection_id):
    """Returns the list of records (products) given a PSUP collection ID.
    """
    records =[]
    psup_url = ''
    if collection_id == 'omega_c_channel_proj':
        psup_url = 'http://psup.ias.u-psud.fr/ds/omega_c_channel/records'
    else:
        print(f'Invalid input collection ID: {collection_id}')
        return None

    # check connection and get the total number of products
    with closing(requests.get(psup_url, params=dict(limit=0))) as r:
        if r.ok:
            response = r.json()
            if 'total' in response.keys():
                n_products = response['total']
                max_n_products = 10000
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

    for record in records:
        # update record with product id, derived from data download path
        # remove 'uri' property (useless in the future)
        product_id = Path(record['download_nc']).stem
        if product_id:
            record['id'] = product_id
        record.pop('uri')

    return records


def omega_c_channel_proj_footprint(netcdf_path) -> Polygon:
    """Returns the GeoJSON Geometry of a OMEGA_C_Channel_Proj NetCDF data product.
    """
    try:
        nc_dataset = netCDF4.Dataset(netcdf_path, 'r')
    except Exception as e:
        print(e)
        print(f'Unable to read NetCDF data product: {netcdf_path}')
        return None
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
        # if bottom_pt[1] < last_poly_pt[1]: error ??
        if left_pt[1] < last_poly_pt[1]:
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
    try:
        nc_dataset = netCDF4.Dataset(netcdf_path, 'r')
        # derive i,e,phase angles from data product
        incidence_angle = float(np.mean(nc_dataset['incidence_n']).data)
        emission_angle = None
        phase_angle = None
        return {
            'id': Path(netcdf_path).stem,
            'stac_extensions': ['ssys', 'processing'],
            'bbox': None,
            'datetime': datetime.fromisoformat(nc_dataset.variables['start_time'].getValue()),
            'title': nc_dataset.title,
            'properties': {
                'mean_tau': None,
                'mean_watericelin': None,
                'mean_icecloudindex': None,
                'ssys:targets': ['Mars'],
                'ssys:incidence_angle': incidence_angle,
                'ssys:emission_angle': emission_angle,
                'ssys:phase_angle': phase_angle,
                'processing:level': 'L3'
            },
            'collection': 'omega_c_channel_proj'
        }
    except Exception as e:
        print(e)
        print(f'Unable to read NetCDF data product: {netcdf_path}')
        return None


def genstac(collection_index, output_stac_dir='catalogs', overwrite=False):
    """Generate a STAC catalog from input data products collection index (dict).
    """
    collection_id = 'omega_c_channel_proj'
    output_stac_dir = Path(output_stac_dir) / collection_id
    if output_stac_dir.exists():
        if overwrite: # remove output STAC directory
            shutil.rmtree(output_stac_dir)
        else:
            print(f'Output STAC directory already exists. Use `overwrite=True`.')
            return

    # default root catalog
    catalog_dict = {
        'id': 'pdssp-lab-catalog',
        'title': 'PDSSP Lab STAC Catalog',
        'description': 'Root catalog containing one STAC collection, to be published via OGC WFS or Features API service.',
        'stac_extensions': ['ssys'],
        'ssys:target': ['Mars']
    }

    collection_dict = {
        'id': 'omega_c_channel_prj',
        'stac_extensions': ['ssys', 'processing', 'sci'],
        'title': 'OMEGA C-channel map-projected observations data cubes.',
        'description': (
            'These data cubes have been specifically selected and filtered for '
            'studies of the surface mineralogy between 1 and 2.5 microns.\n'
            'They contain all the OMEGA observations acquired with the C channel '
            'after filtering. Filtering processes have been implemented to remove '
            'some instrumental artefacts and observational conditions. Each OMEGA '
            'record is available as a netCDF4.nc file and an idl.sav\n',
            'Both files contain the cubes of reflectance of the surface at a given '
            'longitude, latitude and wavelength. The reflectance is defined by the '
            '"reflectance factor" I(lambda)/(F cos(i)) where lambda is the solar incidence angle '
            'with lambda from 0.97 to 2.55 microns (second dimension of the cube with 120 '
            'wavelengths). The spectra are corrected for atmospheric and aerosol '
            'contributions according to the method described in Vincendon et al. '
            '(Icarus, 251, 2015). It therefore corresponds to albedo for a lambertian '
            'surface. The first dimension of the cube refers to the length of scan. It '
            'can be 32, 64, or 128 pixels. It gives the first spatial dimension. The '
            'third dimension refers to the rank of the scan. It is the second spatial '
            'dimension.'
        ),
        'providers': [
            {
                'name': "Institut d'Astrophysique Spatiale (IAS) - IDOC",
                'description': "The Integrated Data and Operation Center (IDOC) is responsible for processing, "
                               "archiving and distributing data from space science missions in which the institute "
                               "is involved.",
                'roles': ['producer', 'processor', 'host'],
                'url': 'https://idoc.ias.universite-paris-saclay.fr',
                "processing:level": "L3",
            }
        ],
        'sci:publications': [
            {
                'doi': '',
                'citation': 'Vincendon M., Audouard J., Altieri F., Ody A., Mars Express measurements of surface albedo  '
                            'changes over 2004–2010, In Icarus, Volume 251, 2015, Pages 145-163, ISSN 0019-1035'
            },
            {
                'doi': 'doi:10.1002/2014JE004649',
                'citation': 'Audouard, J., F. Poulet, M. Vincendon, R. E. Milliken, D. Jouglet, J. Bibring, B. Gondet, '
                            'and Y. Langevin (2014), Water in the Martian regolith from OMEGA/Mars Express, J. Geophys. '
                            'Res. Planets,119, 1969–1989'
            },
            {
                'doi': 'doi:10.1029/2006JE002841',
                'citation': 'Langevin, Y., J.-P. Bibring, F. Montmessin, F. Forget, M. Vincendon, S. Douté, F. Poulet, '
                            'and B. Gondet (2007), Observations of the south seasonal cap of Mars during recession in '
                            '2004–2006 by the OMEGA visible/near-infrared imaging spectrometer on board Mars Express, '
                            'J. Geophys. Res., 112, E08S12.'
            },
            {
                'doi': '',
                'citation': "Bibring et al (2004), OMEGA: Observatoire pour la Mineralogie, l'Eau, les Glaces et "
                            "l'Activité, In: Mars Express: the scientific payload. ESA SP-1240, Noordwijk,"
                            "Netherlands:ESA Publications Division, ISBN 92-9092-556-6, p. 37-49"
            }
        ],
        'keywords': ['surface mineralogy'],
        'license': 'CC-BY-4.0',
        'ssys:targets': ['Mars']
    }

    stac_catalog = pystac.Catalog(
        id=catalog_dict['id'],
        title=catalog_dict['title'],
        description=catalog_dict['description'],
        stac_extensions=catalog_dict['stac_extensions'],
        extra_fields={'ssys:targets': catalog_dict['ssys:target']}
    )

    # create collection STAC object

    providers = []
    for provider_dict in collection_dict['providers']:
        provider = pystac.provider.Provider(
            name=provider_dict['name'],
            description=provider_dict['description'],
            roles=provider_dict['roles'],
            url=provider_dict['url'],
            extra_fields={
                'processing:level': provider_dict['processing:level']
            }
        )
        providers.append(provider)

    stac_collection = pystac.Collection(
        id=collection_dict['id'],
        stac_extensions=collection_dict['stac_extensions'],
        title=collection_dict['title'],
        description=collection_dict['description'],
        providers=providers,
        keywords=collection_dict['keywords'],
        extent=pystac.Extent(pystac.SpatialExtent(bboxes=[[]]), pystac.TemporalExtent(intervals=[[]])),
        license=collection_dict['license'],
        extra_fields={
            'ssys:targets': collection_dict['ssys:targets'],
        }
    )

    # add STAC Scientific Extension
    sci_ext = ScientificExtension.ext(stac_collection, add_if_missing=True)
    publications = []
    for publication_dict in collection_dict['sci:publications']:
        publication = pystac.extensions.scientific.Publication(
            doi=publication_dict['doi'],
            citation=publication_dict['citation']
        )
        publications.append(publication)
    sci_ext.publications = publications


    # write STAC item
    for product in collection_index:
        data_file = product['local_path']
        if data_file != '' and Path(data_file).exists():
            # retrieve metadata from data product file
            item_metadata = omega_c_channel_proj_metadata(data_file)
            if not item_metadata:
                continue
            bbox = [
                (float(product['westernmost_longitude']) + 180.0) % 360.0 - 180.0,
                float(product['minimum_latitude']),
                (float(product['easternmost_longitude']) + 180.0) % 360.0 - 180.0,
                float(product['maximum_latitude'])
            ]

            # add properties derived from data file
            product_props = product
            for key in item_metadata['properties'].keys():
                product_props.update({key: item_metadata['properties'][key]})

            stac_item = pystac.Item(
                id=item_metadata['id'],
                stac_extensions=item_metadata['stac_extensions'],
                geometry=omega_c_channel_proj_footprint(data_file),
                bbox=bbox,
                datetime=item_metadata['datetime'],
                properties=product_props,
                collection=item_metadata['collection']
            )
            stac_item.add_asset(
                key='nc_data_file',
                asset=pystac.Asset(
                    href=product['download_nc'],
                    title=item_metadata['title'],
                    description='NetCDF4 data file',
                    media_type='application/netcdf',
                    roles=['data']
                )
            )
            stac_item.add_asset(
                key='sav_data_file',
                asset=pystac.Asset(
                    href=product['download_sav'],
                    title=item_metadata['title'],
                    description='IDL SAV data file',
                    media_type='application/octet-stream',
                    roles=['data']
                )
            )
            stac_collection.add_item(stac_item)
            print(f'{stac_item} added to STAC collection.')

    # update collection extent and add to catalog
    stac_collection.update_extent_from_items()
    stac_catalog.add_child(stac_collection)

    # save catalog
    stac_catalog.normalize_hrefs(str(output_stac_dir))
    stac_catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)
    print(f'STAC catalog created in {output_stac_dir}')


def process_collection(collection_id, download=True, overwrite=False):
    # set input data dir
    collection_data_dir = Path(INPUT_DATA_DIR) / 'mars' / collection_id
    if not collection_data_dir.exists():
        print(f'ERROR: Input data collection directory not found: {collection_data_dir}')

    # load collection index from PSUP web service
    collection_index = load_colletion_index(collection_id)

    # update collection index with product local path
    for i, product in enumerate(collection_index):
        product_fname = f'{product["id"]}.nc'
        product_path = collection_data_dir / product_fname
        if not product_path.exists():
            if download:
                # download data file
                print(f'Downloading {product_fname} ({product["nc_human_file_size"]}) ...', end = '')
                try:
                    urlretrieve(product['download_nc'], product_path)
                    print('OK')
                except Exception as e:
                    product_path = ''
                    print('ERROR')
                    print(e)
            else:
                product_path = ''
                print(f'{product_fname} does not exist locally. Not downloaded.')
        # add local path
        product['local_path'] = str(product_path)
        # collection_index[i]['local_path'] = str(product_path)

    # generate STAC catalog
    genstac(collection_index, overwrite=overwrite)


if __name__ == '__main__':  # sys.argv
    # set collection ID / directory to process
    collection_id = 'omega_c_channel_proj'
    process_collection(collection_id, download=False, overwrite=True)
