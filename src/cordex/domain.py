# -*- coding: utf-8 -*-
# flake8: noqa
"""Domain module

This module defines preconfigured CORDEX domain. The :class:`Domain` class
is a kind of wrapper for the :class:`Grid` class to connect a grid
with meta information and easy to use functions that work on the member grid.

"""

import numpy as np
import logging

import xarray as xr
from netCDF4 import Dataset

from . import grid as gd
from . import cf

from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)



class Domain():
    """The :class:`Domain` holds data and meta information of a Cordex Domain.
    """
    def __init__(self, nlon, nlat, dlon, dlat,
                 pollon, pollat, ll_lon, ll_lat, name=None, attrs=None):
        if name is None:
            self.name = 'NO NAME'
        else:
            self.name = name
        self.dimnames = ('rlon', 'rlat')
        self.grid_rotated = self._init_grid(nlon, nlat, dlon, dlat, ll_lon, \
                                   ll_lat, pollon, pollat)
        self.grid_lonlat  = self.grid_rotated.transform()
        if attrs is None:
            self.global_attrs = {}
        else:
            self.global_attrs = attrs


    def _init_grid(self, nlon, nlat, dlon, dlat, ll_lon, ll_lat, pollon, pollat):
        rlon = np.array([ll_lon+i*dlon for i in range(0,nlon)], dtype=np.float64)
        rlat = np.array([ll_lat+i*dlat for i in range(0,nlat)], dtype=np.float64)
        return gd.Grid(rlon, rlat, pollon, pollat)


    def extend(self, nlon, nlat=None):
        """Extend a Domain with a number of boundaray cells.

        Args:
          nlon (int): number of extensions in longitual direction.
          nlat (int): number of extensions in latitude direction (default nlat=nlon).

        Returns:
          Domain: Domain instance with extended boundaries.

        """
        if nlat is None: nlat = nlon
        ll_lon = self.ll_lon -  nlon * self.dlon
        ll_lat = self.ll_lat -  nlat * self.dlat
        return Domain(self.nlon+2*nlon, self.nlat+2*nlat, self.dlon, self.dlat,
                      self.pollon, self.pollat, ll_lon, ll_lat)


    def __str__(self):
        text = '\n----- Domain Object -----\n'
        text += '{:<15}    :   {}\n'.format('name', self.name)
        text += str(self.grid_rotated)
        return text


    def get_global_attrs(self):
        attrs = self.global_attrs.copy()
        attrs.update({'CORDEX_domain': self.name})
        return attrs


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


    def get_xarray_dataset(self, grid='', attrs=True, **kwargs):
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
        return create_dataset_nc4(self, filename, **kwargs)





class CFDataset():


    def __init__(self):
        pass


    def add_dimension(self):
        pass

    def add_coorindate(self):
        pass

    def get_dataset(self, grid='', attrs=True, **kwargs):
        return ds.squeeze(drop=True)



class NC4Dataset(CFDataset):

    def __init__(self):
        CFDataset.__init__(self)
        self.ds = None

    def create(self, filename):
        self.ds = Dataset(filename, mode='w')
        return self.ds

    def add_dimension(self, name, length):
        dim = self.ds.createDimension(name, length)
        return dim

    def add_data(self, name, data, **kwargs):
        var = self.ds.createVariable(name, **kwargs)
        var[:] = data
        return var


def create_dataset_nc4(domain, filename='', dummy=None, mapping_name=None, attrs=True):
    if mapping_name is None:
        mapping_name = cf.DEFAULT_MAPPING_NCVAR
    ds = NC4Dataset()
    ds.create(filename)
    ds.add_data(mapping_name, data=np.empty(()), datatype=np.int32)
    map_attrs = cf.mapping.copy()
    map_attrs['grid_north_pole_longitude'] = domain.grid_rotated.pole[0]
    map_attrs['grid_north_pole_latitude']  = domain.grid_rotated.pole[1]
    ds.ds.variables[mapping_name].setncatts(map_attrs)
    rlon, rlat = domain.grid_rotated.coordinates
    rlon = rlon[0]
    rlat = rlat[:,0]
    nrlon = len(rlon)
    nrlat = len(rlat)
    ds.add_dimension('rlon', len(rlon))
    ds.add_dimension('rlat', len(rlat))
    rlon_coord = ds.add_data('rlon', rlon, datatype=np.float64, dimensions=('rlon'))
    rlat_coord = ds.add_data('rlat', rlat, datatype=np.float64, dimensions=('rlat'))
    lon, lat = domain.grid_lonlat.coordinates
    lon_coord = ds.add_data('lon', lon, datatype=np.float64, dimensions=('rlat','rlon'))
    lat_coord = ds.add_data('lat', lat, datatype=np.float64, dimensions=('rlat','rlon'))

    if attrs:
        for key, item in cf.coords.items():
            ds.ds.variables[key].setncatts(item)

    if dummy:
        if dummy is True:
            dummy_name = 'dummy'
        else:
            dummy_name = dummy
        dummy = ds.add_data(dummy_name, np.zeros((nrlat, nrlon)), datatype=np.float32, dimensions=('rlat','rlon'))
        dummy.setncattr('grid_mapping', mapping_name)
        dummy.setncattr('coordinates', 'lat lon')
        if dummy_name == 'topo':
            from cdo import Cdo
            cdo = Cdo()
            ds.ds.close()
            topo = cdo.topo(filename, returnCdf=True).variables['topo'][:]
            ds.ds = Dataset(filename, mode='a')
            ds.ds.variables['topo'][:] = topo
    return ds.ds


class EUR_44(Domain):
    """Defines the EUR-44 rotated Domain.
    """
    def __init__(self):
        Domain.__init__(self, 106, 103, 0.44, 0.44,
            -162.0, 39.25, -28.21, -23.21, name='EUR-44')



class EUR_11(Domain):
    """Defines the EUR-11 rotated Domain.
    """
    def __init__(self):
        Domain.__init__(self, 424, 412, 0.11, 0.11,
            -162.0, 39.25, -28.375, -23.375, name='EUR-11')



class _DomainFactory(object):
    """Factory class for creating a domain instance.
    """

    @staticmethod
    def domains():
        """Returns a list of instances of available Domains.
        """
        return [EUR_44(), EUR_11()]

    @classmethod
    def names(cls):
        """Returns a list of names of available Domains.
        """
        return [domain.name for domain in cls.domains()]

    @classmethod
    def get_domain(cls, name):
        """Returns a Domain instance.

        Args:
          name (str): standard name of the Domain.

        Returns:
          Domain (:class:`Domain`) : a Domain instance.

        """
        out = None
        for domain in cls.domains():
           if name == domain.name:
              out = domain
        if out is None:
           _logger.error('Unknown domain name: '+domain)
           _logger.info('Known domain names: '+str(cls.domains()))
           raise Exception('Unknown domain name: '+name)
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


def domains():
    """Top level function that returns a list of available CORDEX domains.

    Returns:
      names (list): list of available CORDEX domains.

    """
    return _DomainFactory().names()
