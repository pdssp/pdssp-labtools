import click

from pathlib import Path

from .definitions import Definitions
import labtools.loader as loader
from .builder import build_catalog
from .ias import psup
from labtools.schemas import factory as metadata_factory

SOURCE_DATA_DIR = '/Volumes/Data/pdssp/psup/source'
YAML_DEFINITIONS_FILE = '/Users/nmanaud/workspace/pdssp/pdssp-labtools/data/definitions/ias/catalog.yaml'
STAC_DATA_DIR = '/Volumes/Data/pdssp/psup/stac'
N_MAX_ITEMS = 100  # maximum number of items to process per collection

loader.load_schemas([
    'labtools.schemas.pdssp_stac',
])
loader.load_schemas([
    'labtools.ias.schemas.omega_c_proj',
    'labtools.ias.schemas.omega_cube',
    'labtools.ias.schemas.omega_map',
    'labtools.ias.schemas.vector_features'
])


@click.group()
def cli():
    """PDSSP Labtools CLI."""
    pass


@cli.command()
def config():
    """Returns configuration parameters."""
    print(f'SOURCE_DATA_DIR       = {SOURCE_DATA_DIR}')
    print(f'YAML_DEFINITIONS_FILE = {YAML_DEFINITIONS_FILE}')
    print(f'STAC_DATA_DIR         = {STAC_DATA_DIR}')
    print(f'N_MAX_ITEMS           = {N_MAX_ITEMS}')
    print()


@cli.command()
def definitions():
    """Returns defined source collections."""
    definitions = Definitions(yaml_file=YAML_DEFINITIONS_FILE)
    collections_ids = definitions.get_collections_ids()
    source_collections_files = []
    for collection_id in collections_ids:
        urn_collection_id = collection_id  # f'urn:pdssp:ias:collection:{collection_id}'  # temporary patch
        collection_definition = definitions.get_collection(urn_collection_id)
        source_collection_file = Path(SOURCE_DATA_DIR) / collection_definition.get_source_collection_file()
        source_collections_files.append(source_collection_file)
        print(f'{collection_definition.id:<52} {source_collection_file}')
    print()

@cli.command()
@click.argument('collections-ids')
@click.option('--n-max-items', type=click.INT, help='Maximum number of items to process per collection.', default=-1)
@click.option('--overwrite/--no-overwrite', help='Overwrite existing data files.', default=False)
def download(collections_ids, n_max_items, overwrite):
    """Download defined source collections.

    Examples:
        $ labtools download all
        $ labtools download mex_omega_cubes_rdr,features_datasets
        $ labtools download all --overwrite --n-max-items=-1
    """
    # set collections IDS to download
    definitions = Definitions(yaml_file=YAML_DEFINITIONS_FILE)
    collections_ids = collections_ids.split(',')
    if len(collections_ids) == 1:
        if collections_ids[0] == 'all':  # download all defined source collections
            collections_ids = definitions.get_collections_ids()
            for i, collections_id in enumerate(collections_ids):  # PATCH removing urn tokens
                collections_ids[i] = collections_id.split(':')[-1]

    for collection_id in collections_ids:
        collection_id = collection_id.strip()  # remove whitespaces
        urn_collection_id = f'urn:pdssp:ias:collection:{collection_id}'  # temporary patch
        collection_definition = definitions.get_collection(urn_collection_id)
        url = collection_definition.source.url
        metadata_schema = collection_definition.source.metadata_schema
        target = collection_definition.ssys_targets[0].lower()
        source_collections_dir = Path(SOURCE_DATA_DIR) / collection_definition.path / collection_id

        print(f'Download `{collection_id}` collection from `{url}` to `{source_collections_dir}`.')
        if n_max_items == -1:
            n_max_items = None

        source_collection_file = psup.download_collection(collection_id, url, metadata_schema, output_dir=source_collections_dir, overwrite=overwrite)
        if source_collection_file:
            psup.download_data_files(source_collection_file, overwrite=overwrite, n_max_items=n_max_items)
        print(source_collection_file)
        print()


@cli.command()
@click.argument('collections-ids')
@click.option('--item-start', type=click.INT, help='Item start index.', default=0)
@click.option('--n-max-items', type=click.INT, help='Maximum number of items to process per collection.', default=N_MAX_ITEMS)
def build(collections_ids, item_start, n_max_items):
    """Build STAC catalog.

    Examples:
        $ labtools build all
        $ labtools build mex_omega_cubes_rdr,features_datasets
        $ labtools build all --n-max-items=10
        $ labtools build all --n-max-items=-1
        $ labtools build mex_omega_cubes_rdr --item-start=8921 --n-max-items=1
    """
    # set collections IDs to include in STAC catalog
    definitions = Definitions(yaml_file=YAML_DEFINITIONS_FILE)
    collections_ids = collections_ids.split(',')
    if len(collections_ids) == 1:
        if collections_ids[0] == 'all':  # download all defined source collections
            collections_ids = definitions.get_collections_ids()
            for i, collections_id in enumerate(collections_ids):  # PATCH removing urn tokens
                collections_ids[i] = collections_id.split(':')[-1]

    # derive source collections files
    source_collections_files = []
    for collection_id in collections_ids:
        urn_collection_id = f'urn:pdssp:ias:collection:{collection_id}'  # temporary patch
        collection_definition = definitions.get_collection(urn_collection_id)
        source_collection_file = Path(SOURCE_DATA_DIR) / collection_definition.get_source_collection_file()
        source_collections_files.append(source_collection_file)
        print(f'{collection_definition.id:<52} {source_collection_file}')

    # build catalog
    if n_max_items == -1:
        n_max_items = None
    build_catalog(definitions, source_collections_files, stac_dir=STAC_DATA_DIR, item_start=item_start, n_max_items=n_max_items)


if __name__ == '__main__':
    cli()