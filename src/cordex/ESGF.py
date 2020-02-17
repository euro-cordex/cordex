# -*- coding: utf-8 -*-
# flake8: noqa
"""ESGF convenESGF conventionss module

This module defines common ESGF path and filename conventions.

Example:

    To get an index from the :class:`RotatedGrid`, you just need to import it.
    To get a list of available implementations, you can call, e.g.,::

        from cordex import ESGF
        print(ESGF.conventions())

The main interface function is `select_files`.

"""

import os
import copy
import logging
import datetime as dt

from . import conventions as conv


cordex_path_list = ['product','CORDEX_domain','institute_id','driving_model_id', \
                    'experiment_id', 'ensemble', 'model_id', 'rcm_version_id'  , \
                    'frequency', 'variable', 'date']
cordex_conv_str  = '{variable}_{CORDEX_domain}_{driving_model_id}_{experimend_id}_' \
                   '{ensemble}_{model_id}_{rcm_version_id}_{frequency}_' \
                   '{startdate}-{enddate}.{suffix}'
cmip5_path_list  = ['product','institute_id','model_id', \
                    'experiment_id', 'frequency', 'realm', 'rfrequency', 'ensemble'  , \
                    'date', 'variable']
cmip5_conv_str   = '{variable}_{frequency}_{model_id}_{experimend_id}_' \
                   '{ensemble}_{startdate}-{enddate}.{suffix}'

ESGF_CONVS = { 'CORDEX': {'path': cordex_path_list, 'file': cordex_conv_str},
               'CMIP5' : {'path': cmip5_path_list,  'file': cmip5_conv_str}  }


date_fmt = '%Y%m'
# 12: 1hr, 3hr
# 10: 6hr
#  8: day
#  6: sem, mon
date_fmts = {12:'%Y%m%d%H%M', 10:'%Y%m%d%H', 8:'%Y%m%d', 6:'%Y%m'}
date_fmts_by_freq = {12:'%Y%m%d%H%M', 10:'%Y%m%d%H', 8:'%Y%m%d', 6:'%Y%m'}

date_fmts = {'1hr': '%Y%m%d%H%M', '3hr': '%Y%m%d%H%M',
             '6hr': '%Y%m%d%H'  , 'day': '%Y%m%d',
             'sem': '%Y%m'      , 'mon': '%Y%m', }


def parse_date(date_str, freq):
    return dt.datetime.strptime(date_str, date_fmts[freq])

def format_date(date, freq):
    return date.strftime(date_fmts[freq])

date_formatter = conv.Formatter('date', fmt=date_fmt, parser=parse_date)

formatters = {'startdate':date_formatter}


class ESFG


class CORDEXFileNameConvention(conv.FileNameConvention):

    def __init__(self, *args, **kwargs):
        conv.FileNameConvention.__init__(self, *args, **kwargs)

    def parse_attrs(self, attrs):
        attrs['startdate'] = parse_date(attrs['startdate'], attrs['frequency'])
        attrs['enddate']   = parse_date(attrs['enddate'], attrs['frequency'])
        return attrs

    def format_attrs(self, attrs, any_str):
        if isinstance(attrs['startdate'], dt.datetime):
            attrs['startdate'] = format_date(attrs['startdate'], attrs['frequency'])
        if isinstance(attrs['enddate'], dt.datetime):
            attrs['enddate']   = format_date(attrs['enddate'], attrs['frequency'])
        return attrs


class CORDEX(conv.FileConvention):
    """Implements CORDEX path and filename conventions.
    """
    name      = 'CORDEX'

    def __init__(self, root=None):
        path_conv      = conv.FilePathConvention(cordex_path_list, root=root)
        filename_conv  = CORDEXFileNameConvention(cordex_conv_str, formatters=None)
        conv.FileConvention.__init__(self, path_conv, filename_conv)
        filename_conv



class CMIP5(conv.FileConvention):
    """Implements CMIP5 path and filename conventions.
    """
    name      = 'CMIP5'

    def __init__(self, root=None):
        path_conv      = conv.FilePathConvention(cmip5_path_list, root=root)
        filename_conv  = conv.FileNameConvention(cmip5_conv_str, formatters=None)
        conv.FileConvention.__init__(self, path_conv, filename_conv)



class _ConventionFactory(object):
    """Factory class for creating a NamingConvention instance.
    """

#    @staticmethod
#    def create_convention(name):
#        path_conv     = conv.FilePathConvention(ESGF_CONVS[name]['path'])
#        filename_con  = conv.FileNameConvention(ESGF_CONVS[name]['file'])
#        return conv.FileConvention(path_conv, filename_conv)

    @staticmethod
    def conventions():
#        return [cls.create_convention(name) for name in ESGF_CONVS]
        return [CORDEX, CMIP5]

    @classmethod
    def names(cls):
        list_of_names = []
        for conv in cls.conventions():
           list_of_names.append(conv.name)
        return list_of_names

    @classmethod
    def get_convention(cls, name):
        convention = None
        for conv in cls.conventions():
           if name == conv.name:
             convention = conv
        if convention is None:
           logging.error('Unknown convention name: '+name)
           logging.info('Known convention names: '+str(cls.names()))
           raise Exception('Unknown convention name: '+name)
        else:
           return convention


def select_files(project_id, filter={}, root=None, **kwargs):
    """Creates a file selection containing attributes.
    """
    convention = get_convention(project_id, root=root)
    return conv.select_files(convention, filter, root, **kwargs)


def conventions():
    """Lists available ESGF conventions.
    """
    return _ConventionFactory.names()


def get_convention(name, root=None):
    """Returns a ESGS convention instance.
    """
    return _ConventionFactory.get_convention(name)(root=root)


def iterdict(d):
    for k,v in d.items():
        if isinstance(v, dict):
            iterdict(v)
        else:
            print (k,":",v)



        #for item in reversed(path_conv[:-1]):
        #    dict = {item:dict} 
        #for path in self.pathes:
        #    path_list = path.split(os.sep)
        #    for value in reversed(path_list[-nitem:]):


