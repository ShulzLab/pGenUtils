# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 14:49:52 2021

@author: Timothe
"""

try :
    import pandas as pd
except :
    pass

def empty_df(columns, dtypes=[], index=None):
    """
    Creates an empty dataframe with the columns and data types as specified.
    *Previously named df_empty*

    Args:
        columns (list): list of columns names (list of str) .
        dtypes (list, optional): list of data types. Can be numpy built in data types, pandas, or numpy.
        index (list, optional): Index name. Defaults to None. (If None : auto integer index corresponding to row numbers)

    Todo:
        Add ability to create multi-index with that function

    Returns:
        pd.DataFrame : The dataframe with the desired columns names and indices.

    """
    df = pd.DataFrame(index=index)

    if ( type(dtypes) == list or type(dtypes) == tuple ) and len(columns)==len(dtypes):
        for c,d in zip(columns, dtypes):
            df[c] = pd.Series(dtype=d)
    else :
        if type(dtypes) == type :
            d = dtypes
        else :
            d = float
        for c in columns:
            df[c] = pd.Series(dtype=d)
    return df