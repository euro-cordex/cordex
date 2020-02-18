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
import pandas as pd

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


UNIQUE = ['product', 'CORDEX_comdain', 'institute_id', 'driving_model_id', 'experimentd_id',
          'ensemble', 'model_id', 'rcm_version_id', 'frequency', 'variable', 'date', 'realm',
          'rfrequency', 'variable']

#date_fmt = '%Y%m'
# 12: 1hr, 3hr
# 10: 6hr
#  8: day
#  6: sem, mon
date_fmts = {12:'%Y%m%d%H%M', 10:'%Y%m%d%H', 8:'%Y%m%d', 6:'%Y%m', 4:'%Y'}


## define date string formats depending on frequency
#date_fmts = {'1hr'    : '%Y%m%d%H%M'  , '3hr' : '%Y%m%d%H%M',
#             '6hr'    : '%Y%m%d%H'    , 'day' : '%Y%m%d',     'cfDay': '%Y%m%d',
#             'sem'    : '%Y%m'        , 'mon' : '%Y%m',       'cfMon': '%Y%m',
#             '6hrPlev': '%Y%m%d%H'    , 'Amon': '%Y%m',
#             '6hrPlev': '%Y%m%d%H'    , 'Omon': '%Y%m'  }


def parse_date(date_str):
    #return dt.datetime.strptime(date_str, date_fmts[freq])
    return dt.datetime.strptime(date_str, date_fmts[len(date_str)])

def format_date(date, freq):
    return date.strftime(date_fmts[freq])

#date_formatter = conv.Formatter('date', fmt=date_fmt, parser=parse_date)

#formatters = {'startdate':date_formatter}



class ESGFFileNameConvention(conv.FileNameConvention):

    def __init__(self, *args, **kwargs):
        conv.FileNameConvention.__init__(self, *args, **kwargs)

    #def parse_attrs(self, attrs):
    #    print(attrs)
    #    attrs['startdate'] = parse_date(attrs['startdate'], attrs['frequency'])
    #    attrs['enddate']   = parse_date(attrs['enddate'], attrs['frequency'])
    #    return attrs

    #def format_attrs(self, attrs, any_str):
    #    if isinstance(attrs['startdate'], dt.datetime):
    #        attrs['startdate'] = format_date(attrs['startdate'], attrs['frequency'])
    #    if isinstance(attrs['enddate'], dt.datetime):
    #        attrs['enddate']   = format_date(attrs['enddate'], attrs['frequency'])
    #    return attrs


class CORDEX(conv.FileConvention):
    """Implements CORDEX path and filename conventions.
    """
    name      = 'CORDEX'

    def __init__(self, root=None):
        path_conv      = conv.FilePathConvention(cordex_path_list, root=root)
        filename_conv  = ESGFFileNameConvention(cordex_conv_str, formatters=None)
        conv.FileConvention.__init__(self, path_conv, filename_conv)



class CMIP5(conv.FileConvention):
    """Implements CMIP5 path and filename conventions.
    """
    name      = 'CMIP5'

    def __init__(self, root=None):
        path_conv      = conv.FilePathConvention(cmip5_path_list, root=root)
        filename_conv  = ESGFFileNameConvention(cmip5_conv_str, formatters=None)
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



class ESGFFileSelection(conv.FileSelection):
    """Holds a Pandas Dataframe object.

    The :class:`ESGFFileSelection` holds and manages a Pandas
    Dataframe instance. It defines some common methods to work
    with ESGF netcdf files.
    """
    def __init__(self, *args, **kwargs):
        conv.FileSelection.__init__(self, *args, **kwargs)

    def subset(self, **kwargs):
        """Create a subset by filtering attributes.
        """
        return ESGFFileSelection(super().subset(**kwargs).df)

    def to_datetime(self):
        """Converts the date columns to datetime objects.

        The date columns (startdate, enddate) are converted to datetime
        objects depending on the lenght of the date string.

        Returns:
             :class:`ESGFFileSelection`: selection converted date columns.
        """
        df = self.df
        for index, row in df.iterrows():
            row['startdate'] = parse_date(row['startdate'])
            row['enddate']   = parse_date(row['enddate'])
        return ESGFFileSelection(df)

    def select_timerange(self, time_range):
        """Returns a selected timerange.

        Args:
            time_range (tuple): Tuple that contains a startdate
                and enddate in datetime format.

        Returns:
             :class:`ESGFFileSelection`: selection within time range.

        """
        df = self.df[(self.df['startdate'] >= time_range[0]) & (self.df['startdate'] < time_range[1])]
        return ESGFFileSelection(df)

    @property
    def timerange(self):
        return (min(self.df['startdate']), max(self.df['enddate']))


def select_files(project_id, filter={}, root=None, **kwargs):
    """Creates a file selection containing attributes.
    """
    convention = get_convention(project_id, root=root)
    return conv.select_files(convention, filter, root, **kwargs)


def file_selection_from_scratch():
    pass

def file_selection_from_csv(filename):
    return ESGFFileSelection(pd.from_csv(filename))

def get_selection(convention_id, filter={}, root=None, **kwargs):
    """Top level function to create a :class:`ESGFFileSelection` instance.

    This function creates a :class:`FileSelection` instance
    using a file naming convention of type :class:``FileConvention`.

    Args:
        convention_id (str): The name of the convention.
        filter (dict): Defines attributes to filer the search.
        root (str): The root directory where the convention holds.

    Returns:
        :class:`ESGFFileSelection` object.

    """
    convention = get_convention(convention_id, root=root)
    files      = conv.select_files(convention, filter, root, **kwargs)
    df         = conv.make_df(convention, files)
    return ESGFFileSelection(df)


def conventions():
    """Lists available ESGF conventions.

    Returns:
        List of available ESGF convention ids.
    """
    return _ConventionFactory.names()


def get_convention(name, root=None):
    """Returns a ESGS convention instance.

    Args:
        name (str): The convention id.

    Returns:
        :class:`ESGFFileConvention` object.
    """
    return _ConventionFactory.get_convention(name)(root=root)


def unique(df):
    for column, data in df.items():
        column_in_unique = column in UNIQUE
        data_unique      = len(data.unique())==1
        if column_in_unique and not data_unique:
            return False
    return True


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


