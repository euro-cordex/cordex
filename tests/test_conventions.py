# -*- coding: utf-8 -*-
# flake8: noqa
import pytest
import os
from cordex.conventions import FileNameConvention, FilePathConvention

# work around since travis does not install pandas properly!
os.system('pip install pandas')

__author__ = "Lars Buntemeyer"
__copyright__ = "Lars Buntemeyer"
__license__ = "mit"


def test_filename_convention():
    conv_str = '{model}_{domain}_{startdate}-{enddate}.{suffix}'
    filename = 'REMO2015_EUR-11_20150101-20151231.nc'
    conv = FileNameConvention(conv_str)
    attrs = conv.parse(filename)
    print('attrs: {}'.format(attrs))
    assert attrs['model'] == 'REMO2015'
    assert attrs['domain'] == 'EUR-11'
    assert attrs['startdate'] == '20150101'
    assert attrs['enddate'] == '20151231'
    assert attrs['suffix'] == 'nc'
    print(conv.filename(**attrs))
    assert conv.filename(**attrs) == filename
    assert conv.filename(model='REMO2015') == 'REMO2015_*_*-*.*'
    print(conv.filename(model='REMO2015', any_str='MISSING'))
    print(conv.defaults)
    assert conv.filename(model='REMO2015', any_str='MISSING') == 'REMO2015_MISSING_MISSING-MISSING.MISSING'


def test_filepath_convention():
    conv_list = ['model','domain','variable']
    path      = 'REMO2015/EUR-11/pr'
    root      = '/root_dir'
    conv = FilePathConvention(conv_list, root)
    attrs = conv.parse(path)
    print('attrs: {}'.format(attrs))
    print('conv.path_conv: {}'.format(conv.path_conv))
    assert conv.path_conv == 'model/domain/variable'
    assert attrs['model']  == 'REMO2015'
    assert attrs['domain'] == 'EUR-11'
    assert attrs['variable'] == 'pr'
    print(conv.path(**attrs))
    print(conv.path(model='REMO2015', any_str='MISSING'))


if __name__ == '__main__':
    test_filename_convention()
    test_filepath_convention()

