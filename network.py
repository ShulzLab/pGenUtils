# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Mar 30 20:44:51 2020

@author: Timothe
"""

import socket
import strings
import platform
import sqlalchemy as sql
from pathlib import Path

def OpenSQL():
    cnx_string = find_activeSQL()
    engine = sql.create_engine(cnx_string)
    return engine

def isOpen(ip,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def local_roots(**kwargs):

    p = Path(__file__).parents[2]
    node_name = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"device_names",platform.node())
    if node_name is None :
        raise ValueError(f"Please add {platform.node()} into your local_network_config.ini and create associated local_DATAroots key value list")
    localpaths = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"local_DATAroots",node_name)
    autochoose = kwargs.get("auto",True)
    localpath = []
    if localpath is not None:
        for item in localpaths :
            if Path(item).is_dir() :
                localpath.append(item)

    return localpath if len(localpath) > 0 else None


def distant_roots(**kwargs):
    from os.path import join, isdir
    p = Path(__file__).parents[2]

    distantpaths = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"device_names","distant_storages")
    ports = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"ports","smb_ftp")
    distantpath = []
    if distantpaths is not None:
        for item, por in unique_pairs(distantpaths,ports) :
            adress = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"adresses",item)
            if isOpen(adress,por):
                temp_path = join(r"\\"+adress, strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"distant_DATAroots",item))
                if isdir(temp_path):
                    if not temp_path in distantpath :
                        distantpath.append(temp_path)

    return distantpath if len(distantpath) > 0 else None

def find_favoritesRootFolder(**kwargs):
    import os
    source = kwargs.get("source",None)

    p = Path(__file__).parents[2]
    node_name = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"device_names",platform.node())
    if node_name is None :
        raise ValueError(f"Please add {platform.node()} into your local_network_config.ini and create associated local_DATAroots key value list")
    localpaths = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"local_DATAroots",node_name)
    autochoose = kwargs.get("auto",True)
    localpath = None
    if autochoose and localpath is not None:
        for item in localpaths :
            if Path(item).is_dir() :
                localpath = item
                break

    distantpaths = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"device_names","distant_storages")
    ports = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"ports","smb_ftp")
    distantpath = None
    if autochoose and distantpaths is not None:
        for item, por in unique_pairs(distantpaths,ports) :
            adress = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"adresses",item)
            if isOpen(adress,por):
                temp_path = os.path.join(r"\\"+adress, strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"distant_DATAroots",item))
                if os.path.isdir(temp_path):
                    distantpath = temp_path
                    break

    if (source == 'local' or source is None ) and localpath is not None:
        return localpath
    elif (source == 'server' or source is None) and distantpath is not None:
        return distantpath
    else :
        hard_coded = ""
        if distantpath is not None :
            hard_coded = hard_coded + "\ndistant : " + distantpath
        if localpath is not None :
            hard_coded = hard_coded + "\nlocal : " + localpath
        raise ValueError(f"Can't fine any source folder. Check network acess or that external drive is plugged and powered up. Hard-coded paths that should correspond to your setup : {hard_coded}\n( check that hard-drives that match letters are plugged in and that server is acessible and folders are correspunding to shown data")



def find_activeSQL():
    p = Path(__file__).parents[2]

    database_locations = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"device_names","database_locations")
    port = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"ports","database")
    for location in database_locations :
        db_user_pass = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"db_strings",location)
        adress = strings.LoadConfigFile(p.joinpath("local_network_config.ini"),"adresses",location)

        connect_string = r"mysql+mysqlconnector://" + db_user_pass + "@" + adress +  r"/maze?use_pure=True"
        if isOpen(adress,port) :
            return connect_string

if __name__ == "__main__":

    print(find_favoritesRootFolder())
    print(find_activeSQL())
    print(distant_roots())

