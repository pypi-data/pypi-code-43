'''
Created on Nov 4, 2017

@author: stelios
'''

class Column(object):
    """Column class, equivalent to a Firethorn ADQL Column
    """


    def __init__(self, adql_column=None):
        self.__adql_column = adql_column
        
    
    def name(self):
        return self.__adql_column.name()                    
 
    def type(self):
        return self.__adql_column.type()     
    
    def ucd(self):
        return self.__adql_column.ucd()  
    
    def utype(self):
        return self.__adql_column.utype()             
    
    def __str__(self):
        """Get class as string
        """
        return self.__adql_column
