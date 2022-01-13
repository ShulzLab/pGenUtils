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
    
try :
    import pandas as pd
except ImportError as e :
    pd = _deps.default_placeholder("pandas",e)
    _deps.dep_miss_warning(pd)

@singleton
class StaticSQLEngine(sql.engine.base.Engine):
    """
    A wrapper class around ``open_sql`` function that creates an engine object, but as a singleton.
    This means that if this class has been called once anywhere during a python session, a reference to
    this existing instance will be returned instead of creating a new one, to save time.
    """
    import mysql.connector.errors as mysql_cnx_errors 

    class _StaticSQLEngine__proc():
       """
       self.wrapped class for calling a procedure as an attribute
       """
       def __init__(self , name , parent):
           self.parent = parent
           self.name = name

       def __call__(self, *params):
           return self.parent.call_procedure(self.name,params)
       
    class _StaticSQLEngine__func():
       """
       self.wrapped class for calling a procedure as an attribute
       """
       def __init__(self , name , parent):
           self.parent = parent
           self.name = name

       def __call__(self, *params):
           return self.parent.call_function(self.name,params)
        
    
    def __init__(self,input_method):

        _deps.assert_not_imported(sql)
        temp_engine = open_sql(input_method)
        super().__init__(temp_engine.pool,temp_engine.dialect,temp_engine.url)
        
        _deps.assert_not_imported(pd)
        
        for proc in list(pd.read_sql_query(f"SHOW PROCEDURE STATUS WHERE Db = '{self.default_schema}';",self)["Name"]):
            self.__setattr__(proc,self.__proc(proc,self))
            
        for func in list(pd.read_sql_query(f"SHOW FUNCTION STATUS WHERE Db = '{self.default_schema}';",self)["Name"]):
            self.__setattr__(func,self.__func(func,self))
    
    def _call_sql_executeable(self,exec_type,function_name, params):
        
        def listify(var):
            return [var] if not isinstance(var,(list,tuple)) else var
        
        #import mysql.connector as mysql 
        
        params = listify(params)
        cnx = self.raw_connection()
        cursor = cnx.cursor()
        
        if exec_type == "function" :
            exec_query , finisher = "select", 'as result;'
        elif exec_type == "procedure" :
            exec_query , finisher = "call",';'
        else :
            raise ValueError("executeable typestring must be either 'function' or 'procedure'")
        query = f"{exec_query} {self.default_schema}.{function_name}("+''.join((["%s,"]*(len( params )-1))+['%s)',finisher])
        try:
            for result in cursor.execute( query ,params, multi = True ) :
                try :
                    df = pd.DataFrame(result.fetchall())
                    try :
                        df.columns = result.keys()
                    except AttributeError:
                        df.columns = result.column_names
                except self.mysql_cnx_errors.InterfaceError:
                    pass     
                
        finally:
            cursor.close()
            cnx.close()
        return df if exec_type == "procedure" else df["result"][0]
    
    def call_function(self,function_name, params):
        return self._call_sql_executeable("function",function_name, params)
        
    def call_procedure(self,function_name, params):
        return self._call_sql_executeable("procedure",function_name, params)
    
    
    @property
    def default_schema(self):
        try :
            return self.dialect.default_schema_name
        except AttributeError: 
            return self.url.get_dialect()._get_default_schema_name(self.url.get_dialect(),self.connect())
    

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
