# -*- coding: utf-8 -*-
# flake8: noqa
"""conventions module

This module defines file naming conventions in the
:class:``FileConvention`.

"""

import os
import copy
import logging

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



class CORDEX(conv.FileConvention):
    """Implements CORDEX path and filename conventions.
    """
    name      = 'CORDEX'

    def __init__(self, root=None):
        path_conv      = conv.FilePathConvention(cordex_path_list, root=root)
        filename_conv  = conv.FileNameConvention(cordex_conv_str)
        conv.FileConvention.__init__(self, path_conv, filename_conv)



class CMIP5(conv.FileConvention):
    """Implements CMIP5 path and filename conventions.
    """
    name      = 'CMIP5'

    def __init__(self, root=None):
        path_conv      = conv.FilePathConvention(cmip5_path_list, root=root)
        filename_conv  = conv.FileNameConvention(cmip5_conv_str)
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


