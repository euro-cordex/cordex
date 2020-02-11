

import os
import copy
import logging

from . import conventions as conv



# cordex ESGF example
# cordex/output/EUR-11/GERICS/MPI-M-MPI-ESM-LR/historical/r3i1p1/GERICS-REMO2015/v1/day/pr/v20190925/pr_EUR-11_MPI-M-MPI-ESM-LR_historical_r3i1p1_GERICS-REMO2015_v1_day_19500102-19501231.nc
# cordex/output/EUR-11/GERICS/ECMWF-ERAINT/evaluation/r1i1p1/GERICS-REMO2015/v1/day/pr/v20180813/pr_EUR-11_ECMWF-ERAINT_evaluation_r1i1p1_GERICS-REMO2015_v1_day_*
# cordex/output/EUR-22/GERICS/MPI-M-MPI-ESM-LR/rcp26/r1i1p1/GERICS-REMO2015/v1/mon/tas/v20191025/tas_EUR-22_MPI-M-MPI-ESM-LR_rcp26_r1i1p1_GERICS-REMO2015_v1_mon_200601-201012.nc

class Cordex(conv.FileConvention):

    def __init__(self, root='', defaults={}):
        conv.FileConvention.__init__(self, root, defaults)
        self.name      = 'CORDEX'
        self.path_conv = ['product','CORDEX_domain','institute_id','driving_model_id', \
                          'experiment_id', 'ensemble', 'model_id', 'rcm_version_id'  , \
                          'frequency', 'variable', 'date']
        self.file_conv = ['variable','CORDEX_domain','driving_model_id', \
                          'experiment_id', 'ensemble', 'model_id', 'rcm_version_id'  , \
                          'frequency', 'timerange']
        self.suffix    = '.nc'
        self.conv_str  = '{variable}_{CORDEX_domain}_{driving_model_id}_{experimend_id}_' \
                         '{ensemble}_{model_id_rcm}_{version_id}_{frequency}_' \
                         '{startdate}-{enddate}.{suffix}'


# cmip5 ESGF example
# cmip5/output1/MPI-M/MPI-ESM-LR/historical/day/atmos/day/r1i1p1/v20111006/pr/pr_day_MPI-ESM-LR_historical_r1i1p1_*
# cmip5/output1/MPI-M/MPI-ESM-LR/historical/day/atmos/day/r1i1p1/v20111006/pr/pr_day_MPI-ESM-LR_historical_r1i1p1_18500101-18591231.nc
# cmip5/output2/MPI-M/MPI-ESM-LR/historical/mon/ocean/Omon/r1i1p1/v20131120/umo/umo_Omon_MPI-ESM-LR_historical_r1i1p1_185001-185912.nc

class CMIP5(conv.FileConvention):

    def __init__(self, root='', defaults={}):
        conv.FileConvention.__init__(self, root, defaults)
        self.name      = 'CMIP5'
        self.path_conv = ['product','institute_id','model_id', \
                          'experiment_id', 'frequency', 'realm', 'rfrequency', 'ensemble'  , \
                          'date', 'variable']
        self.file_conv = ['variable', 'frequency', 'model_id', 'experiment_id'  , \
                          'ensemble', 'timerange']
        self.conv_str  = '{variable}_{frequency}_{model_id}_{experimend_id}_' \
                         '{ensemble}_{startdate}-{enddate}.{suffix}'
        self.suffix    = '.nc'


class _ConventionFactory(object):
    """Factory class for creating a NamingConvention instance.

    """
    @staticmethod
    def conventions():
       return [Cordex(), CMIP5()]

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



#institute_id            = 'GERICS'
#project_id              = 'CORDEX'
#CORDEX_domain           = 'EUR-22'
#product                 = 'output'
#driving_model_id        = 'ECMWF-ERAINT'
#driving_experiment_name = 'evaluation'
#ensemble                = 'r0i0p0'
#model_id                = 'GERICS-REMO2015'
#rcm_version_id          = 'v1'
#frequency               = 'fx'
#cf_name                 = 'orog'


def select(project_id, **kwargs):
    convention = _ConventionFactory.get_convention(project_id)
    return conv.select_files(convention, **kwargs)


def conventions():
    return _ConventionFactory.names()




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


