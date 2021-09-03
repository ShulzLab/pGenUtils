# -*- coding: utf-8 -*-
"""Boilerplate:

Created on Tue Feb 16 18:54:55 2021
@author: Timothe
"""

import os,sys,inspect
import warnings
from datetime import datetime

from fileio import ConfigFile
import pathes

try :
    import numpy as np
except TypeError as e :
    warnings.warn("Numpy must be installed in order to use UX functions")
else :

    class CachedVariables(ConfigFile):

        @property
        def _add_readme_section(self):
            self._enter_var_init
            self["help_section_current"] ="The current section contains the values of variables last used or currentely in use."
            self._enter_var_init
            self["help_section_meta"] = "The meta section contains information for you, reader, to determine if the file can be removed (very old last_used date) and by wich program it was used (caller_full_path and caller_object)"
            self._enter_var_init
            self["help_section_date#name"] = "The sections with names composed of a [date#name] are sections that contains saved cached variables values and that can be retrieved back in the current section by calling `retrieve` with a name or a date."

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
                        By default, it will be saved in the LabUtils package, inside the __varcache__ folder.

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
                - individual key getters and setters:
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
                    updates or add values of all keys stored in ram to the attached
                    file
            """
            cache_dir_path = kwargs["cache_dir_path"] if kwargs.get("cache_dir_path") is not None else os.path.join(os.path.dirname(__file__), "__varcache__")
            path.is_or_makedir(cache_dir_path)

            name_distinguisher = "#" + kwargs["distinguisher"] if kwargs.get("distinguisher") is not None else ""

            if not os.path.exists(cache_dir_path):
                os.makedirs(cache_dir_path)

            if name_distinguisher != "" :
                name_distinguisher = '#' + name_distinguisher
            self._filename = os.path.splitext( os.path.basename(inspect.stack()[1][1]) )[0] +"."+ inspect.stack()[1][3][1:-1] + name_distinguisher + ".ini"
            self._dirname = cache_dir_path
            self._fullpath = os.path.join(self._dirname,self._filename)

            super().__init__(self._fullpath)
            super().__setitem__(("meta","caller_full_path"),inspect.stack()[1][1])
            super().__setitem__(("meta","caller_object"),inspect.stack()[1][3])
            super().__setitem__(("meta","last_used"),datetime.now().strftime("%y-%m-%d %H:%M:%S"))
            super().__setitem__(("meta","description"),kwargs["description"]) if kwargs.get("description") is not None else None

            self._exit_var_init

            self._section = "readme"
            self._add_readme_section
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

        @property
        def init(self):
            self._enter_var_init
            return self

        def __getitem__(self, key):
            if self._is_init:
                self._exit_var_init
            return super().__getitem__((self._section,key))

        def __setitem__(self, key, value):
            setkey = True
            if self._is_init :
                try :
                    super().__getitem__((self._section,key))
                    setkey = False
                except :
                    setkey = True
                self._exit_var_init
            if setkey :
                super().__setitem__((self._section,key),value)

        def save(self):
            """
            Question:
                TODO
                Save function to save current values by putting them into a section named by date.
                Could be usefull to make sets of parameters that have been saved and can be easily switched to X or Y config, for user interfaces in particular.

            Returns:
                None.
            """
            pass

        def retrieve(self,date):
            """
            Question:
                TODO
                Retrieve function to load previous values by putting the section named by date if existing, into current section.

            Returns:
                None.
            """
            pass

    def ProgressBarImage(Fraction):

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