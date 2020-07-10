# -*- coding: utf-8 -*-
# flake8: noqa
"""Variable module

This module defines variables for the CORDEX data request.

"""

from .tables import data_request_tables, read_tables 


try:
  TABLES = read_tables(data_request_tables, index_col='variable_id', converters = {'frequency': (lambda x: x.split(",")) })
except:
  print('could not read tables from: {}'.format(data_request_tables))
  TABLES = {}


def table(name):
    """Top level function that returns a CORDEX data request table.

    Args:
      name (str): name of the CORDEX table.

    Returns:
      table (DataFrame): Cordex table.

    """
    return TABLES[name]


def tables():
    """Top level function that returns a list of available CORDEX data request tables.

    Returns:
      names (list): list of available CORDEX data request tables.

    """
    return list(TABLES.keys())




class Variable():

    def __init__(self, variable_id, project_id='cmip5'):
        self.variable_id = variable_id
        self.project_id  = project_id
        self._from_table()


    def __str__(self):
        return str(self.series)

    def __repr__(self):
        return str(self.series)


    def __getattr__(self, attr):
        if attr in self.series:
           return self.series[attr]
        else:
           raise AttributeError 

    def _from_table(self):
        self.series = table(self.project_id).loc[self.variable_id]
       


def variables(project_id='cmip5'):
    return {id:Variable(id, project_id) for id in table(project_id).index}
     
