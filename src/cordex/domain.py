# -*- coding: utf-8 -*-
# flake8: noqa
"""Domain module

This module defines preconfigured CORDEX domain.

Example:
    To get an index from the :class:`RotatedDomain`, you just need to import it.
    To get a list of available implementations, you can call, e.g.,::

        from cordex import domain
        print(domain.domains())

    and to get an instance::

        EUR44 = domain.domain('EUR-44')
        EUR11 = domain.domain('EUR-11')

More to come soon..
"""

import numpy as np
import logging

import xarray as xr

from . import grid as gd

from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"

_logger = logging.getLogger(__name__)



class Domain():
    """The :class:`Domain` holds data and meta information of a Cordex Domain.
    """
    def __init__(self, nlon, nlat, dlon, dlat,
                 pollon, pollat, ll_lon, ll_lat, name=None):
        if name is None:
            self.name = 'NO NAME'
        else:
            self.name = name
        self.dimnames = ('rlon', 'rlat')
        self.grid_rotated = self._init_grid(nlon, nlat, dlon, dlat, ll_lon, \
                                   ll_lat, pollon, pollat)
        self.grid_lonlat  = self.grid_rotated.transform()


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


    def get_xarray_rotated(self):
        rlon, rlat   = self.grid_rotated.coordinates
        da_rlon = xr.DataArray(data=rlon[0],   dims=self.dimnames[0])
        da_rlat = xr.DataArray(data=rlat[:,0], dims=self.dimnames[1])
        return da_rlon, da_rlat


    def get_xarray_lonlat(self):
        lon, lat   = self.grid_lonlat.coordinates
        print(lon.shape)
        print(lat.shape)
        da_lon = xr.DataArray(data=lon, dims=tuple(reversed(self.dimnames)))
        da_lat = xr.DataArray(data=lat, dims=tuple(reversed(self.dimnames)))
        return da_lon, da_lat


    def get_xarray_dataset(self, grid=''):
        data = {}
        if not grid:
            data['rlon'], data['rlat'] = self.get_xarray_rotated()
            data['lon'],  data['lat']  = self.get_xarray_lonlat()
        elif grid == 'rotated':
            data['rlon'], data['rlat'] = self.get_xarray_rotated()
        elif grid == 'lonlat':
            data['lon'],  data['lat']  = self.get_xarray_lonlat()
        else:
            raise Exception('unknown grid description, should be \"rotated\" or \"latlon\".')
        return xr.Dataset(coords=data)


    def to_netcdf(self, filename, grid='', **kwargs):
        self.get_xarray_dataset(grid).to_netcdf(filename, **kwargs)


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
