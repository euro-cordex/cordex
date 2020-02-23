
from cordex import ESGF as esgf

root       = '/my_root'

attributes   = {'institute_id'    : 'GERICS',
                'product'         : 'output',
                'model_id'        : 'GERICS-REMO2015',
                'experiment_id'   : 'evaluation',
                'driving_model_id': 'ECMWF-ERAINT',
                'variable'        : 'pr',
                'rcm_version_id'  : 'v1',
                'date'            : 'v20200221',
                'frequency'       : '6hr',
                'CORDEX_domain'   : 'EUR-11',
                'suffix'          : 'nc',
                'ensemble'        : 'r1i1p1'}

convention = esgf.CORDEX()
print(convention.path_conv.conv_str)
print(convention.filename_conv.conv_str)
filename = convention.filename(**attributes, startdate='20010101', enddate='20010131')
path     = convention.path(**attributes, startdate='20010101', enddate='20010131')
file     = convention.pattern(root, **attributes, startdate='20010101', enddate='20010131')
print(filename)
print(path)
print(file)
