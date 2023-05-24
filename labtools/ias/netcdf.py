from typing import Any, Dict, List, Union, Optional
from pathlib import Path

import netCDF4
import numpy as np
import json
import geojson
from geojson import Polygon
from datetime import datetime

from labtools.utils import utc_to_iso

def get_netcdf_footprint(netcdf_file) -> Optional[Dict[str, Any]]:
    """Returns the GeoJSON Geometry of a OMEGA_C_Channel_Proj NetCDF data product.
    """
    try:
        nc_dataset = netCDF4.Dataset(netcdf_file, 'r')
    except Exception as e:
        print(e)
        print(f'Unable to read NetCDF data product: {netcdf_file}')
        return None
    alt = nc_dataset.variables['altitude']
    latitudes = nc_dataset.variables['latitude']
    longitudes = nc_dataset.variables['longitude']

    top_pts = []
    right_pts = []
    bottom_pts = []
    left_pts = []
    for i in range(alt.shape[0]):
        m = np.where(alt[i, :].mask == False)
        if len(m[0]) > 0:
            top_pts.append((i, m[0][0]))
            bottom_pts.append((i, m[0][-1]))

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
        poly_geopts.append((lon, lat))
    poly_geopts.append(poly_geopts[0])  # close polygon

    geometry = json.loads(geojson.dumps(Polygon([poly_geopts])))

    return geometry


def get_netcdf_properties(netcdf_file, schema_name):
    """Returns a selection of metadata derived from a OMEGA_C_Channel_Proj NetCDF data product.
    """
    if schema_name == 'OMEGA_C_PROJ':
        try:
            nc_dataset = netCDF4.Dataset(netcdf_file, 'r')
            # derive i,e,phase angles from data product
            incidence_angle = float(np.mean(nc_dataset['incidence_n']).data)
            mean_tau = float(np.mean(nc_dataset['tau']).data)
            mean_tau = mean_tau if not np.isnan(mean_tau) else None
            mean_watericelin = float(np.mean(nc_dataset['watericelin']).data)
            mean_watericelin = mean_watericelin if not np.isnan(mean_watericelin) else None
            mean_icecloudindex = float(np.mean(nc_dataset['icecloudindex']).data)
            mean_icecloudindex = mean_icecloudindex if not np.isnan(mean_icecloudindex) else None
            return {
                # 'title': nc_dataset.title,
                # 'created': nc_dataset.history  # TODO: parse 'Created 28/03/18'
                'mean_tau': mean_tau, # float(np.mean(nc_dataset['tau']).data),
                'mean_watericelin': mean_watericelin,  # float(np.mean(nc_dataset['watericelin']).data),
                'mean_icecloudindex': mean_icecloudindex,  # float(np.mean(nc_dataset['icecloudindex']).data),
                'incidence_angle': incidence_angle
            }
        except Exception as e:
            print(e)
            print(f'Unable to read NetCDF data product: {netcdf_file}')
            return {}
    elif schema_name == 'OMEGA_CUBE':
        # ATTENTION: Currently assuming that a OMEGA_C_PROJ NetCDF file is read so as to retrieve start and stop times
        # mission in OMEGA_CUBE NetCDF files.
        try:
            nc_dataset = netCDF4.Dataset(netcdf_file, 'r')
            # derive i,e,phase angles from data product
            incidence_angle = float(np.mean(nc_dataset['incidence_n']).data)
            mean_tau = float(np.mean(nc_dataset['tau']).data)
            mean_tau = mean_tau if not np.isnan(mean_tau) else None
            mean_watericelin = float(np.mean(nc_dataset['watericelin']).data)
            mean_watericelin = mean_watericelin if not np.isnan(mean_watericelin) else None
            mean_icecloudindex = float(np.mean(nc_dataset['icecloudindex']).data)
            mean_icecloudindex = mean_icecloudindex if not np.isnan(mean_icecloudindex) else None
            return {
                'datetime': utc_to_iso(nc_dataset.variables['start_time'].getValue(), timespec='milliseconds'),
                'start_time': utc_to_iso(nc_dataset.variables['start_time'].getValue(), timespec='milliseconds'),
                'end_time': utc_to_iso(nc_dataset.variables['stop_time'].getValue(), timespec='milliseconds'),
                'mean_tau': mean_tau, # float(np.mean(nc_dataset['tau']).data),
                'mean_watericelin': mean_watericelin,  # float(np.mean(nc_dataset['watericelin']).data),
                'mean_icecloudindex': mean_icecloudindex,  # float(np.mean(nc_dataset['icecloudindex']).data),
                'incidence_angle': incidence_angle
            }
        except Exception as e:
            print(e)
            print(f'Unable to read NetCDF data product: {netcdf_file}')
            return {}
    else:
        raise Exception(f'Unknown schema name: {schema_name}')