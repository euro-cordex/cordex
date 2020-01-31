# -*- coding: utf-8 -*-
"""Grid module

This module defines preconfigured CORDEX grids.

Example:
    To get an index from the :class:`RotatedGrid`, you just need to import it.
    To get a list of available implementations, you can call, e.g.,::

        from cordex import grid
        print(grid.grids())

    and to get an instance::

        EUR44 = grid.grid('EUR-44')
        EUR11 = grid.grid('EUR-11')

More to come soon..
"""

import numpy as np
import logging

from cordex import __version__

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"


class Grid(object):
    """Parent grid class.
    """
    pass

class RotatedGrid(Grid):
    """The :class:`RotatedGrid` holds data and meta information of a rotated grid.
    """
    def __init__(self, nlon, nlat, dlon, dlat,
                 pollon, pollat, ll_lon, ll_lat, name=None):
        if name is None: 
            self.name = 'NO NAME'
        else:
            self.name = name
        self.nlon = nlon
        self.nlat = nlat
        self.dlon = dlon
        self.dlat = dlat
        self.pollon = pollon
        self.pollat = pollat
        self.ll_lon = ll_lon
        self.ll_lat = ll_lat
        self._init_data()

    def _init_data(self):
        self.rlon = np.array([self.ll_lon+i*self.dlon for i in range(0,self.nlon)], dtype=np.float64)
        self.rlat = np.array([self.ll_lat+i*self.dlat for i in range(0,self.nlat)], dtype=np.float64)

    def extend(self, nlon, nlat=None):
        """Extend a grid with a number of boundaray cells.

        Args:
          nlon (int): number of extensions in longitual direction.
          nlat (int): number of extensions in latitude direction (default nlat=nlon).

        Returns:
          Grid: Grid instance with extended boundaries. 

        """
        if nlat is None: nlat = nlon
        ll_lon = self.ll_lon -  nlon * self.dlon
        ll_lat = self.ll_lat -  nlat * self.dlat
        return RotatedGrid(self.nlon+2*nlon, self.nlat+2*nlat, self.dlon, self.dlat,
                self.pollon, self.pollat, ll_lon, ll_lat)

    def __str__(self):
        text = '\n----- Grid Object -----\n'
        for key, item in self.__dict__.items():
            text += '{:<15}    :   {}\n'.format(key, item)
        return text



class EUR_44(RotatedGrid):
    """Defines the EUR-44 rotated grid.
    """
    def __init__(self):
        RotatedGrid.__init__(self, 106, 103, 0.44, 0.44,
                -162.0, 39.25, -28.21, -23.21, name='EUR-44')


class EUR_11(RotatedGrid):
    """Defines the EUR-11 rotated grid.
    """
    def __init__(self):
        RotatedGrid.__init__(self, 424, 412, 0.11, 0.11,
                -162.0, 39.25, -28.375, -23.375, name='EUR-11')



class _GridFactory(object):
    """Factory class for creating a Grid instance.
    """

    @staticmethod
    def grids():
        """Returns a list of instances of available grids.
        """
        return [EUR_44(), EUR_11()]

    @classmethod
    def names(cls):
        """Returns a list of names of available grids.
        """
        return [grid.name for grid in cls.grids()]

    @classmethod
    def get_grid(cls, name):
        """Returns a grid instance.

        Args:
          name (str): standard name of the grid.

        Returns:
          grid (:class:`Grid`) : a grid instance. 

        """
        out = None
        for grid in cls.grids():
           if name == grid.name:
              out = grid
        if out is None:
           logging.error('Unknown grid name: '+grid) 
           logging.info('Known grid names: '+str(cls.grids())) 
           raise Exception('Unknown grid name: '+name)
        else:
           return out


def grid(name):
    """Top level grid function to get a :class:`RotatedGrid` instance.

    Args:
      name (str): name of the grid instance.

    Returns:
      Grid: preconfigured grid instance.

    """
    return _GridFactory().get_grid(name)


def grids():
    """Top level function that returns a list of available CORDEX domains.

    Returns:
      names (list): list of available CORDEX domains.

    """
    return _GridFactory().names()
