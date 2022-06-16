# -*- coding: utf-8 -*-
"""Boilerplate:
A one line summary of the module or program, terminated by a period.

Created on Tue Mar 31 02:02:57 2020
@author: Timothe
"""

import re
import numpy as np

from structs import func_io_typematch


def alphabet(index,caps = False):
    if caps :
        return chr(ord('@')+int(index)+1)
    else :
        return chr(ord('`')+index+1)

# list based functions
def alphanum_sort(list_of_strings):
    """
    Sorts an iterable of strings by alphanumeric value.
    *Previously named AlphaNum_Sort*

    Args:
        list_of_strings (list): contains N strings elements.

    Returns:
        list: list of strings sorted.

    Note:
        The return type will be a copy of the input type.
    """
    iomatch = func_io_typematch(list_of_strings)
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)',key)]
    return iomatch.cast(sorted(list_of_strings, key = alphanum_key))

def quick_regexp(input_line,regex,**kwargs):
    """
    Simplified implementation for matching regular expressions. Utility for python's built_in module re .
    *Previously named QuickRegexp*

    Tip:
        Design your patterns easily at [Regex101](https://regex101.com/)

    Args:
        input_line (str): Source on wich the pattern will be searched.
        regex (str): Regex pattern to match on the source.
        **kwargs (optional):
            - groupidx : (``int``)
                group index in case there is groups. Defaults to None (first group returned)
            - matchid : (``int``)
                match index in case there is multiple matchs. Defaults to None (first match returned)
            - case : (``bool``)
                `False` / `True` : case sensitive regexp matching (default ``False``)

    Returns:
        Bool , str: False or string containing matched content.

    Warning:
        This function returns only one group/match.

    """

    if 'case' in kwargs:
        case = kwargs.get("case")
    else :
        case = False

    if case :
        matches = re.finditer(regex, input_line, re.MULTILINE|re.IGNORECASE)
    else :
        matches = re.finditer(regex, input_line, re.MULTILINE)

    groupidx = kwargs.get("groupidx",None)
    matchid = kwargs.get("matchidx",None)
    if matchid is not None :
        matchid = matchid +1

    for matchnum, match in enumerate(matches,  start = 1):

        if matchid is not None :
            if matchnum == matchid :
                if groupidx is not None :
                    for groupx, groupcontent in enumerate(match.groups()):
                        if groupx == groupidx :
                            return groupcontent
                    return False

                else :
                    MATCH = match.group()
                    return MATCH

        else :
            if groupidx is not None :
                for groupx, groupcontent in enumerate(match.groups()):
                    if groupx == groupidx :
                        return groupcontent
                return False
            else :
                MATCH = match.group()
                return MATCH
    return False

#paths related functions

def quick_regexp_multi(input_line,regex,**kwargs):
    """
    Simplified implementation for matching regular expressions. Utility for python's built_in module re .
    *Previously named QuickRegexp*

    Tip:
        Design your patterns easily at [Regex101](https://regex101.com/)

    Args:
        input_line (str): Source on wich the pattern will be searched.
        regex (str): Regex pattern to match on the source.
        **kwargs (optional):
            - groupidx : (``int``)
                group index in case there is groups. Defaults to None (first group returned)
            - matchid : (``int``)
                match index in case there is multiple matchs. Defaults to None (first match returned)
            - case : (``bool``)
                `False` / `True` : case sensitive regexp matching (default ``False``)

    Returns:
        Bool , str: False or string containing matched content.

    Warning:
        This function returns only one group/match.

    """
    
    def listify(var):
        return [var] if var is not None and not isinstance(var,(list,tuple)) else var

    if 'case' in kwargs:
        case = kwargs.get("case")
    else :
        case = False

    if case :
        matches = re.finditer(regex, input_line, re.MULTILINE|re.IGNORECASE)
    else :
        matches = re.finditer(regex, input_line, re.MULTILINE)

    groupidxs = listify(kwargs.get("groupidxs",None))
    matchidxs = listify(kwargs.get("matchidxs",None))
    if matchidxs is not None :
        for index, value in enumerate(matchidxs):
            matchidxs[index] +=  1

    results = []
    for matchnum, match in enumerate(matches,  start = 1):

        if matchidxs is not None and groupidxs is None:
            for matchid in matchidxs :
                if matchid == matchnum :
                    results.append(match)
                    
        if  groupidxs is not None and ( (matchidxs is not None and matchnum in matchidxs ) or (matchidxs is None and matchnum == 1) ) :
            for groupx, groupmatch in enumerate(match.groups()):
                for groupid in groupidxs :
                    if groupx == groupid :
                        results.append(groupmatch)
                        
        if groupidxs is None and matchidxs is None :
            return [match.group()]
                        
    if len(results) == 0:
        return False
    return results



def greek(input_str):
    greek_letters = ["α","β","γ","δ"]
    roman_repr = ["alpha","beta","gamma","delta"]
    for index, roman in enumerate(roman_repr) :
        if input_str == roman :
            return greek_letters[index]
    return input_str

convert_to_greek = greek #backward compatibility

if __name__ == "__main__":
    import numpy as np
    print(alphanum_sort(["1","54","zze","test1","aske"]))

    #print(folder_search(r"C:\Users\Timothe\NasgoyaveOC\Professionnel\TheseUNIC\DevScripts\Python\__packages__\pLabUtils", "__init__.py"))

    #import configparser
    #import json


    #path = r"C:\Users\Timothe\Desktop\Testzone\test_config.txt"

    #CheckConfigFile(path,["secion1","secion2","secion3"])
    #WriteToConfigFile(path, "secion3" , "newparam2" , 155)


    #test = quick_regexp(string, regex = r"[Mm]ouse_?\d$")