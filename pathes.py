# -*- coding: utf-8 -*-

"""Boilerplate:
A one line summary of the module or program, terminated by a period.

Leave one blank line.  The rest of this docstring should contain an
overall description of the module or program.  Optionally, it may also
contain a brief description of exported classes and functions and/or usage
examples.

Created on Tue Aug 24 15:33:04 2021
@author: Timothe

  Typical usage example:

  foo = ClassFoo()
  bar = foo.FunctionBar()
"""

import os, warnings
import strings

def list_recursive_files(input_path, condition = "True"):
    #condition = "os.path.splitext(f)[1] != '.txt'"
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(input_path) for f in filenames if eval(condition)]

def list_recursive_dirs(input_path, condition = "True"):
    return [os.path.join(dp, d) for dp, dirnames, fn in os.walk(input_path) for d in dirnames if eval(condition)]

def list_toplevel_dirs(input_path):
    return [ os.path.join(input_path,name) for name in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, name)) ]

def list_toplevel_files(input_path):
    return [ os.path.join(input_path,name) for name in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, name)) ]

def separate_path_components(input_path):
    input_path = os.path.normpath(input_path)
    return input_path.split(os.sep)

def is_or_makedir(input_path):
    """
    Search for a directory. Does nothing if it exists. Create it otherwise (and the subfolders necessary to make the arborescence complete)

    Args:
        input_path (str): Path to the directory to be checked or created.

    Returns:
        Always returns None.

    """
    if os.path.splitext(input_path)[1] == '':
        if not os.path.isdir(input_path):
            os.makedirs(input_path)
    else :
        warnings.warn("The input_path is not a directory")

def remove_common_prefix(input_path, common_root_base):
    """
    Compare an input path and a path with a common root with the input path, and returns only the part of the input path that is not shared with the _common_root_path.
    *Previously named RemoveCommonPrefix*

    Args:
        input_path (TYPE): DESCRIPTION.
        common_root_base (TYPE): DESCRIPTION.

    Returns:
        TYPE: DESCRIPTION.

    """
    return os.path.relpath(os.path.normpath(input_path),os.path.commonprefix((os.path.normpath(common_root_base),os.path.normpath(input_path))))

def switch_root(input_path, original_root, new_root):
    """
    Processed a path to a destination with an "original_root", and replaces this root, if shared with the input_path, for the new root (entirely included).
    *Previously named SwitchRoot*

    Args:
        input_path (TYPE): DESCRIPTION.
        original_root (TYPE): DESCRIPTION.
        new_root (TYPE): DESCRIPTION.

    Returns:
        TYPE: DESCRIPTION.
    """
    try :
        arborescence = remove_common_prefix(input_path, original_root)
    except ValueError :
        return input_path
    if input_path == arborescence :
        return input_path
    return os.path.join(new_root,arborescence)

def get_most_recent_file(filelist):
    """
    *Previously named GetMostRecentFile*

    Args:
        filelist (list tuple): List of file paths from wich to search the most recent one.

    Returns:
        most_recent_file (str): Path to the most recent file.

    """
    import numpy as np
    times = []
    for file in filelist :
        times.append( os.path.getctime(file) )
    most_recent_file = filelist[np.argmax(times)]
    return most_recent_file

def up_folder(input_path,steps):
    """Returns the input_path where we removed the deepest folders, N times.
    *Previously named UpFolder*

    Args:
        input_path (str): DESCRIPTION.
        steps (int): N * stemps is the number of folders removed from the base of the path.

    Returns:
        TYPE: DESCRIPTION.

    """
    import os
    for i in range(steps) :
        input_path = os.path.join(input_path ,"..")
    return os.path.abspath(input_path)

def folder_search(input_folder,file_name):
    """
    Scans a folder an returns a list of the paths to files that match the requirements. The matching is litteral.
    *Previously named Foldersearch*

    Warning:
        It is just returning rigidly the files that **exaclty** match the path entered. Prefer re_folder_search for a more flexible scan using regular expressions.

    Args:
        input_folder (str): Root path from wich to search deeper.
        file_name (str): A name of folder or file located in any subfolders (max recursion depth : 1) of the input_folder.

    Returns:
        NewDirlist (list): List of dirs matching the requirement.
    """
    DirList = os.listdir(input_folder)
    DirList.append(".")
    NewDirlist=[]
    for Subdir in DirList:
        print(Subdir)
        if os.path.exists(os.path.join(input_folder,Subdir,file_name)):
            NewDirlist.append(os.path.abspath(os.path.join(input_folder,Subdir,file_name)))
    return NewDirlist


def re_folder_search(input_folder, regexp, **kwargs):
    """
    Scans a folder an returns a list of the paths to files that matched the requirements. Uses regular expressions.
    *Previously named RegFileSearch*

    Args:
        input_folder (TYPE): DESCRIPTION.
        regexp (TYPE): DESCRIPTION.
        **kwargs (optional): DESCRIPTION.

    Returns:
        list none : DESCRIPTION.

    """
    File_List = os.listdir(input_folder)
    if "checkfile" in kwargs:
        #Care : this function considerably slows down the process and is only
        #necessary in multifolder search
        checkfile = kwargs.get("checkfile")
    else :
        checkfile = False
    if checkfile:
        check_list = []
        for f in File_List:
            if os.path.isfile(os.path.join(input_folder, f)):
                print("Checked")
                check_list.append(f)
        File_List = check_list

    NewDirlist=[]
    for File in File_List:
        if strings.quick_regexp(File,regexp):
            NewDirlist.append(os.path.join(input_folder,File))

    if len(NewDirlist) == 0 :
        return None
    else :
        return NewDirlist

def GetVersionnedPickles(folder, analysis, version):
    filelist = os.listdir(folder)
    outfilelist = []
    for file in filelist :
        attributes = os.path.splitext(file)[0].split("#")
        if attributes[1] == analysis and attributes[2] == version:
            outfilelist.append( os.path.join(folder,file) )
    return outfilelist

def BinarySearch(InputFolder,extension):
    DirList = os.listdir(InputFolder)
    NewDirlist=[]
    try:
        for Subdir in DirList:
            FILE = os.path.join(InputFolder,Subdir)
            if os.path.exists(FILE) and FILE.endswith(extension):
                NewDirlist.append(Subdir)
    except Exception as e:
        print(e)
    return NewDirlist

if __name__ == "__main__":
    pass