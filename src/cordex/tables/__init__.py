

from ._tables import CSV

import pandas as pd

import pkg_resources



def read_table_from_csv(csv, index_col=None):
    """reads a csv table from the package resource.
    """
    csv_file = pkg_resources.resource_stream('cordex.tables', csv)
    return pd.read_csv(csv_file, index_col=index_col)
