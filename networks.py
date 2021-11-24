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
import _dependancies as _deps

#optionnal packages
try :
    import sqlalchemy as sql
except ImportError as e :          
    sql = _deps.sql_placeholder("sqlalchemy",e)
    _deps.dep_miss_warning(sql)

@singleton
class StaticSQLEngine(sql.engine.base.Engine):
    """
    A wrapper class around ``open_sql`` function that creates an engine object, but as a singleton.
    This means that if this class has been called once anywhere during a python session, a reference to
    this existing instance will be returned instead of creating a new one, to save time.
    """
    def __init__(self,input_method):
        _deps.assert_not_imported(sql)
        temp_engine = open_sql(input_method)
        super().__init__(temp_engine.pool,temp_engine.dialect,temp_engine.url)
        
        
    def call_procedure(self,function_name, params):
        def listify(var):
            return [var] if not isinstance(var,(list,tuple)) else var
        
        from itertools import chain
        import mysql.connector as mysql 
        
        params = listify(params)
        cnx = self.raw_connection()
        cursor = cnx.cursor()
        try:
            for result in cursor.execute( f"call {function_name}(%s);",params, multi = True ) :
                try :
                    records = result.fetchall()
                except mysql.errors.InterfaceError:
                    pass           
        finally:
            cursor.close()
            cnx.close()
        return list(chain(*records))


def open_sql(input_method):
    """
    *Previously named OpenSQL*

    input_method is either a string formated as an sqlalchemy "connect_string" or a function that returns a "connect_string"

    Raises:
        sql: DESCRIPTION.

    Returns:
        engine (TYPE): DESCRIPTION.

    """
    _deps.assert_not_imported(sql)
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
