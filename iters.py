# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Mar 30 17:48:42 2020

@author: Timothe
"""
#import sys
#import numpy as np


def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def unique_pairs(a,b):
    """Produce pairs of values from two iterables"""
    for i in a:
        for j in b:
            yield i, j

def nest_iter(dimension,current_dimension=None,slicing = False,**kwargs):
    """
    Recursive function that produces a generator meant to yield nested index values to target every possible array sub_unit, whatever the number of provided dimensions

    Parameters
    ----------
    dimension : TYPE
        DESCRIPTION.
    current_dimension : TYPE, optional
        Internal only parameter.
        Specifies the current state of the iteration for the yielder.
        The default is None.
    slicing : Bool, optional
        dimensions indices are returns in the format of a tuple of slices objects (for better compatibility with numpy arrays)
        The default is False.
    **kwargs : TYPE
        DESCRIPTION.

    Raises
    ------
    StopIteration
        DESCRIPTION.

    Yields
    ------
    TYPE
        DESCRIPTION.

    """
    if current_dimension is None :
        current_dimension = [0,]*len(dimension)
        slicing = kwargs.get("slices",False)

    for i in range(dimension[len(dimension)-1]):
        current_dimension[len(dimension)-1] = i
        if slicing :
            outuple = tuple()
            for j in range(len(dimension)):
                outuple = outuple + (slice(current_dimension[j],current_dimension[j]+1),)
            yield outuple
        else :
            yield tuple(current_dimension)

    for j in range(len(dimension)):
        if current_dimension[j] == dimension[j]-1:
            if j == 0 :
                return #python 3.5 equivelent of raise StopIteration
            #https://stackoverflow.com/questions/43617399/how-to-get-rid-of-warning-deprecationwarning-generator-ngrams-raised-stopiter
            for u in range(j,len(dimension)):
                current_dimension[u] = 0
            current_dimension[j-1] = current_dimension[j-1] + 1

    yield from nest_iter(dimension,current_dimension,slicing)


if __name__ == "__main__":

    pass