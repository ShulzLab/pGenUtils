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

def is_or_makedir(path):
    if os.path.splitext(path)[1] == '':
        if not os.path.isdir(path):
            os.makedirs(path)
    else :
        warnings.warn("The path is not a directory")

def remove_common_prefix(input_path, common_root_base):
    return os.path.relpath(input_path,os.path.commonprefix((common_root_base,input_path)))

def SwitchRoot(path ,original_root , new_root):
    try :
        arborescence = RemoveCommonPrefix(path, original_root)
    except ValueError :
        return path
    if path == arborescence :
        return path
    return os.path.join(new_root,arborescence)

def GetMostRecentFile(filelist):
    import numpy as np
    times = []
    for file in filelist :
        times.append( os.path.getctime(file) )
    most_recent_file = filelist[np.argmax(times)]
    return most_recent_file

def UpFolder(path,steps):
    import os
    for i in range(steps) :
        path = os.path.join(path ,"..")
    return os.path.abspath(path)

def folder_search(MainInputFolder,VideoName):
    """
    Scans a folder an returns a list of the paths to files that match the requirements. The matching is litteral.
    *Previously named Foldersearch*

    Warning:
        It is just returning rigidly the files that **exaclty** match the path entered. Prefer re_folder_search for a more flexible scan using regular expressions.

    Args:
        MainInputFolder (str): Root path from wich to search deeper.
        VideoName (str): A name of folder or file located in any subfolders (max recursion depth : 1) of the MainInputFolder.

    Returns:
        NewDirlist (list): List of dirs matching the requirement.
    """
    DirList = os.listdir(MainInputFolder)
    DirList.append(".")
    NewDirlist=[]
    for Subdir in DirList:
        print(Subdir)
        if os.path.exists(os.path.join(MainInputFolder,Subdir,VideoName)):
            NewDirlist.append(os.path.abspath(os.path.join(MainInputFolder,Subdir,VideoName)))
    return NewDirlist


def re_folder_search(MainInputFolder, regexp, **kwargs):
    """
    Scans a folder an returns a list of the paths to files that matched the requirements. Uses regular expressions.
    *Previously named RegFileSearch*

    Args:
        MainInputFolder (TYPE): DESCRIPTION.
        regexp (TYPE): DESCRIPTION.
        **kwargs (optional): DESCRIPTION.

    Returns:
        list none : DESCRIPTION.

    """
    File_List = os.listdir(MainInputFolder)
    if "checkfile" in kwargs:
        #Care : this function considerably slows down the process and is only
        #necessary in multifolder search
        checkfile = kwargs.get("checkfile")
    else :
        checkfile = False
    if checkfile:
        check_list = []
        for f in File_List:
            if os.path.isfile(os.path.join(MainInputFolder, f)):
                print("Checked")
                check_list.append(f)
        File_List = check_list

    NewDirlist=[]
    for File in File_List:
        if strings.quick_regexp(File,regexp):
            NewDirlist.append(os.path.join(MainInputFolder,File))

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