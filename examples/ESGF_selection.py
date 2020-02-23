import datetime as dt
from cordex.ESGF import get_selection, conventions

project_id = 'CMIP5'
root       = '/pool/data/CMIP5/cmip5'

filter   = {'institute_id' : 'MPI-M',
            'output'       : 'output1',
            'model_id'     : 'MPI-ESM-LR',
            'realm'        : 'atmos',
            'experiment_id': 'historical',
            'ensemble'     : 'r1i1p1'}

# get a selection of files (using pandas dataframes)
selection = get_selection(project_id, root=root, filter=filter)
print(selection)

# create a finer selection and convert dates to datetime objects
selection = selection.subset(variable='pr').to_datetime()
# get a timeseries of files
selection = selection.select_timerange([dt.datetime(1990,1,1),dt.datetime(2000,1,1)])
print(selection)
