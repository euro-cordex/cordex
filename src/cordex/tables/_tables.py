"""This module defines the csv tables for cordex.
"""

import pandas as pd
import pkg_resources

domain_tables = {'cordex-core': 'cordex-core.csv',
       'cordex': 'cordex.csv',
       'cordex-high-res': 'cordex-high-res.csv'}


data_request_tables = {'cmip5': 'https://raw.githubusercontent.com/euro-cordex/tables/master/data-request/cordex-cmip5.csv'}


def read_table(table, **kwargs):
    """reads a csv table from an external resource.
    """
    csv_file = table
    return pd.read_csv(csv_file, **kwargs)
    
def read_tables(csv_dict, **kwargs):
    """reads all tables from an external resource.
    """
    tables = {}
    for set_name, table in csv_dict.items():
        tables[set_name] = read_table(table, **kwargs)
    return tables

def read_resource_table(csv, **kwargs):
    """reads a csv table from the package resource.
    """
    csv_file = pkg_resources.resource_stream('cordex.tables', csv)
    return pd.read_csv(csv_file, **kwargs)

def read_resource_tables(csv_dict, **kwargs):
    """reads all csv tables from the package resource.
    """
    tables = {}
    for set_name, table in csv_dict.items():
        tables[set_name] = read_resource_table(table, **kwargs)
    return tables
