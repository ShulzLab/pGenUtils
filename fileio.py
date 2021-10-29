# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Jun  7 15:37:56 2021

@author: Timothe
"""


import os, sys
import pickle as _pickle
import configparser, json
import shutil, pathlib

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath("__filename__"))))
#print(os.path.dirname(os.path.dirname(os.path.abspath("__name__"))))
from structs import TwoLayerDict
import pathes






class Pickle():

    def __init__(self,path):
        self.path = path

    def load(self):
        if os.path.isfile(self.path):
            results = []
            with open(self.path,"rb") as f :
                while True :
                    try :
                        results.append(_pickle.load(f))
                    except EOFError :
                        break
                return results if len(results) > 1 else results[0]
        return None

    def dump(self,data,noiter = True):

        with open(self.path,"wb") as f :
            if isinstance(data, (list,tuple)) and not noiter:
                for item in data :
                    _pickle.dump(item,f)# protocol = _pickle.HIGHEST_PROTOCOL ?
                return None
            _pickle.dump(data,f)

class ConfigFile(TwoLayerDict):
    def __init__(self, path, **kwargs):
        """
        A class to access config files through an object with indexing,
        either for geting or seting values.
        Seamless and easy integration in code, ability to load or set multiple
        variables at once for more readability when using in static environments.

        (e.g. functions or simple classes)

        If not existing, the file will be created (but folder must exist)
        when key values are assigned.

        Python standard variables are supported, as well as numpy arrays, internally
        represented as nested lists. Avoid using complex numpy structures as they could be
        erroneously loaded from file. (no specific dtypes support #TODO)

        Parameters
        ----------
        path : str
            Path to the config file.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        A variable which is also a handle to the file.
        Can be used to load values with tho text indexes (two layer dictionary)
        or set values in the same way (immediately applies changes to the text file on setting variable value)
        """
        self.path = path
        self.cfg = configparser.ConfigParser()
        self.last_mtime = None
        self.cursor = None
        super(TwoLayerDict, self).__init__({})
        self._read_if_changed()

    def couples(self):
        sections = self.sections()
        result = []
        [ result.extend( [ ( section, param ) for param in self.params(section) ] ) for section in sections ]
        return tuple(result)

    def sections(self):
        return self.cfg.sections()

    def params(self,section = None):
        return self.cfg.options(section)

    def _read_if_changed(self):
        if self._filechanged :
            self._read()

    def __getitem__(self,index):
        self._read_if_changed()
        try :
            return super().__getitem__(index)
        except KeyError as e:
            raise KeyError(f"Key and section pair may not exist in the config structure. Cannot access value. Key causing the issue : {e}")


    def __setitem__(self,key,value):
        super().__setitem__(key,value)
        self._write()

    def _create_sections(self):
        for section in self.keys():
            if not section in self.sections():
                self.cfg.add_section(section)

    def _write(self):
        """
        Question:
            #TODO
            Make sure we can load many variables types correctly by saving them with pickle dumping in str format. And loading from str with pickle, instead of creating a custom "key type" with json.
            Or see if we can jsonize pandas dataframes easily. Could be an idea too. In that case though, we need to jsonize arrays in a better way, including dype. Need to see if numpy doesn't have that ability built in.'
        Returns:
            TYPE: DESCRIPTION.

        """
        def jsonize_if_np_array(array):
            if (array.__class__.__module__, array.__class__.__name__) == ('numpy', 'ndarray'):
                value = ["np.ndarray", array.tolist()]
                return value
            return array

        def ini_compat_json_dumps(_value):
            return json.dumps(_value.replace("%","%%"))

        self._create_sections()
        for section in self.keys():
            for param in super().__getitem__((section,slice(None))).keys():
                value = jsonize_if_np_array(super().__getitem__((section,param)))
                self.cfg.set(section,param,ini_compat_json_dumps(value))
        with open(self.path, 'w') as configfile:
            self.cfg.write(configfile)

    def _read(self):
        self.cfg.read(self.path)
        super().clear()
        for sec in self.sections():
            super().__setitem__(sec , {param: self._getasvar(sec,param) for param in self.params(sec) } )

    def _getasvar(self,section,param):

        def unjsonize_if_np_array(array):
            if isinstance(array,list):
                if len(array) == 2 :
                    if array[0] == "np.ndarray":
                        import numpy as np
                        value = np.array(array[1])
                        return value
            return array

        try :
            #print(section,param)
            #print(self.cfg.get(section,param))
            val =  json.loads(self.cfg.get(section,param))
            val =  unjsonize_if_np_array(val)
        except configparser.NoOptionError:
             return None
        if isinstance(val,str):
            if val[0:1] == "f" :
                val = val.replace("''",'"')
        if isinstance(val,list):
            if len(val) == 2 :
                if val[0] == "np.ndarray":
                    val = np.array(val[1])
        return val

    @property
    def _filechanged(self):
        try :
            filestatus =  os.stat(self.path).st_mtime
            if self.last_mtime is None or self.last_mtime != filestatus:
                self.last_mtime = filestatus
                return True
        except FileNotFoundError :
            pass
        return False


def paste_dir_content(src, dst, include_root_files : bool = True , copy : bool = True ):
    def recursive_copy(s,d, symlinks=False, ignore=None):
        try :
            shutil.copytree(s, d, symlinks, ignore) if os.path.isdir(s) else shutil.copy2(s, d)
        except FileExistsError :
            pass

    operating_function = recursive_copy if copy else shutil.move

    if pathlib.Path(src).drive == pathlib.Path(dst).drive :
        def produce_distant_path(src_name):
            return pathes.switch_root(src_name,src,dst)
    else :
        def produce_distant_path(src_name):
            return os.path.join(dst, pathes.remove_common_prefix(src_name,src))

    def operate_on_items(item_producing_function):
        for src_item in item_producing_function(src):
            dst_item = produce_distant_path(src_item)
            pathes.is_or_makedir(os.path.dirname(dst_item))
            operating_function(src_item, dst_item)

    operate_on_items(pathes.list_toplevel_dirs)
    if include_root_files :
        operate_on_items(pathes.list_toplevel_files)

# def __FilepathResolverConfigFile(file_path,**kwargs):
#     foldup = kwargs.get("foldup",False)
#     if foldup :
#         file_path = UpFolder(file_path,foldup)
#     filename = kwargs.get("filename","config.txt")
#     if filename != "config.txt" or os.path.splitext(file_path)[0] == file_path :
#         file_path = os.path.join(file_path, filename)

#     if not os.path.isfile(file_path) :
#         raise OSError(f"File not found : {file_path}")

#     return file_path

# def GetAllParamsConfigFile(file_path,section,**kwargs):
#     file_path = __FilepathResolverConfigFile(file_path,**kwargs)
#     cfg = configparser.ConfigParser()
#     cfg.read(file_path)
#     return cfg.options(section)

# def GetAllSectionsConfigFile(file_path,**kwargs):
#     file_path = __FilepathResolverConfigFile(file_path,**kwargs)
#     cfg = configparser.ConfigParser()
#     cfg.read(file_path)
#     return cfg.sections()

# def CheckConfigFile(file_path,sections,**kwargs):
#     file_path = __FilepathResolverConfigFile(file_path,**kwargs)
#     cfg = configparser.ConfigParser()
#     cfg.read(file_path)

#     if not isinstance(sections , list):
#         sections = [sections]

#     for section in sections :
#         if not cfg.has_section(section):
#             cfg.add_section(section)

#     with open(file_path, "w") as file_handle :
#         cfg.write(file_handle)

# def LoadConfigFile(file_path,section,param,**kwargs):
#     file_path = __FilepathResolverConfigFile(file_path,**kwargs)
#     cfg = configparser.ConfigParser()
#     cfg.read(file_path)
#     try :
#         val =  json.loads(cfg.get(section,param))
#     except configparser.NoOptionError:
#         return None
#     if isinstance(val,str):
#         if val[0:1] == "f" :
#             val = val.replace("''",'"')
#     if isinstance(val,list):
#         if len(val) == 2 :
#             if val[0] == "np.ndarray":
#                 import numpy as np
#                 val = np.array(val[1])
#     return val

# def WriteToConfigFile(file_path,section,param,value,**kwargs):
#     file_path = __FilepathResolverConfigFile(file_path,**kwargs)
#     cfg = configparser.ConfigParser()
#     cfg.read(file_path)
#     if (value.__class__.__module__, value.__class__.__name__) == ('numpy', 'ndarray'):
#         value = ["np.ndarray", value.tolist()]
#     cfg.set(section, param , json.dumps(value))

#     with open(file_path, "w") as file_handle :
#         cfg.write(file_handle)

if __name__ == "__main__":

    import sys

    test = ConfigFile(r"\\157.136.60.15\EqShulz\Timothe\DATA\BehavioralVideos\Whole_area\Low_speed_triggered\gateway.ini")
    print(test["outer_architecture","dateformat"])
    sys.exit()


    import numpy as np
    #test = ConfigFile(r"\\157.136.60.15\EqShulz\Timothe\DATA\DataProcessing\Expect_3_mush\CrossAnimals\SpatialScale\scale.txt")
    test = ConfigFile(r"test.config")
    test["foo","zbo"]=12
    test["foo","zbi"]="adas"
    test["flee","moulaga"]=142.13
    test["flee","ratata"]= np.array([[1,3],[4,56]])
    print(test["flee","ratata"])

    print(test.couples())