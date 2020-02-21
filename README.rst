.. image:: https://readthedocs.org/projects/cordex/badge/?version=latest
    :alt: Documentation Status
    :target: https://cordex.readthedocs.io/en/latest/?badge=latest
.. image:: https://travis-ci.org/euro-cordex/cordex.svg?branch=develop
    :target: https://travis-ci.org/euro-cordex/cordex
.. image:: https://coveralls.io/repos/github/euro-cordex/cordex/badge.svg?branch=develop
    :target: https://coveralls.io/github/euro-cordex/cordex?branch=develop

======
cordex
======


cordex python package


Description
===========

Python package for common tools and data in the Cordex community.

Installation
============

You can install the package directly from github using pip:


.. code-block:: console

    pip install git+https://github.com/euro-cordex/cordex
   
 
If you want to contribute, I recommend cloning the repository and installing the package in development mode, e.g.

    
.. code-block:: console

    git clone https://github.com/euro-cordex/cordex
    cd cordex
    pip install -e .

    
This will install the package but you can still edit it and you don't need the package in your :code:`PYTHONPATH`

Highlights
==========

Using the ESGF module for browsing the file system and creating pandas dataframes of file selections:
(DKRZ example)

.. code-block:: python

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

    selection = get_selection(project_id, root=root, filter=filter)
    print(selection)

    selection = selection.subset(variable='pr').to_datetime()
    selection = selection.select_timerange([dt.datetime(1990,1,1),dt.datetime(2000,1,1)])
    print(selection)
    
Use the domain module to create Cordex domains safe and easy:

.. code-block:: python

    from cordex import domain as dm

    for short_name in dm.domains():
        print('creating domain: {}'.format(short_name))
        domain = dm.domain(short_name)
        print(domain)
        domain.to_netcdf(short_name+'.nc', dummy='topo')


Requirements
============

* python3.6 or higher
* numpy
* pandas
* (xarray)
* netCDF4
* parse


Note
====

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.
