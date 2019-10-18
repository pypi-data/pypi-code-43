#!/usr/bin/env python
# coding: utf-8

# # Data Parser
# Parses data retrieved from a technqiue.

# In[14]:


from collections import namedtuple

import ec_lib as ecl


# # Parser

# In[ ]:


def parse( info, data, fields = None ):
    """
    Parses data retrieved from a technique.

    :param info: DataInfo object representing metadata of the technqiue.
    :param data: Data to parse.
    :param fields: List of FieldInfo used to interpret the data.
        If None, uses the technique ID to retrieve 
    :returns: A list of namedtuples representing the data.
    """
    rows = info.NbRows
    cols = info.NbCols
    technique = ecl.TechniqueId( info.TechniqueID )

    # technique info
    field_names = [ field.name for field in fields ]
    Datum = namedtuple( 'Datum', field_names )

    # convert singles
    data = [
        ecl.convert_numeric( datum ) 
        if ( fields[ index % cols ].type is ecl.ParameterType.SINGLE ) 
        else datum
        for index, datum in enumerate( data )
    ]

    # group data
    parsed = [
        Datum( *data[ i : i + cols ] ) for i in range( 0, rows* cols, cols )
    ]

    return parsed


# In[23]:


# For holding field info.
FieldInfo = namedtuple( 'FieldInfo', [ 'name', 'type' ] )


# In[34]:


class SP300_Fields():
    """
    Holds technique field definitions.
    """
    # for convenience
    TID     = ecl.TechniqueId 
    INT32   = ecl.ParameterType.INT32
    BOOL    = ecl.ParameterType.BOOLEAN
    SINGLE  = ecl.ParameterType.SINGLE
    FI      = FieldInfo
    
    OCV = [
        FI( 'start',    INT32   ),  
        FI( 'end',      INT32   ),
        FI( 'voltage',  SINGLE  )
    ]
    
    CP = [
        FI( 'start',   INT32  ),
        FI( 'end',     INT32  ),
        FI( 'voltage', SINGLE ),
        FI( 'current', SINGLE ),
        FI( 'cycle',   INT32  )
    ]
    
    CA      = CP
    CPLIMIT = CP
    CALIMIT = CP


# In[ ]:




