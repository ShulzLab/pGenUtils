
import warnings, os, inspect

_standard_dependancy_message = """
The function : function {caller_function_name}() of the submodule : {caller_file_name} of pGenUtils, requires the optionnal package : {package_name} ({package_website}). 
You can install it in your environment with : 
{package_install_command}
""" 
            
_dependancies_install_commands = {"rasterio": ["conda install rasterio","pip install rasterio"]}

_dependancies_websites = {"rasterio": "https://rasterio.readthedocs.io/en/latest/installation.html"}
                  
def dependancy_missing_warning(package_name):
    message_format_pieces = {"package_name" : package_name}
    message_format_pieces["package_website"] = _dependancies_websites[package_name]
    message_format_pieces["caller_function_name"] = inspect.stack()[1][3]
    message_format_pieces["caller_file_name"]  = os.path.basename(inspect.stack()[1][1])
    or_list = ["\nor\n"]*(len( _dependancies_install_commands[package_name] )-1)+['']
    message_format_pieces["package_install_command"] = ''.join(  [item + str(conj_coord) for item, conj_coord in zip(_dependancies_install_commands[package_name],or_list) ] ) 
    
    raise ImportError(_standard_dependancy_message.format(**message_format_pieces))
    
    
        
