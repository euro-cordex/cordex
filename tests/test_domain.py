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

def test_refine():
    eur11 = dm.domain('EUR-11')
    eur22 = dm.domain('EUR-22')
    eur44 = dm.domain('EUR-44')
    assert(eur22 == eur44.refine(2))
    assert(eur11 == eur44.refine(4))
    # test simple domain math.
    assert(eur22 == 0.5 * eur44 )
    assert(eur11 == 0.25 * eur44 )
    assert(eur11 == 0.5 * eur22 )
    assert(eur44 == 4 * eur11 )


def test_write():
    domain = dm.domain('EUR-11')
    domain.to_netcdf('EUR-11.nc')


if __name__ == '__main__':
    test_names()
    test_write()
