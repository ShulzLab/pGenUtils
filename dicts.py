# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Aug 23 14:24:59 2021

@author: Timothe
"""

def keep_matched_keys(dict_to_modify,source_dict):
    """
    Keeps the keys of a dict where they have the same name as the keys in a source dictionnary.

    Args:
        dict_to_modify (TYPE): DESCRIPTION.
        source_dict (TYPE): DESCRIPTION.

    Returns:
        modified_dict (TYPE): DESCRIPTION.

    """
    modified_dict = dict_to_modify.copy()
    modified_dict = { your_key: modified_dict[your_key] for your_key in source_dict.keys() if your_key != 'empty' and modified_dict.get(your_key) is not None }
    return modified_dict

def drop_matched_keys(dict_to_modify,source_dict):
    """
    Drops the keys of a dict where they have the same name as the keys in a source dictionnary.

    Args:
        dict_to_modify (TYPE): DESCRIPTION.
        source_dict (TYPE): DESCRIPTION.

    Returns:
        modified_dict (TYPE): DESCRIPTION.

    """
    modified_dict = dict_to_modify.copy()
    [ modified_dict.pop(your_key,False) for your_key in source_dict.keys() ]
    return modified_dict