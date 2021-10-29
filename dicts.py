# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Aug 23 14:24:59 2021

@author: Timothe
"""

def keep_matched_keys(dict_to_modify,model_keys):
    """
    Drops only the keys of a dict that do **not** have the same name as the keys in a source dictionnary.
    Return dictionnary containing the rest.

    Args:
        dict_to_modify (TYPE): DESCRIPTION.
        source_dict (TYPE): DESCRIPTION.

    Returns:
        modified_dict (TYPE): DESCRIPTION.

    """
    if isinstance(model_keys, dict) :
        model_keys = set(model_keys.keys())

    return { kept_key : dict_to_modify[kept_key] for kept_key in model_keys if kept_key != 'empty' and dict_to_modify.get(kept_key) is not None}

def drop_matched_keys(dict_to_modify,source_dict):
    """
    Drops all the keys of a dict that have the same name as the keys in a source dictionnary.
    Return dictionnary containing the rest.

    Args:
        dict_to_modify (TYPE): DESCRIPTION.
        source_dict (TYPE): DESCRIPTION.

    Returns:
        modified_dict (TYPE): DESCRIPTION.

    """
    modified_dict = dict_to_modify.copy()
    [ modified_dict.pop(your_key,False) for your_key in source_dict.keys() ]
    return modified_dict