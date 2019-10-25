'''
Python Extensions for data structures

History:
08-19-2019 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'
from exceptions import Exception


class StructPositionalArgsException(Exception):
    ''' positional arguments passed exception '''


class Struct(object):
    ''' structure class

    Mimics structures in other langauges. Requires using with
    keyword arguments only

    example -
    # define structure
    class SomeStruct(Struct):
        """ some structure """
        data_str = ''
        data_num = 0

    # instantiate structure
    ss_no_vals = SomeStruct()
    ss_one_vals = SomeStruct(data_num=49)
    ss_exception = SomeStruct('seventy')
    ss_all_vals = SomeStruct(data_str='val', data_num=10)

    see - https://stackoverflow.com/questions/35988/c-like-structures-in-python
    '''

    def __init__(self, *args, **kwargs):
        if len(kwargs):
            # Update by dictionary
            self.__dict__.update(kwargs)
        elif len(args) == 0:
            pass
        else:
            raise StructPositionalArgsException(
                'Must only use keyword arguments')
