# -*- coding: utf-8 -*-
# flake8: noqa
import pytest
from cordex import grid as gd

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"



def test_grids():
    # assert grid names
    for grid in gd.grids():
        print(grid)
        assert grid == gd.grid(grid).name



if __name__ == '__main__':
    test_grids()
