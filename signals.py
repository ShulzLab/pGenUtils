# -*- coding: utf-8 -*-

"""Boilerplate:
A one line summary of the module or program, terminated by a period.

Rest of the description. Multiliner

<div id = "exclude_from_mkds">
Excluded doc
</div>

<div id = "content_index">

<div id = "contributors">
Created on Thu Sep  2 22:19:02 2021
@author: Timothe
</div>
"""
import warnings
import numpy as np

def removenans(array):
    warning.warn("""Never use this function 'removenans' unless you know
                 absolutely for sure that you will never need to know in the
                 future where the nans you removed were initially in your array.
                 Otherwise, always prefer using my_new_array = splicedArray(my_array)
                 to keep nan information even with functions that don't accept nan as input.
                 See help(splicedArray) for more information""")
    #A simple function to remove nans. Cannot know for sure afterward where nans were but still can try with labor intensive and annoying item comparisons with the original array
    return array[~np.isnan(array)]

def get_array_splices_infos(List,threshold = None):
    #Supports Nan containing arrys and is in fact, in part, written to handle
    #detection of edges between numeral data and nan chunks in time series
    import math
    _List = np.asarray(List.copy())

    if threshold is not None :
        if np.isnan(threshold) :
            for idx , val in enumerate(_List) :
                if not np.isnan(val):
                    _List[idx] = 1
        else :
            for idx , val in enumerate(_List) :
                if not np.isnan(val) and val >= threshold :
                    _List[idx] = 1
                if not np.isnan(val) and val < threshold :
                    _List[idx] = 0

    ranges = [i+1  for i in range(len(_List[1:])) if not ( ( _List[i] == _List[i+1] ) or ( math.isnan(_List[i]) and math.isnan(_List[i+1]) ) ) ]
    ranges.append(len(_List))
    ranges.insert(0, 0)

    slices = []
    values = []
    for i in range(len(ranges)-1):
        slices.append([ranges[i], ranges[i+ 1]])
        if _List[ranges[i]] is None :
            values.append(None)
        else :
            values.append(_List[ranges[i]])

    return slices, values


#For better traceability of the data : use splices builder and it's wrapper nan_paded_array for easier use.
#Supports up to 2D arrays with first dimension being time. (or expecting every column in the second dimension to be consistant with the first regarding nan positions)
class splicedArrayBuilder():
    #Nan spliced Array Builder
    def __init__(self,array,edges = None):
        if edges is not None :
            self.edges = edges
        else :
            self.edges = self.get_edges(array)
        self.dtype = array.dtype

    def get_edges(self,array):
        return self._edges_2D(array)

    def _ensure_2D(self,array):
        if len(array.shape) < 2 :
            array = np.expand_dims(array,axis = 1)
        return array

    def _edges_2D(self,array):
        array = self._ensure_2D(array)
        edges = []
        for dim in range(array.shape[1]):
            edges.append(get_array_splices_infos(array[:,dim],np.nan))

        #shortest_edges = [[None,None]] * len(edges[0][0])
        if len(edges) > 1 :
            for index,edge in enumerate(edges) :
                if index > 0:
                    if len(edge[0]) != len(edges[index-1][0]):
                        raise ValueError("Not the same number of slices in all the dimensions")
                    for subindex, ed in enumerate(edge[0]):
                        if ed == edges[index-1][0][subindex] :
                            continue
                        raise ValueError("Edges are different between dimensions")
        return edges[0]

    def is_built(self,array):
        if self.edges[0][-1][1] != array.shape[0]:
            return False
        return True

    def unbuild(self,array):
        if not self.is_built(array):
            return array
        else :
            array = self._ensure_2D(array)

            ndim_array = None
            for dim in range(array.shape[1]):
                reconstructed_array = np.empty((0,))
                for index, item in enumerate(self.edges[0]):
                    if not np.isnan(self.edges[1][index]):
                        reconstructed_array = np.append(reconstructed_array,array[item[0]:item[1],dim])
                if ndim_array is None :
                    ndim_array = reconstructed_array
                    continue
                ndim_array = np.stack((ndim_array,reconstructed_array),axis = 1)

            return ndim_array.squeeze().astype(array.dtype)

    def build(self,array,**kwargs):
        if self.is_built(array):
            return array
        else :
            if kwargs.get("fix_side","end") != "none":
                #autofix = true to fix the shape of the array back to the shape it had before removing nans.
                #It will fix it by adding as many nan as necessary, either at the end or the start of the array.
                #this can be tuned with fix_side = 'end' or 'start'
                fix_nan_amount = self.unbuilt_size - array.shape[0]
                if fix_nan_amount > 0 :
                    array = self.append_nan(array,fix_nan_amount,side=kwargs.get("fix_side","end"))

            array = self._ensure_2D(array)
            ndim_array = None
            for dim in range(array.shape[1]):
                cursor = 0
                reconstructed_array = np.empty((0,))
                for index, item in enumerate(self.edges[0]):
                    if np.isnan(self.edges[1][index]):
                        reconstructed_array = np.append( reconstructed_array, np.full((item[1]-item[0],),np.nan) )
                    else :
                        slice_end = cursor + (item[1] - item[0])
                        reconstructed_array = np.append( reconstructed_array,  array[ cursor : slice_end , dim]  )
                        cursor =  slice_end

                if ndim_array is None :
                    ndim_array = reconstructed_array
                    continue
                ndim_array = np.stack((ndim_array,reconstructed_array),axis = 1)

            return ndim_array.squeeze().astype(array.dtype)

    @property
    def unbuilt_size(self):
        first_dim_size = sum([(self.edges[0][index][1] - self.edges[0][index][0]) for index in range( len(self.edges[0]) ) if not np.isnan(self.edges[1][index]) ])
        return first_dim_size

    @property
    def nb_notnan_chunks(self):
        non_nan_chunks = np.where(np.isnan(self.edges[1]) == False)[0].tolist()
        return len(non_nan_chunks)

    @property
    def has_one_chunk(self):
        chunks = self.nb_notnan_chunks
        return False if chunks == 0 or chunks > 1 else True

    @property
    def is_nan(self):
        if len(self.edges[1]) == 1 and np.isnan(self.edges[1]):
            return True
        return False

    def append_nan(self, array, nan_nb, **kwargs):
        #Add nan after or at the begining of the array
        #(do not check for nan blocks = expected to be used on unbuilt arrays)
        side = kwargs.get("side",'end')
        if side != "end" and side != "start":
             raise ValueError("If side is provided, it can either be 'end' or 'start'")

        return self._append_2D(array,np.full((nan_nb,),np.nan),side)
        #if case == 'end' :
        #    return np.append(array,np.full((nan_nb,),np.nan))
        #if case == "start" :
        #    return np.append(np.full((nan_nb,),np.nan),array)

    def _append_2D(self,array,appendix,side = "end"):
        #performs the addition securely for consistancy over second dimension if it exists
        array = self._ensure_2D(array)
        ndim_array = None
        for dim in range(array.shape[1]):
            if side == "end":
                _temp = np.append(array[:,dim],appendix)
            if side == "start":
                _temp = np.append(appendix,array[:,dim])

            if ndim_array is None :
                ndim_array = _temp
                continue
            ndim_array = np.stack((ndim_array,_temp),axis = 1)

        return ndim_array.squeeze().astype(array.dtype)


    def shift_index(self,array):
        #used to recalculate the built equivalent indices
        #of any array that extracted indices from the unbuilt array
        outlist = []
        for item in array:
            offset = 0
            for indiced, aslice in enumerate(self.edges[1]):
                if np.isnan(aslice):
                    offset = offset + self.edges[0][indiced][1]
                    continue
                if self.edges[0][indiced][0]-offset <= item < self.edges[0][indiced][1]-offset :
                    outlist.append(item+offset)
                    break
        return np.array(outlist).reshape(array.shape)


    #todo : a method to check if values in the array are a certain number and replace them

    #todo : a method to check if the distance between two consecutive values in the array is not too great and if so, replace the spot with a too great value with a nan

class splicedArray(np.ndarray):
    """
    Examples:
        '''python

            vanilla_numpy_array = np.array([np.nan,1,2,3,3,np.nan,np.nan,23,32,np.nan,2212,2,2,332])
            better_array = splicedArray(test)
            print(better_array) #this is still a numpy array...  but boosted with special abilities :
            print(better_array.a) #use array.a to get only non_nan values off the array. Usefull to feed into functions that do not cope well with nans.
            To get back the nan at the places of the original array into itself, or an array of the same shape where values have been transformed by any function, use either

            transformed_better_array = better_array( a_function_not_working_with_nans( better_array.a ) )
            print(toast(toast.a)) #equivalent of doing that.

        '''

    Tip:
        When using the call ``better_array(array)`` to put back nan in place,
        if the shape has changed on one dimension, for example,
        because of a numerical derivative operation, the output array will be
        given back it's original shape, appendded at the end by as much np.nan as
        necessary.
        This can be adjusted by adding a second optionnal parameter, with value,
        ``"start"``,``"end"``,or ``"none"``. Default is ``"end"``
        Example :
        ```python
            better_array(array,"none") #will not be shape-fixed
            better_array(array,"start") #will not shape-fixed by addind np.nan at the start IF NECESSARY.
        ```

    """

    def __new__(cls, input_array, **kwargs):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance

        obj.splices = splicedArrayBuilder(input_array)
        # Finally, we must return the newly created object:
        return obj#, kwargs

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments

        if obj is None: return
        self.splices = getattr(obj, 'splices', None)

    @property
    def a(self):
        """
        Extracts only the non_nan values off the array.

        Returns:
            np.array: An array with no nan inside.

        """
        self = self._recompute_npa
        return self.splices.unbuild(self)

    def __call__(self,array=None,fix_side = "end"):
        self = self._recompute_npa
        if array is None :
            return self.splices.build(self)# this condition has no use by the way,
            # since we never set unbuild self in this class, when we do,
            # we only return a copy of a standard numpy array, without .a and not callable
        return splicedArray(self.splices.build(array))
        #by default, this returns an array with the same shape of  the original by adding nan
        #at the end of the last numeral block if shape is shorter than original

    @property
    def _recompute_npa(self):
        #just a self check in case unpickling didn't called __new__ or
        #deserialization did weird things silently and splices attibute is gone
        try :
            self.splices
            return self
        except AttributeError :
            return splicedArray(self)

if __name__ is "__main__" :

    test = np.array([np.nan,1,2,3,3,np.nan,np.nan,23,32,np.nan,2212,2,2,332])
    toast = splicedArray(test)
    print(toast)
    print(toast.a)
    print(toast(toast.a))
    print(toast(toast.a[:-5]))