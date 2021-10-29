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
from workflows import singleton

#optionnal packages
try :
    import sqlalchemy as sql
except ImportError as e :
    import warnings
    warnings.warn("sqlalchemy installation was not detected, some functions from networks module will be deactivated")
    sql = e

@singleton
class StaticSQLEngine(sql.engine.base.Engine):
    """
    A wrapper class around ``open_sql`` function that creates an engine object, but as a singleton.
    This means that if this class has been called once anywhere during a python session, a reference to
    this existing instance will be returned instead of creating a new one, to save time.
    """
    def __init__(self,input_method):
        temp_engine = open_sql(input_method)
        super().__init__(temp_engine.pool,temp_engine.dialect,temp_engine.url)


def open_sql(input_method):
    """
    *Previously named OpenSQL*

    input_method is either a string formated as an sqlalchemy "connect_string" or a function that returns a "connect_string"

    Raises:
        sql: DESCRIPTION.

    Returns:
        engine (TYPE): DESCRIPTION.

    """
    if isinstance(sql,ImportError):
        raise sql("You must install sqlalchemy to be able to use this function")
    if not isinstance(input_method,str) : #
        input_method = input_method()
    engine = sql.create_engine(input_method)
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


    test = StaticSQLEngine("test")
    print(test)
    toast = StaticSQLEngine("seck")
    print(toast)
