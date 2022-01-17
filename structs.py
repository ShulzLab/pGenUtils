# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Jun  7 15:43:06 2021

@author: Timothe
"""


####### CUSTOM TYPES AND OBJECTS

class sdict(dict):

    def __init__(self,value=None):
        """
        A class for a modified version of python built in dictionnary,
        with enhanced indexation abilities : get or set values with lists or ':' operator.
        This requires a more rigorous aproach regarding variable order while writing to it,
        but is this downside is neglected when used inside a class wich takes care of the acess,
        as in "TwoLayerDict" declared below.

        Parameters
        ----------
        value : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        Timothe Jost - 2021
        """
        if value is None:
            value = {}
        super(sdict, self).__init__(value)
        self._dyn_attrs = []
        #self._update_attrs()

    def _update_attrs(self):
        [ self.__delattr__(key) for key in self._dyn_attrs ]
        self._dyn_attrs = [ key for key in super(sdict, self).keys() ]
        [ self.__setattr__(key, super(sdict, self).__getitem__(key) ) if not isinstance( super(sdict, self).__getitem__(key),dict ) else self.__setattr__(key, sdict(super(sdict, self).__getitem__(key)) ) for key in self._dyn_attrs]

    @staticmethod
    def _assert_index_single(index):
        return True if isinstance(index,(str,int,float)) else False

    @staticmethod
    def _assert_index_iter(index):
        return True if isinstance(index,(list,tuple)) else False

    @staticmethod
    def _assert_index_dict(index):
        return True if isinstance(index,(dict,set)) else False

    @staticmethod
    def _assert_index_dotslice(index):
        if isinstance(index,slice):
            if index.start is None and index.step is None and index.stop is None :
                return True
            else :
                raise ValueError("Only ':' slice operator is allowed for whole selection as sliceable_dict is unordered")
        return False

    @staticmethod
    def _assert_key_match(subset,masterset):
        if set(subset) & (set(masterset)) != set(subset) :
            raise KeyError("A key provided for indexing doesn't exist in data")

    @staticmethod
    def _assert_iter_len_match(one,two):
        if not isinstance(one,(list,tuple)) or not isinstance(two,(list,tuple)) or len(one) != len(two) :
            raise ValueError("sizes must match")

    def __getitem__(self,index):
        if self._assert_index_single(index):
            return super().__getitem__(index)
        elif self._assert_index_iter(index):
            self._assert_key_match(index,self.keys())
            return sdict({ key : self[key] for key in index })
        elif self._assert_index_dotslice(index):
            return self
        raise TypeError(f"Unsupported indexer :{index}")

    def __setitem__(self,index,value):
        if self._assert_index_single(index):
            super().update({index:value})
        elif self._assert_index_iter(index):
            if self._assert_index_dict(value):
                self._assert_key_match(index,value.keys())
                [super(sdict, self).update({key : value[key]}) for ix, key in enumerate(index)]
            else :
                self._assert_iter_len_match(index,value)
                [super(sdict, self).update({key : value[ix]}) for ix, key in enumerate(index)]
        elif self._assert_index_dotslice(index):
            if self._assert_index_dict(value):
                self.clear()
                super().update(value)
            else :
                raise ValueError("A dictionnary must be provided when overwriting values with ':' slicing operator")
        else :
            raise TypeError(f"Unsupported indexer :{index}")
        #self._update_attrs()

    def update(self,*value):
        super().update(*value)
        #self._update_attrs()

    class _default_proxy():
        """
        Just an empty class to fake a default condition equal to no other possible value the user could enter.
        (because we want to preserve None as a possible user value in this case)
        """
        pass

    _default_holder = _default_proxy()#Placeholder for a "None" default arg value, to allow None or any other value as an optionnal argument
    def pop(self,value,default = _default_holder):
        _inner_default_holder = self._default_proxy()
        local_super = super()
        def _pop_helper(key,_default = _inner_default_holder):
            if not isinstance(default,sdict._default_proxy):
                return local_super.pop(key,default)
            else :
                return local_super.pop(key)
                
        if self._assert_index_single(value):
            retval = _pop_helper(value,default)
        elif self._assert_index_iter(value):
            retval = {val:_pop_helper(val,default) for val in value}
        elif self._assert_index_dict(value):
            iterkeys = list(value.keys())
            retval = {val:_pop_helper(val,value[val]) for val in iterkeys}
        elif self._assert_index_dotslice(value):
            iterkeys = list(self.keys())
            retval = {val:_pop_helper(val,default) for val in iterkeys}
            
        #self._update_attrs()
        return retval

    def __str__(self):
        return super().__str__()


class TwoLayerDict(sdict):
    def __init__(self,value=None):
        """
        A class for a forced two layer indexing dictionnary.
        Usefull to access config files with section param value architecture
        and read-write to them seamlessly from this python object as if it was
        only a nested dictionnary.
        Based on sdict and inheriting from it's indexation abilities.

        Parameters
        ----------
        value : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        Timothe Jost - 2021
        """
        if value is None:
            value = {}
        else :
            self._assert_two_layers(value)
        super(TwoLayerDict, self).__init__(value)

    @staticmethod
    def _assert_two_layers(value):
        if isinstance(value,TwoLayerDict):
            return
        if not isinstance(value,dict):
            raise TypeError("A two layer dictionnary must be dictionnary")
        for key in value.keys():
            if not isinstance(value[key],dict):
                raise ValueError("Not enough layers")

    @staticmethod
    def _assert_index(index):
        if not isinstance(index,(list,tuple)) or len(index) != 2:
            if isinstance(index,(str,int)):
                return index,slice(None,None,None)
            elif isinstance(index,slice) and index.start is None and index.step is None and index.stop is None :
                return slice(None,None,None), slice(None,None,None)
            else :
                raise ValueError("TwoLayerDict is rigid and only supports two str indices")
        return index[0],index[1]
    
    
    def pop(self, index):
        outindex, inindex = self._assert_index(index)
        newvalue = sdict(super().__getitem__(outindex))
        retval = newvalue.pop(inindex)
        TwoLayerDict.__setitem__(self,(outindex,slice(None)),newvalue)
        return retval
    
    def __getitem__(self,index):
        outindex, inindex = self._assert_index(index)
        return sdict(super().__getitem__(outindex))[inindex]

    def __setitem__(self, index, value):
        outindex, inindex = self._assert_index(index)
        if super()._assert_index_single(outindex):
            temp = sdict()
            temp[inindex] = value
            if not outindex in self.keys() or super()._assert_index_dotslice(inindex):
                temp = sdict()
                temp[inindex] = value
                super().__setitem__(outindex,temp)
            else :
                old = sdict(super().__getitem__(outindex))
                super().__setitem__(outindex , {**old , **temp})

        elif super()._assert_index_dotslice(outindex):
            if super()._assert_index_dict(value):
                self.clear()
                super().update(value)
        else :
            raise(f"Unsupported indexer :{index}")

    def assign(self,outer,inner,value):
        if outer in super().keys():
            _temp = super().__getitem__(outer)
            _temp.update({inner:value})
            super().update({outer:_temp})
        super().update({outer:{inner:value}})

    def get(self,outer,inner,default = None):
        try :
            return super().__getitem__(outer)[inner]
        except KeyError:
            return default

    def update(self,value):
        self._assert_two_layers(value)
        value = TwoLayerDict(value)
        for key in value.keys():
            pass

    def __str__(self):
        return str([ str(key) + " : "+ super(TwoLayerDict, self).get(key).__str__() for key in super(TwoLayerDict, self).keys() ])

    def __repr__(self):
        return self.__str__()


################# USEFULL METHODS


def get_properties_names(cls):
    """
    Get a list of all the names of the properties of a given class.
    (usefull for copying all variables/parameters of an object programatically with eval)

    Parameters
    ----------
    cls : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        All properties that are not callable
        (= most of the existing variables except some dumb variables like the
         callable ones i created, (like nan_padded_array).
    """
    def stringiscallable(string,cls):
        return callable(eval(f"cls.{string}"))
    return [ a for a in dir(cls) if not a.startswith('__') and not stringiscallable(a,cls) ]


class func_io_typematch():
    """Converts a type back to the one it had entering a function.
    """
    def __init__(self,*args):
        self.casts = [type(arg) for arg in args]

    def cast(self,*args):

        if len(args) != len(self.casts):
            raise ValueError("Argument amount lengths must match between construction and cast call")

        try :
            return [self.casts[index](args[index]) for index, _ in enumerate(args) ] if len(args)>1 else self.casts[0](args[0])
        except Exception as e:
            raise TypeError(f"Cannot convert this specific type back.\nOriginal error : {e}")
            #return args if len(args)>1 else args[0]


if __name__ == "__main__" :
    pass