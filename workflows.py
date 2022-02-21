# -*- coding: utf-8 -*-
"""Boilerplate:

Created on Tue Feb 16 18:54:55 2021
@author: Timothe
"""

import os,sys,inspect
import warnings
from datetime import datetime

from structs import TwoLayerDict
from strings import quick_regexp

import pathes

try :
    import numpy as np
except TypeError as e :
    warnings.warn("numpy installation was not detected, some functions from workflow module will be deactivated")
    np = e
    
# @dataclass
# class Point:
#     x: float
#     y: float
#     z: float = 0.0
    
    
def get_currentfile_git_repo_metadata(input_path = None):
    if input_path is None :
        input_path = inspect.stack()[1][1]
        if 'ipython' in input_path and input_path[0] == '<':
            raise NameError("cannot get file path of current executed script from a jupyter call; ")
    import git
    try :
        repo = git.Repo(input_path, search_parent_directories=True)
    except git.InvalidGitRepositoryError :
        warnings.warn(f"No git repository was found here or upstream : {input_path}")
        return None
    repo_data = {"file_called" : input_path,"path_on_disk":repo.git_dir, "name":repo.remotes.origin.url.split('.git')[0].split('/')[-1], "branch": repo.active_branch.name, "author": repo.remotes.origin.url.split('.git')[0].split('/')[-2], "commit": repo.active_branch.commit.hexsha, "commiter": repo.active_branch.commit.committer.name, "commiter_email": repo.active_branch.commit.committer.email}
    return repo_data


def get_all_working_vars():
    import types
    working_vars = []
    globalscope = vars(sys.modules["__main__"])
    varnames = list(globalscope.keys())
    patterns = [r"^__.*$",r"^_.*$",r"^__.*__$"]#(leading or trailing underscores are used for private or reserved variables naming)
    rejected_names = ["In","Out"]# variables defined by Ipython internally
    ### Here we will test if variable match conditions, if so, we reject it, else, we keep it.
    for var in varnames:
        ### Is this a module or package
        try :
            globalscope[var].__package__
            continue
        except AttributeError:
            pass
        ### Is this a function
        try :
            globalscope[var].__module__
            continue
        except AttributeError:
            pass
        ### Is this a generator
        if isinstance(globalscope[var],types.GeneratorType) :
            continue
        exit = False
        ### Is this a rejected variable by name
        if var in rejected_names :
            continue
        ### Is this a private or reserved variable (leading or trailing underscores)
        for pattern in patterns :
            if quick_regexp(var,pattern):
                exit = True
                break
        if exit :
            continue
        
        ### Hurray, we found one interesting variable, keeping it
        print(var)
        working_vars.append(globalscope[var])
    return working_vars


def get_glob_varname(var):
    globalscope = vars(sys.modules["__main__"])
    return [k for k,v in globalscope.items() if v is var][0]

def get_main_filename():
    globalscope = vars(sys.modules["__main__"])   
    if "__filename__" in globalscope.keys():
        return globalscope["__filename__"]
    if "__name__" in globalscope.keys():
        return globalscope["__filename__"]

from fileio import ConfigFile
class CachedVariables(ConfigFile):
    
    
    def _get_outside_caller_info(self):
        """
        Iteratively scans the caller's parents and stops at first encounter of a function coming from another file than this one (the deepest outside caller)
        Returns it' file name and the function that "asked" for a raise if a module wasn't present.
    
        Returns:
            dict
    
        """
        start_depth = 2
        for depth in range(start_depth,len(inspect.stack())):
            #fullpath = inspect.stack()[depth][1]
            fullpath = inspect.stack()[depth][0].f_code.co_filename
            if not "__packages__" in fullpath:
                try :#If caller is a classmethod
                    caller_object = str(inspect.stack()[depth][0].f_locals["self"].__class__.__name__)+'.'+str(inspect.stack()[depth][0].f_code.co_name)
                except KeyError :#if caller is a simple function
                    caller_object = str(inspect.stack()[depth][3])
                
                return { "caller_function_name" : caller_object, "caller_file_name" : fullpath}
        return { "caller_function_name" : "unknown", "caller_file_name" : "unknown"}

    def _add_meta_section(self,description):
        self._section = "meta"
        self._enter_var_init
        self["creator_full_path"]= inspect.stack()[2][1]
        self._enter_var_init
        try :#If caller is a classmethod
            self["creator_object"] = str(inspect.stack()[2][0].f_locals["self"].__class__.__name__)+'.'+str(inspect.stack()[2][0].f_code.co_name)
        except KeyError :#if caller is a simple function
            self["creator_object"] = inspect.stack()[2][3]
        self._enter_var_init
        self["creation_date"] = datetime.now().strftime("%y-%m-%d %H:%M:%S")
        self._enter_var_init
        self["description"] = description if description is not None else None
        self._section = "current"

    def _add_readme_section(self):
        self._section = "readme"
        self._enter_var_init
        self["help_section_current"] ="The current section contains the values of variables last used or currentely in use."
        self._enter_var_init
        self["help_section_meta"] = "The meta section contains information for you, reader, to determine if the file can be removed (very old last_used date) and by wich program it was used (caller_full_path and caller_object)"
        self._enter_var_init
        self["help_section_date#name"] = "The sections with names composed of a [date#name] are sections that contains saved cached variables values and that can be retrieved back in the current section by calling `retrieve` with a name or a date."
        self._section = "current"
        
    def __init__(self, **kwargs):
        """
        Handle file and ram representation of user selected current working variables
        that needs to be saved to later execution sessions, to improve work efficiency
        and user experience, mainly intended to use with GUI work variables.

        Args:
            **kwargs (optionnal):
                - description (`str`):


                - cache_dir_path (`str`):
                    path to the .ini file if you wish to save it in a custom location.
                    By default, it will be saved in the pGenUtils package, inside the __varcache__ folder.

                - distinguisher (`str`):
                    Warning :
                        Advanced user

                    If you wish to have the ability to have several variables caches configurations
                    for a class implementing a CachedVariables object, and if that class is called from several functions,
                    you will need to disambiguate the .ini file with such distinguisher.

                    Question:
                        TODO
                        Add the ability to simply roll back the caller to the top,
                        so the user doesn't have to specify itself subjective distinguisher
                        strings in the code depending on if it has been called from here or there.





        Returns:
            CachedVariables : An instance of the class


        Info:
            how to use inspect:
            ```python
            import inspect

            inspect.stack first index content :
            inspect.stack()[0] #callee
            inspect.stack()[1] #caller
            inspect.stack()[2] #caller's caller etc

            #inspect.stack second index content, for the caller in that case
            frame,filename,line_number,function_name,lines,index = inspect.stack()[1][1]
            ```

        """
        """

            Cache section to use for a given script (to separate variables used
            for different scripts in the same cache file).
        cache_filename : str, optional
            Optionnal filename. The default is "saved_cache.vars".
            Can contain only the filename, and supply the folder
            in cache_dir_path, or can contain the whole concatenated path.
            In that case, leave the parameter cache_dir_path to None.
        cache_dir_path : str, optional
            The default is None.
            If None, the path is automatically set to the __varcache__ folder
            inside the main library folder.

        Returns
        -------
        cached_execution_variables object.

        Available methods bound to that object :
            - individual key getters and setters :
                ( value = object["item"]  or bject["item"] = value )
                that will automatically resolve if the kei is available in ram
                or fetch it on .vars file attached to the object.
            - pull() :
                fetches all available variables in section in attached file
                to the ram. Can be usefull at start if all variables are necessary,
                to avoid loading them individually.
            - fetch(key) :
                updates the ram of unique or list of keys supplied to the function
                with values stored in the attached file.
                Same as pull except if is selective to variables supplied by user.
            - refresh() :
                same as pull except it selective only to keys already
                stored in ram (ie : keys already used during current session,
                for efficiency purposes)
            - push() :
                updates or add values of all keys stored in ram to the attached file
        """

        cache_dir_path = kwargs["cache_dir_path"] if kwargs.get("cache_dir_path") is not None else os.path.join(os.path.dirname(__file__), "__varcache__")
        pathes.is_or_makedir(cache_dir_path)

        name_distinguisher = "#" + kwargs["distinguisher"] if kwargs.get("distinguisher") is not None else ""

        if not os.path.exists(cache_dir_path):
            os.makedirs(cache_dir_path)

        if name_distinguisher != "" :
            name_distinguisher = '#' + name_distinguisher
            
        if kwargs.get("cache_filename") is not None :
            self._filename = kwargs["cache_filename"]
        else :
            self._filename = os.path.splitext( os.path.basename(inspect.stack()[1][1]) )[0] +"."+ inspect.stack()[1][3][1:-1] + name_distinguisher + ".ini"
        self._dirname = cache_dir_path
        self._fullpath = os.path.join(self._dirname,self._filename)
        
        super().__init__(self._fullpath)

        self._add_readme_section()
        self._add_meta_section(kwargs.get("description",None))
        self._section = "current"

        #CheckConfigFile(self.fullpath, self.section)
        #super().__init__()

    @property
    def _enter_var_init(self):
        self._initializing_var_mode = True

    @property
    def _exit_var_init(self):
        self._initializing_var_mode = False

    @property
    def _is_init(self):
        if self._initializing_var_mode :
            return True
        return False


    
    def _key_resolver(self,key):
        if isinstance(key,(list,tuple)):
            return key
        return (self._section,key)

    def __getitem__(self, key):
        if self._is_init:
            self._exit_var_init
        return super().__getitem__(self._key_resolver(key))

    def __setitem__(self, key, value):
        setkey = True
        if self._is_init :
            try :
                super().__getitem__(self._key_resolver(key))
                setkey = False
            except :
                setkey = True
            self._exit_var_init
        if setkey :
            super().__setitem__(self._key_resolver(key),value)
            
    def _write_callback(self):
        self._update_timestamp()
    
    def _update_timestamp(self):
        TwoLayerDict.__setitem__(self,("meta","last_used"),datetime.now().strftime("%y-%m-%d %H:%M:%S"))
        call_info = self._get_outside_caller_info()

        TwoLayerDict.__setitem__(self,("meta","last_caller_full_path"), call_info["caller_file_name"] )
        TwoLayerDict.__setitem__(self,("meta","last_caller_objet"), call_info["caller_function_name"] )

    @property
    def init(self):
        self._enter_var_init
        return self
    
    def set_working_section(self,section):
        self._section = section

    def save(self,section = None):
        """

        """
        sel_section = self._section if section is None else section
        backup_section = datetime.now().strftime("%y%m%d") + "#" + sel_section
        for key in self[sel_section,:].keys():
            self[backup_section,key] = self[sel_section,key]
        self.pop((sel_section,slice(None,None,None)))

    def retrieve(self,date=None,section = None):
        """

        """
        sel_section = self._section if section is None else section
        backup_section = self._find_most_recent_backup(sel_section) if date is None else date + "#" + sel_section
        for key in self[backup_section,:].keys():
            self[sel_section,key] = self[backup_section,key]
    
    def _find_most_recent_backup(self,section):
        dates = []
        for sec in self.sections():
            parts = sec.split("#")
            if len(parts) == 1:
                continue
            if parts[1] == section:
                dates.append(parts[0])
        date = sorted(dates,key=lambda content : int(content),reverse = True)[0]
        return date + "#" + section
        
def ProgressBarImage(Fraction):
    try :
        raise np("Numpy must be installed in order to use this function")
    except TypeError :
        pass
    if Fraction == 1:
        blue = np.zeros((10,100,3))
        blue[:,:,2] = np.ones((10,100))
        return(blue)
    elif Fraction == 0:
        blue = np.zeros((10,100,3))
        return(blue)
    else:
        blue = np.zeros((10,100,3))
        blue[:,:,2] = np.ones((10,100))
        blue[:,int(Fraction*100):,:] = np.ones((10,100-int(Fraction*100),3))
        return(blue)

def sizeof_fmt(num, suffix='oct'):
    ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
    for unit in ['','K ','M ','G ','T ','P ','E ','Z ']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)

def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances or kwargs.get("regen",False) is True:
            kwargs.pop("regen",None)
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

if __name__ == "__main__" :

    #parse_mkdocs_yml(test_path , "")


    test = CachedVariables(description="This is a test description")



    test.init["a_key"] = "vola"
    test["a_key"] = "value"
    test.init["a_key"] = "SHIT"
    print(test["a_key"])


    print(test["a_key"])
    test["a_key"] = 1332
    import numpy as np
    test["another_key"] = np.array([[7,8],[4,1]])
    print(test["a_key"])

    test = np.zeros((1000,1000,100),dtype = np.float64)

    sys.exit()

    for name, size in sorted(((name, sys.getsizeof(value)) for name, value in globals().items()),key= lambda x: -x[1])[:]:
        print("{:>30}: {:>8}".format(name, sizeof_fmt(size)))