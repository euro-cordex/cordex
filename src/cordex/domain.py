# -*- coding: utf-8 -*-
# flake8: noqa
"""Domain module

This module defines preconfigured CORDEX domain. The :class:`Domain` class
is a kind of wrapper for the :class:`Grid` class to connect a grid
with meta information and easy to use functions that work on the member grid.

Domains can either be defined statically in this module or read from a csv table
that should be defined in the :mod:`table`.

Example:

    To get a list of available implementations, create cordex domains, write
    them to netcdf with some dummy data, you can use ,e.g.,::

        from cordex import domain as dm

        for short_name in dm.domains():
            print('creating domain: {}'.format(short_name))
            domain = dm.domain(short_name)
            domain.to_netcdf(short_name+'.nc', dummy='topo')

"""

import numpy as np
import logging
from itertools import chain

import pandas as pd

import xarray as xr
from netCDF4 import Dataset

from . import grid as gd
from . import cf

from .tables.tables import CSV

from cordex import __version__

import pkg_resources
from . import tables

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def _read_table_from_csv(csv):
    csv_file = pkg_resources.resource_stream('cordex.tables', csv)
    return pd.read_csv(csv_file, index_col='short_name')

def _read_tables_from_csv():
    tables = {}
    for set_name, csv in CSV.items():
        tables[set_name] = _read_table_from_csv(csv)
    return tables


def _create_domains_from_table(table):
    domains = {}
    for short_name, row in table.iterrows():
        print(dict(row))
        domains[short_name] = Domain(short_name=short_name, **dict(row))
    return domains

def _create_domain_from_table(short_name, table):
    return Domain(short_name=short_name, **dict(table.loc[short_name]))

TABLES = _read_tables_from_csv()


class Domain():
    """The :class:`Domain` holds data and meta information of a Cordex Domain.
    """
    def __init__(self, nlon, nlat, dlon, dlat,
                 pollon, pollat, ll_lon, ll_lat, short_name=None,
                 long_name='', ncattrs=None, **kwargs):
        if short_name is None:
            self.short_name = 'NO NAME'
        else:
            self.short_name = short_name
        self.long_name = long_name
        self.nlon = nlon
        self.nlat = nlat
        self.dlon = dlon
        self.dlat = dlat
        self.dim_names   = ('rlon', 'rlat')
        self.coord_names = ('lon' , 'lat')
        self.grid_rotated = self._init_grid(nlon, nlat, dlon, dlat, ll_lon, \
                                   ll_lat, pollon, pollat)
        self.grid_lonlat  = self.grid_rotated.transform()
        if ncattrs is None:
            self.global_attrs = {}
        else:
            self.global_attrs = attrs

    @property
    def pollon(self):
        return self.grid_rotated.pole[0]

    @property
    def pollat(self):
        return self.grid_rotated.pole[1]

    def _init_grid(self, nlon, nlat, dlon, dlat, ll_lon, ll_lat, pollon, pollat):
        rlon = np.array([ll_lon+i*dlon for i in range(0,nlon)], dtype=np.float64)
        rlat = np.array([ll_lat+i*dlat for i in range(0,nlat)], dtype=np.float64)
        return gd.Grid(rlon, rlat, pollon, pollat)

    def extend(self, nlonl, nlatl=None, nlonr=None, nlatu=None, **kwargs):
        """Extend a Domain with a number of boundaray cells.

        Args:
          nlon (int): number of extensions in longitual direction.
          nlat (int): number of extensions in latitude direction (default nlat=nlon).

        Returns:
          Domain: Domain instance with extended boundaries.

        """
        boundary = self.grid_rotated.get_bounding_box()
        ll = boundary[0]
        print(ll)
        if nlatl is None: nlatl = nlonl
        if nlonr is None: nlonr = nlonl
        if nlatu is None: nlatu = nlatl
        ll_lon = ll[0] -  nlonl * self.dlon
        ll_lat = ll[1] -  nlatl * self.dlat
        return Domain(self.nlon+nlonl+nlonr, self.nlat+nlatl+nlatu, self.dlon, self.dlat,
                      self.pollon, self.pollat, ll_lon, ll_lat, **kwargs)


    def __str__(self):
        text = '\n----- Domain Object -----\n'
        text += '{:<15}    :   {}\n'.format('short_name', self.short_name)
        text += '{:<15}    :   {}\n'.format('long_name', self.long_name)
        text += '{:<15}    :   {}\n'.format('nlon', self.nlon)
        text += '{:<15}    :   {}\n'.format('nlat', self.nlat)
        text += str(self.grid_rotated)
        return text


    def get_global_attrs(self):
        attrs = self.global_attrs.copy()
        attrs.update({'CORDEX_domain': self.short_name})
        return attrs


    def _get_xarray_rotated(self, attrs=True):
        rlon, rlat   = self.grid_rotated.coordinates
        da_rlon = xr.DataArray(data=rlon[0],   dims=self.dimnames[0])
        da_rlat = xr.DataArray(data=rlat[:,0], dims=self.dimnames[1])
        if attrs:
            da_rlon.attrs = cf.coords['rlon']
            da_rlat.attrs = cf.coords['rlat']
        return da_rlon, da_rlat


    def _get_xarray_mapping(self, mapping_key):
        da_mapping = xr.DataArray(np.empty((), dtype=np.int32))
        attrs = cf.mapping[mapping_key].copy()
        attrs['grid_north_pole_longitude'] = self.grid_rotated.pole[0]
        attrs['grid_north_pole_latitude']  = self.grid_rotated.pole[1]
        da_mapping.attrs = attrs
        return da_mapping


    def _get_xarray_lonlat(self, attrs=True):
        lon, lat   = self.grid_lonlat.coordinates
        print(lon.shape)
        print(lat.shape)
        da_lon = xr.DataArray(data=lon, dims=tuple(reversed(self.dimnames)))
        da_lat = xr.DataArray(data=lat, dims=tuple(reversed(self.dimnames)))
        if attrs:
            da_lon.attrs = cf.coords['lon']
            da_lat.attrs = cf.coords['lat']
        return da_lon, da_lat


    def _get_xarray_dataset(self, grid='', attrs=True, **kwargs):
        coords       = {}
        global_attrs = {}
        data         = {}
        mapping_key  = list(cf.mapping.keys())[0]
        print(mapping_key)
        if not grid:
            coords['rlon'], coords['rlat'] = self.get_xarray_rotated(attrs)
            coords['lon'],  coords['lat']  = self.get_xarray_lonlat(attrs)
            data[mapping_key]              = self.get_xarray_mapping(mapping_key)
        elif grid == 'rotated':
            coords['rlon'], coords['rlat'] = self.get_xarray_rotated(attrs)
            data[mapping_key]              = self.get_xarray_mapping(mapping_key)
        elif grid == 'lonlat':
            coords['lon'],  coords['lat']  = self.get_xarray_lonlat(attrs)
        else:
            raise Exception('unknown grid description, should be \"rotated\" or \"latlon\".')
        ds = xr.Dataset(data, coords=coords)
        ds.update({'test': xr.DataArray(np.array((424, 412)), coords=coords)})
        # remove FillValue attribute
        for key, coord  in ds.coords.items():
            coord.encoding['_FillValue'] = False
        # add global attributes
        if attrs:
            ds.attrs = self.get_global_attrs()
        return ds


    def to_netcdf(self, filename, **kwargs):
        #self.get_xarray_dataset(grid).to_netcdf(filename, **kwargs)
        return self.get_dataset(filename, **kwargs).close()

    def get_dataset(self, filename, **kwargs):
        #self.get_xarray_dataset(grid).to_netcdf(filename, **kwargs)
        return _get_dataset(self, filename, **kwargs)



class _CFDataset():


    def __init__(self):
        pass


    def add_dimension(self):
        pass

    def add_coorindate(self):
        pass

    def get_dataset(self, grid='', attrs=True, **kwargs):
        return ds.squeeze(drop=True)



class _NC4Dataset(_CFDataset):

    def __init__(self):
        _CFDataset.__init__(self)
        self.ds = None

    def create(self, filename, mode=None, **kwargs):
        if mode is None:
            mode = 'w'
        self.ds = Dataset(filename, mode=mode, **kwargs)
        return self.ds

    def close(self):
        self.ds.close()

    def add_dimension(self, name, length):
        dim = self.ds.createDimension(name, length)
        return dim

    def add_data(self, name, data, **kwargs):
        var = self.ds.createVariable(name, **kwargs)
        var[:] = data
        return var

    def add_rlon_rlat(self, domain):
        x, y = domain.grid_rotated.coordinates
        x_name, y_name = domain.dim_names
        x = x[0]
        y = y[:,0]
        x_dim = self.add_dimension(x_name, len(x))
        x_dim = self.add_dimension(y_name, len(y))
        x_coord = self.add_data(x_name, x, datatype=np.float64, dimensions=(x_name))
        y_coord = self.add_data(y_name, y, datatype=np.float64, dimensions=(y_name))
        return x_coord, y_coord

    def add_lon_lat(self, domain):
        x, y = domain.grid_lonlat.coordinates
        x_name, y_name = domain.coord_names
        x_dim, y_dim   = domain.dim_names
        x_coord = self.add_data(x_name, x, datatype=np.float64, dimensions=(y_dim,x_dim))
        y_coord = self.add_data(y_name, y, datatype=np.float64, dimensions=(y_dim,x_dim))
        return x_coord, y_coord

    def add_pole(self, domain, mapping_name, mapping_attrs):
        self.add_data(mapping_name, data=np.empty(()), datatype=np.int32)
        mapping_attrs['grid_north_pole_longitude'] = domain.grid_rotated.pole[0]
        mapping_attrs['grid_north_pole_latitude']  = domain.grid_rotated.pole[1]
        self.ds.variables[mapping_name].setncatts(mapping_attrs)
        return self.ds


class _XrDataset(_CFDataset):

    def __init__(self):
        CFDataset.__init__(self)
        self.ds = None

    def create(self, filename, mode=None, **kwargs):
        if mode is None:
            mode = 'w'
        self.ds = Dataset(filename, mode=mode, **kwargs)
        return self.ds

    def close(self):
        self.ds.close()

    def add_dimension(self, name, length):
        dim = self.ds.createDimension(name, length)
        return dim

    def add_data(self, name, data, **kwargs):
        var = self.ds.createVariable(name, **kwargs)
        var[:] = data
        return var

    def add_pole(self, domain, mapping_name, mapping_attrs):
        self.add_data(mapping_name, data=np.empty(()), datatype=np.int32)
        mapping_attrs['grid_north_pole_longitude'] = domain.grid_rotated.pole[0]
        mapping_attrs['grid_north_pole_latitude']  = domain.grid_rotated.pole[1]
        self.ds.variables[mapping_name].setncatts(mapping_attrs)
        return self.ds

    def get_xarray_rotated(self, attrs=True):
        rlon, rlat   = self.grid_rotated.coordinates
        da_rlon = xr.DataArray(data=rlon[0],   dims=self.dimnames[0])
        da_rlat = xr.DataArray(data=rlat[:,0], dims=self.dimnames[1])
        if attrs:
            da_rlon.attrs = cf.coords['rlon']
            da_rlat.attrs = cf.coords['rlat']
        return da_rlon, da_rlat

    def get_xarray_mapping(self, mapping_key):
        da_mapping = xr.DataArray(np.empty((), dtype=np.int32))
        attrs = cf.mapping[mapping_key].copy()
        attrs['grid_north_pole_longitude'] = self.grid_rotated.pole[0]
        attrs['grid_north_pole_latitude']  = self.grid_rotated.pole[1]
        da_mapping.attrs = attrs
        return da_mapping

    def get_xarray_lonlat(self, attrs=True):
        lon, lat   = self.grid_lonlat.coordinates
        print(lon.shape)
        print(lat.shape)
        da_lon = xr.DataArray(data=lon, dims=tuple(reversed(self.dimnames)))
        da_lat = xr.DataArray(data=lat, dims=tuple(reversed(self.dimnames)))
        if attrs:
            da_lon.attrs = cf.coords['lon']
            da_lat.attrs = cf.coords['lat']
        return da_lon, da_lat


def _get_dataset(domain, filename='', dummy=None, mapping_name=None, attrs=True, **kwargs):
    return _get_dataset_nc4(domain, filename, dummy, mapping_name, attrs, **kwargs)


def _get_dataset_nc4(domain, filename='', dummy=None, mapping_name=None, attrs=True, **kwargs):
    if mapping_name is None:
        mapping_name = cf.DEFAULT_MAPPING_NCVAR
    ds = _NC4Dataset()
    ds.create(filename, **kwargs)
    ds.add_pole(domain, mapping_name, cf.mapping.copy())
    x_coord, y_coord = ds.add_rlon_rlat(domain)
    nx = x_coord.size
    ny = y_coord.size
    ds.add_lon_lat(domain)

    if attrs:
        for key, item in cf.coords.items():
            ds.ds.variables[key].setncatts(item)

    if dummy:
        if dummy is True:
            dummy_name = 'dummy'
        else:
            dummy_name = dummy
        dummy = ds.add_data(dummy_name, np.zeros((ny, nx)), datatype=np.float32, dimensions=('rlat','rlon'))
        dummy.setncattr('grid_mapping', mapping_name)
        dummy.setncattr('coordinates', 'lon lat')
        if dummy_name == 'topo':
            from cdo import Cdo
            cdo = Cdo()
            ds.ds.close()
            topo = cdo.topo(filename, returnCdf=True).variables['topo'][:]
            ds.ds = Dataset(filename, mode='a')
            ds.ds.variables['topo'][:] = topo
    return ds.ds



def _get_dataset_xr(domain, filename='', dummy=None, mapping_name=None, attrs=True):
    if mapping_name is None:
        mapping_name = cf.DEFAULT_MAPPING_NCVAR
    coords       = {}
    global_attrs = {}
    data         = {}
    coords['rlon'], coords['rlat'] = self.get_xarray_rotated(attrs)
    coords['lon'],  coords['lat']  = self.get_xarray_lonlat(attrs)
    data[mapping_key]              = self.get_xarray_mapping(mapping_key)
    ds = xr.Dataset(data, coords=coords)
    ds.update({'test': xr.DataArray(np.array((424, 412)), coords=coords)})
    # remove FillValue attribute
    for key, coord  in ds.coords.items():
        coord.encoding['_FillValue'] = False
    # add global attributes
    if attrs:
        ds.attrs = self.get_global_attrs()
    return ds


# euro-cordex domains now read from csv
##class EUR_44(Domain):
##    """Defines the EUR-44 rotated Domain.
##    """
##    def __init__(self):
##        Domain.__init__(self, 106, 103, 0.44, 0.44,
##            -162.0, 39.25, -28.21, -23.21, short_name='EUR-44')
##
##
##class EUR_11(Domain):
##    """Defines the EUR-11 rotated Domain.
##    """
##    def __init__(self):
##        Domain.__init__(self, 424, 412, 0.11, 0.11,
##            -162.0, 39.25, -28.375, -23.375, short_name='EUR-11')



class _DomainFactory(object):
    """Factory class for creating a domain instance.
    """

    @classmethod
    def static_domains(cls):
        """Returns a list of instances of static domains.
        """
        #return [EUR_44(), EUR_11()]
        return []

    @classmethod
    def names_from_static_domains(cls):
        """Returns a list of names of static domains.
        """
        return [domain.short_name for domain in cls.static_domains()]

    @classmethod
    def names_from_csv(cls, table=None):
        """Returns a list of names of csv domains.
        """
        if table:
            return list(TABLES[table].index.values)
        else:
            return list(chain.from_iterable([[sn for sn in t.index.values] for n,t in TABLES.items()]))

    @classmethod
    def create_domain_from_table(cls, short_name):
        """Returns a list of names of csv domains.
        """
        for table_name,table in TABLES.items():
            if short_name in table.index.values:
                return _create_domain_from_table(short_name, table)

    @classmethod
    def names(cls, table=None):
        """Returns a list of names of available Domains.
        """
        if table:
            return cls.names_from_csv(table)
        else:
            return cls.names_from_static_domains() + cls.names_from_csv()

    @classmethod
    def get_static_domain(cls, short_name):
        for domain in cls.static_domains():
            if short_name == domain.short_name:
               return domain

    @classmethod
    def get_domain(cls, short_name):
        """Returns a Domain instance.

        Args:
          name (str): standard name of the Domain.

        Returns:
          Domain (:class:`Domain`) : a Domain instance.

        """
        out = None
        if short_name in cls.names_from_static_domains():
            out = cls.get_static_domain(short_name)
        elif short_name in cls.names_from_csv():
            out = cls.create_domain_from_table(short_name)
        if out is None:
           _logger.error('Unknown domain name: '+short_name)
           _logger.info('Known domain names: '+str(cls.names()))
           raise Exception('Unknown domain name: '+short_name)
        else:
           return out




def domain(name):
    """Top level Domain function to get a :class:`Domain` instance.

    Args:
      name (str): name of the domain instance.

    Returns:
      :class:`Domain`: preconfigured domain instance.

    """
    return _DomainFactory().get_domain(name)


def domains(table=None):
    """Top level function that returns a list of available CORDEX domains.

    Returns:
      names (list): list of available CORDEX domains.

    """
    return _DomainFactory().names(table)


def table(name):
    """Top level function that returns a CORDEX table.

    Args:
      name (str): name of the CORDEX table.

    Returns:
      table (DataFrame): Cordex table.

    """
    return TABLES[name]

def tables():
    """Top level function that returns a list of available CORDEX tables.

    Returns:
      names (list): list of available CORDEX domains.

    """
    return list(TABLES.keys())
