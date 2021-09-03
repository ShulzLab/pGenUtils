# -*- coding: utf-8 -*-
"""Boilerplate:
Created on Mon Mar 30 20:44:51 2020

@author: Timothe
"""

#built-in packages
import socket
import platform
import pathlib

import strings

#optionnal packages
try :
    import sqlalchemy as sql
except ImportError as e :
    sql = e

def open_sql():
    """
    *Previously named OpenSQL*

    Raises:
        sql: DESCRIPTION.

    Returns:
        engine (TYPE): DESCRIPTION.

    """
    if isinstance(sql,ImportError):
        raise sql("You must install sqlalchemy to be able to use this function")
    cnx_string = find_activeSQL()
    engine = sql.create_engine(cnx_string)
    return engine

def is_port_open(ip,port):
    """
    *Previously named isOpen*

    Args:
        ip (TYPE): DESCRIPTION.
        port (TYPE): DESCRIPTION.

    Returns:
        bool: DESCRIPTION.

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False



if __name__ == "__main__":

    print(find_favoritesRootFolder())
    print(find_activeSQL())
    print(distant_roots())

