
import warnings, os, inspect

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

_called_dep_message = f"""The function : {color.BOLD + color.BLUE}{'{caller_function_name}'}(){color.END}
of the submodule : {'{caller_file_name}'} of pGenUtils, requires the optionnal package : {'{package_name}'}
""" 

_install_dep_message = """If required, you can install {package_name} in your environment with : 
{package_install_command}\n
({package_website})\n
"""

_missing_dep_warn_message = """The package {package_name} is missing and required for some functions of the submodule {caller_file_name} of pGenUtils. 
You won't be able to use these functions.\n
"""

_dependancies_data = {"default" : 
                      {"installs" : None,
                       "website" : None
                          },
    
                      "rasterio": 
                          {"installs" : ["conda install rasterio","pip install rasterio"], 
                           "website" : "https://rasterio.readthedocs.io/en/latest/installation.html",
                           },
                               
                      "sqlalchemy":
                          {"installs" : ["conda install -c anaconda sqlalchemy","pip install SQLAlchemy"], 
                           "website" : "https://www.sqlalchemy.org/library.html#tutorials"},
                      }

    
def get_outside_caller_info():
    """
    Iteratively scans the caller's parents and stops at first encounter of a function coming from another file than this one (the deepest outside caller)
    Returns it' file name and the function that "asked" for a raise if a module wasn't present.

    Returns:
        dict

    """
    sdepth = 2
    current_file_name = os.path.basename(inspect.stack()[0][1])
    for depth in range(sdepth,len(inspect.stack())):
        temp_filename = os.path.basename(inspect.stack()[depth][1])
        if current_file_name != temp_filename:
            return { "caller_function_name" : inspect.stack()[depth][3], "caller_file_name" : temp_filename}

def called_dependancy_message(dep_placeholder):   
    message_format_pieces = {"package_name" : dep_placeholder.package_name}
    message_format_pieces.update(get_outside_caller_info())
    
    return _called_dep_message.format(**message_format_pieces)

def missing_dependancy_warning_message(dep_placeholder):
    message_format_pieces = {"package_name" : dep_placeholder.package_name}
    message_format_pieces.update(get_outside_caller_info())
        
    return _missing_dep_warn_message.format(**message_format_pieces)

def install_dependancy_message(dep_placeholder):
    if _dependancies_data[dep_placeholder.package_selector]["installs"] is None or _dependancies_data[dep_placeholder.package_selector]["website"] is None :
        return ""
    message_format_pieces = {"package_name" : dep_placeholder.package_name}
    message_format_pieces["package_website"] = _dependancies_data[dep_placeholder.package_selector]["website"]
    or_list = ["\nor\n"]*(len( _dependancies_data[dep_placeholder.package_selector]["installs"] )-1)+['']
    message_format_pieces["package_install_command"] = ''.join(  [ "\t- " + item + str(conj_coord) for item, conj_coord in zip(_dependancies_data[dep_placeholder.package_selector]["installs"],or_list) ] ) 

    return _install_dep_message.format(**message_format_pieces)
        
def dep_miss_warning(dep_placeholder):
    warnings.warn( missing_dependancy_warning_message(dep_placeholder) + str(dep_placeholder) + install_dependancy_message(dep_placeholder) )
    
def dep_miss_raising(dep_placeholder):
    raise ImportError( called_dependancy_message(dep_placeholder) + str(dep_placeholder) + install_dependancy_message(dep_placeholder) )
    
    
class dependancy_placeholder(ImportError):
    def __init__(self, package_name , error = "" ):
        super().__init__(error)
        self.package_name = package_name
        if not package_name in _dependancies_data.keys():
            self.package_selector = "default"
        else :
            self.package_selector = package_name
            
class sql_placeholder(dependancy_placeholder):
    class _1objclass(object):
        class _2objclass(object):
            class _3objclass(object):
                pass
            Engine = _3objclass()
        base = _2objclass()
    engine = _1objclass()
    def __init__(self, package_name, error ):
        super().__init__(package_name, error)
        
def assert_not_imported(package,raising = True):
    if isinstance(package,dependancy_placeholder):
        if raising:
            dep_miss_raising(package)
        return True
    return False
        
