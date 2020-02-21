# -*- coding: utf-8 -*-
# flake8: noqa
import pytest
from cordex import domain as dm

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"



def test_names():
    # assert domain names
    for short_name in dm.domains():
        print(short_name)
        assert short_name == dm.domain(short_name).short_name


def test_write():
    domain = dm.domain('EUR-11')
    domain.to_netcdf('EUR-11.nc')


if __name__ == '__main__':
    test_names()
    test_write()
