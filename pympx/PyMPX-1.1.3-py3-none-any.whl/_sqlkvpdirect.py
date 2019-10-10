'''
Module for writing to Empower data stores directly - i.e. not via Empower Importer.

Currently this only works with the SQL Server transactional data storage.

This module depends on the pythonnet package for Common Language Runtime functions. Pythonnet is available via Conda, but is not part of the standard Anaconda setup.
'''

#This module documentation follows the conventions set out in http://pythonhosted.org/an_example_pypi_project/sphinx.html
#and is built into the automatic documentation

#/****************************************************************************/
#/* Metapraxis Limited                                                       */
#/* Date: 27-08-2019                                                         */
#/*                                                                          */
#/*                                                                          */
#/* Copyright (c) Metapraxis Limited, 2019-present.                          */
#/* All Rights Reserved.                                                     */
#/****************************************************************************/
#/* NOTICE:  All information contained herein is, and remains the property   */
#/* of Metapraxis Limited and its suppliers, if any.                         */
#/* The intellectual and technical concepts contained herein are proprietary */
#/* to Metapraxis Limited and its suppliers and may be covered by UK and     */
#/* Foreign Patents, patents in process, and are protected by trade secret   */
#/* or copyright law.  Dissemination of this information or reproduction of  */
#/* this material is strictly forbidden unless prior written permission is   */
#/* obtained from Metapraxis Limited.                                        */
#/*                                                                          */
#/* This file is subject to the terms and conditions defined in              */
#/* file "license.txt", which is part of this source code package.           */
#/****************************************************************************/


#TODO: There is a possibility of a speed-up by not writing out shard files as full bulk-import files (i.e. text files), 
#but rather keeping the empower key and pickling the file instead 
#This means we wouldn't have to reconstruct a key which we've already created in order to do the sort


import struct
import pyodbc 
import os
import sys
import datetime
import multiprocessing
from pympx import low_level_utilities as llu
from pympx import logconfig
from pympx import exceptions as mpex
from pympx import pympx as mpx

log=logconfig.get_logger()

FAILED = llu.FAILED
DONE = llu.DONE


try:
	#Need pythonnet package to import clr
	#This can be imported via conda
	import clr
	clr_imported = True
	
	clr.AddReference('System')
	clr.AddReference('System.Data')
	#from System import *
	#from System import Console
	from System import Data
	from System import Int32, Byte, Array, Object

except ImportError:
	clr_imported = False
	


INTERVAL_NUMBER = 3
INTERVALBYTES = bytearray.fromhex('4404')
ZEROVALUEBYTES = struct.pack('<d', 0)

import functools
@functools.lru_cache(2**16)
def _bytify_int(someint):
    return str(someint).encode('utf8')

@functools.lru_cache(2**32)
def _bytify_str(somestr):
    return somestr.encode('utf8')

@functools.lru_cache(2**16)
def _le_int(somestr):
    return int(somestr).to_bytes(4,'little')

@functools.lru_cache(2**16)
def _four_bytes_to_int_str_byte(_bytes):
    return str(int.from_bytes(_bytes[0:2],'little')+int.from_bytes(_bytes[2:4],'little')*256*256).encode('utf8')

@functools.lru_cache(2**16)
def _four_bytes_to_int(_bytes):
    return int.from_bytes(_bytes[0:2],'little')+int.from_bytes(_bytes[2:4],'little')*256*256

@functools.lru_cache(2**16)
def _two_bytes_to_int(_bytes):
    return int.from_bytes(_bytes,'little')

@functools.lru_cache(2**16)
def _int_to_four_bytes(int):
    return int.to_bytes(4,'little')

@functools.lru_cache(2**16)
def _int_to_two_bytes(int):
    return int.to_bytes(2,'little')

@functools.lru_cache(2**32)
def _cache_float(somestr):
    return float(somestr)

@functools.lru_cache(2**16)
def _cache_int(somestr):
    return int(somestr)

#Save 10% of time by caching this!
@functools.lru_cache(2**16)
def _cast_to_Int32(someint):
    return Int32(someint)

#def _cast_to_ArrayByte(somebytes):
#    return Array[Byte](somebytes)

@functools.lru_cache(2**8)
def _cast_to_Byte(somebyte):
    return Byte(somebyte)

#def _cast_to_ArrayByte(somebytes):
#    return Array[Byte]([_cast_to_Byte(b) for b in somebytes])

#@functools.lru_cache(2**32)
def _cast_to_ArrayByte(somebytes):
    return Array[Byte](somebytes)

@functools.lru_cache(2**32)
def _unpack_float(eightbytes):
    return struct.unpack('<d', eightbytes)[0]



def _build_empower_key(splitline):
    #Original order is
    #u1,...u8,metric,comparison,currency,empower year,empower period type,empower period,datapoint
    #Target order is
    #currency,comparison,metric,u1-u8,t

    #We need these bytes whether we are chunking or not
    ccy  = _le_int(splitline[10])
    comp = _le_int(splitline[9])
    mtrc = _le_int(splitline[8])

    #Not using this - using constant INTERVALBYTES instead
    #intvl = _le_int(splitline[12])

    #Sort the data by turning it into a massive dictionary and then iterating over the items
    key = (INTERVALBYTES+ccy+comp+mtrc
          +_le_int(splitline[0])
          +_le_int(splitline[1])
          +_le_int(splitline[2])
          +_le_int(splitline[3])
          +_le_int(splitline[4])
          +_le_int(splitline[5])
          +_le_int(splitline[6])
          +_le_int(splitline[7])
          )
    return key
	
	
def _build_record_from_shard_line(key,splitline):
    current_record = {'key' :key
                     ,'dim0':_cache_int(splitline[0])
                     ,'dim1':_cache_int(splitline[1])
                     ,'dim2':_cache_int(splitline[2])
                     ,'dim3':_cache_int(splitline[3])
                     ,'dim4':_cache_int(splitline[4])
                     ,'dim5':_cache_int(splitline[5])
                     ,'dim6':_cache_int(splitline[6])
                     ,'dim7':_cache_int(splitline[7])
                     ,'dim8': _cache_int(splitline[8])
                     ,'dim9': _cache_int(splitline[9])
                     ,'dim10':_cache_int(splitline[10]) 
                     ,'dim11':_cache_int(splitline[11])             
                     ,'data': [] 
                     } 
    return current_record	
	
def _append_shard_line_to_current_record(current_record,splitline):
    value = _cache_float(splitline[14])
    year  = _cache_int(splitline[11])
    interval_type = _cache_int(splitline[12])
    #This is usually the month, when interval type = 3
    #interval_number = _cache_int(splitline[13])
    
    current_record['data'].append({'year': year,
                                  'interval': INTERVAL_NUMBER,
                                  'intervaltype': interval_type,
                                  'value': value,
                                  'transactionnumber': -1})	
								  

def _yield_from_ordered_shard(datafile):
    #WARNING - this will cause issues if we use intervals other than months
    
    previous_empower_key = None
    first_record = True
    previous_splitline_10 = []
    #Instantiate n in case we don't ever read the file
    n=0    
    with open(datafile,'r') as datafileobject:
        for n, l in enumerate(datafileobject):

            #split on tabs (:-1 takes the newline off, which would otherwise end up on the end of the datapoint)
            #We don't take the newline off, since we are going to write it anyway
            splitline = l[:-1].split('\t')
            splitline_10 = splitline[:10]
            
            #TODO Could try not building key unless previous_splitline[0:10] differs to current_splitline[0:10]
            if previous_splitline_10 != splitline_10: #key!=previous_empower_key:
                key = _build_empower_key(splitline)
                #Start a new record
                if not first_record:
                    yield current_record
                
                current_record = _build_record_from_shard_line(key,splitline)
            
            #previous_empower_key = key
            previous_splitline_10 = splitline_10
            first_record = False
                    
            #Add the value and date from the current line to the current record
            _append_shard_line_to_current_record(current_record,splitline)

    #yield the final record             
    #if previous_empower_key is not None:
    if previous_splitline_10 is not None:
        yield current_record

    log.verbose("Parsed {} records from shard {}".format(n,datafile))

@functools.lru_cache(2**4)
def _lockmaybe_realnamaybe(eightbytes):
    lockmaybe= _four_bytes_to_int(eightbytes[:4])
    realnamaybe = _four_bytes_to_int(eightbytes[4:])
    return lockmaybe,realnamaybe

@functools.lru_cache(2**16)
def _transform_year(year,dateindex,n):
    return year+(dateindex +n) // 12

@functools.lru_cache(2**8)
def _transform_interval(dateindex, n):
    return 1+(dateindex +n) % 12

@functools.lru_cache(2**8)
def _trailing_datetype_dateindex_number_of_entries(eight_bytes):
    datetype = _two_bytes_to_int(eight_bytes[0:2])
    dateindex = _two_bytes_to_int(eight_bytes[2:4])
    number_of_entries = _four_bytes_to_int(eight_bytes[4:8])
    return datetype, dateindex, number_of_entries

@functools.lru_cache(2**16)
def _parse_first_ten_bytes(ten_bytes):
    year = _two_bytes_to_int(ten_bytes[0:2])
    
    datetype = _two_bytes_to_int(ten_bytes[2:4])
    #e.g. may = 4 (5th month using 0 based indexing)
    dateindex = _two_bytes_to_int(ten_bytes[4:6])
    number_of_entries = _four_bytes_to_int(ten_bytes[6:10])
    
    return year, datetype, dateindex, number_of_entries

def _parse_empower_data(empower_data):
    #Read the first 14 bytes - that will tell us how many entries are in the data
    offset = 0
    
    #year = _two_bytes_to_int(empower_data[0:2])
    #offset = 2
    #
    #datetype = _two_bytes_to_int(empower_data[offset:offset+2])
    ##e.g. may = 4 (5th month using 0 based indexing)
    #dateindex = _two_bytes_to_int(empower_data[offset+2:offset+4])
    #number_of_entries = _four_bytes_to_int(empower_data[offset+4:offset+8])
    #
    year, datetype, dateindex, number_of_entries = _parse_first_ten_bytes(empower_data[:10])
    
    offset +=10
    
    while number_of_entries != 0:
        
        #Surely we can hold more than one datetype that means we will need to emit records per datetype
        
        #We don't do anything with anotherthing - so ignore it (for now at least)
        #anotherthing = _four_bytes_to_int(empower_data[offset:offset+4])
        #print(year,datetype,'dateindex={}'.format(dateindex),'n={}'.format(number_of_entries),anotherthing)
        
        offset += 4
            
        #read blocks of 18 bytes, each which contain a single data point

        for n in range(number_of_entries):
            
            lockmaybe, realnamaybe = _lockmaybe_realnamaybe(empower_data[offset:offset+8])
            #Moved this 'if' up - because there is no point parsing daat (just zeroes anyway) which we are going to ignore
            if realnamaybe == 1:
                value = struct.unpack('<d', empower_data[offset+8:offset+16])[0]
                #value = _unpack_float(empower_data[offset+8:offset+16])
                transactionnumber = _two_bytes_to_int(empower_data[offset+16:offset+18])
                
                #Removed this if, as it is now further up
                #if realnamaybe == 1:
                ##print('\t',year+(dateindex +n) // 12,1+(dateindex +n) % 12,n,lockmaybe,realnamaybe,value,transactionnumber)
                yield {'year' : _transform_year(year,dateindex,n)
                      ,'interval': _transform_interval(dateindex, n)
                      ,'intervaltype':datetype
                      #,lockmaybe
                      ,'value':value
                      ,'transactionnumber':transactionnumber
                      }
                       
            offset += 18

        #Grab this as one memoized function, because all three values usually the same
        datetype,dateindex,number_of_entries= _trailing_datetype_dateindex_number_of_entries(empower_data[offset:offset+8])
        offset +=8
    
    #print(year,datetype,dateindex,number_of_entries)

if clr_imported:

    def _record_to_dict(r):
        record = {'key' :r.Key
                         ,'dim0':r.Dim0
                         ,'dim1':r.Dim1
                         ,'dim2':r.Dim2
                         ,'dim3':r.Dim3
                         ,'dim4':r.Dim4
                         ,'dim5':r.Dim5
                         ,'dim6':r.Dim6
                         ,'dim7':r.Dim7
                         ,'dim8':r.Dim8
                         ,'dim9':r.Dim9
                         ,'dim10':r.Dim10
                         #,'data': list(_parse_empower_data(r.Data))
                         ,'orig_data': r.Data
                         }
        return record
    
    def _yield_empower_records(cnxn,first_physid,last_physid,interval_type=3):
        #WARNING - this will cause issues if we use intervals other than months
        datatypeintervaltype = bytearray.fromhex('4404')

        cursor = cnxn.cursor()

        query = """SELECT [Dim0]
              ,[Dim1]
              ,[Dim2]
              ,[Dim3]
              ,[Dim4]
              ,[Dim5]
              ,[Dim6]
              ,[Dim7]
              ,[Dim8]
              ,[Dim9]
              ,[Dim10]
              ,[Key]
              ,[Data]
          FROM [dbo].[Data] WITH (NOLOCK) --We are updating the table as we read, but NEVER these Dim 0 values. So read them with NOLOCK for speed
          WHERE 
          [Dim11] = {} and
          [Dim0] between {} and {}
          order by [Key]
          """.format(interval_type,first_physid,last_physid)

        for r in cursor.execute(query):
            yield _record_to_dict(r)

            #key2 = datatypeintervaltype+(_le_int(r.Dim10)
            #      +_le_int(r.Dim9)
            #      +_le_int(r.Dim8)
            #      +_le_int(r.Dim0)
            #      +_le_int(r.Dim1)
            #      +_le_int(r.Dim2)
            #      +_le_int(r.Dim3)
            #      +_le_int(r.Dim4)
            #      +_le_int(r.Dim5)
            #      +_le_int(r.Dim6)
            #      +_le_int(r.Dim7)
            #      )

            #if r.Key != key2:
            #    print(r.Key)
            #    print(key2)

            #    raise ValueError

            
else:    

	raise SystemError('This functionality needs pythonnet to be installed in the environment, so that the .Net Common Language Runtime can be called')
	
def _merge_records(empower_record,shard_record,replace_slice_year=None, replace_slice_year_interval_min = None, replace_slice_year_interval_max = None):
    '''
    :param replace_slice_year: Year for the slice we want to replace.  Slices can only span a single year (because multiple years would be slower)
    :param replace_slice_year_interval_min: Start interval (usually month) for the slice we want to replace
    :param replace_slice_year_interval_max:  End interval (usually month) for the slice we want to replace
    
    Replacement slice is for when we are replacing a timeslice in Empower with a timeslice from a source,
    We want to clear out that timeslice in the site and replace the time slice with data that exists in the source data.
       
    '''
    
    change_status = None
    #Keep track of record counts, so that we can determine whether the final record is due for insert, update or delete
    original_record_count = 0
    #Note - changes will include deletions, so if a record is deleted it will count as +1 change and +1 delete
    changed_record_count = 0
    final_record_count = 0
    deleted_record_count = 0
    
    empower_data_gen = (r for r in _parse_empower_data(empower_record['orig_data']))
    if shard_record is not None:
        shard_data_gen   = (r for r in shard_record['data'])  
    else:
        #pass an empty generator if there is no shard record - this happens when we are only passed an empower record
        #which can happen if we are clearing out the empower time slice
        shard_data_gen = (r for r in [])
        
    #Copy keys from the Empower Record
    output_record = {}
    output_record['key']  = empower_record['key']
    output_record['dim0'] = empower_record['dim0'] 
    output_record['dim1'] = empower_record['dim1'] 
    output_record['dim2'] = empower_record['dim2'] 
    output_record['dim3'] = empower_record['dim3'] 
    output_record['dim4'] = empower_record['dim4'] 
    output_record['dim5'] = empower_record['dim5'] 
    output_record['dim6'] = empower_record['dim6'] 
    output_record['dim7'] = empower_record['dim7'] 
    output_record['dim8'] = empower_record['dim8'] 
    output_record['dim9'] = empower_record['dim9'] 
    output_record['dim10']= empower_record['dim10']
    
    combined_data = []
    try:
        shard_datum   = next(shard_data_gen)
    except StopIteration:
        shard_datum   = None
    try:
        empower_datum = next(empower_data_gen)
    except StopIteration:
        empower_datum = None
    
    try:
        while True:
            if shard_datum is None and empower_datum is None:
                print("Some sort of error occurred - we shouldn't be able to get to this point")
                break

            if shard_datum is None:

                #Check whether this datum is inside the timeslice marked for replacement
                #If it is, it shold be deleted

                if replace_slice_year is not None and empower_datum['year'] == replace_slice_year and empower_datum['interval'] >= replace_slice_year_interval_min and empower_datum['interval'] <= replace_slice_year_interval_max:
                    #Record a deletion and a change if the original site data is not present in the source data, but is part of the time-slice we are replaceing
                    deleted_record_count += 1
                    changed_record_count += 1
                else:

                    #Shard datum is earlier
                    combined_data.append(empower_datum)
                    original_record_count += 1
                    final_record_count += 1
                    empower_datum['changed_flag'] = False 

                try:
                    empower_datum   = next(empower_data_gen)
                except StopIteration:
                    empower_datum   = None
                    break

            elif empower_datum is None:
                    #Shard datum is earlier
                    combined_data.append(shard_datum)     
                    final_record_count += 1
                    changed_record_count += 1

                    shard_datum['changed_flag'] = True 
                    try:
                        shard_datum   = next(shard_data_gen)
                    except StopIteration:
                        shard_datum   = None
                        break
                        
            elif shard_datum['year'] > empower_datum['year'] or shard_datum['interval'] > empower_datum['interval']:

                #Check whether this datum is inside the timeslice marked for replacement
                #If it is, it shold be deleted

                if replace_slice_year is not None and shard_datum['year'] == replace_slice_year and shard_datum['interval'] >= replace_slice_year_interval_min and shard_datum['interval'] <= replace_slice_year_interval_max:
                    #Record a deletion and a change if the original site data is not present in the source data, but is part of the time-slice we are replaceing
                    deleted_record_count += 1
                    changed_record_count += 1
                else:

                    #Shard datum is earlier
                    combined_data.append(empower_datum)
                    original_record_count += 1
                    final_record_count += 1
                    empower_datum['changed_flag'] = False 

                try:
                    empower_datum   = next(empower_data_gen)
                except StopIteration:
                    empower_datum   = None

            elif shard_datum['year'] < empower_datum['year'] or shard_datum['interval'] < empower_datum['interval']:
                    #Shard datum is earlier
                    combined_data.append(shard_datum)     
                    final_record_count += 1
                    changed_record_count += 1

                    shard_datum['changed_flag'] = True 
                    try:
                        shard_datum   = next(shard_data_gen)
                    except StopIteration:
                        shard_datum   = None

            elif shard_datum['year'] == empower_datum['year'] and shard_datum['interval'] == empower_datum['interval']:     

                changed_flag = empower_datum['value'] != shard_datum['value']

                original_record_count += 1
                final_record_count += 1
                if changed_flag:
                    changed_record_count += 1

                combined_data.append( {'year'        : empower_datum['year']
                                      ,'interval'    : empower_datum['interval']
                                      ,'intervaltype': empower_datum['intervaltype']
                                      ,'value'       : shard_datum['value']
                                      ,'transactionnumber': empower_datum['transactionnumber']
                                      ,'changed_flag': changed_flag
                                      #,'orig_data'   : empower_datum['orig_data']    
                                      }
                                    )

                try:
                    shard_datum   = next(shard_data_gen)
                except StopIteration:
                    shard_datum   = None
                    if empower_datum is None:
                        break

                try:
                    empower_datum   = next(empower_data_gen)
                except StopIteration:
                    empower_datum   = None
                    if shard_datum is None:
                        break
            else:
                assert(False)
    except TypeError:
        print("empower_datum")
        print(empower_datum)
        print("shard_datum")
        print(shard_datum)
        raise
        
    output_record['data'] = combined_data

    if original_record_count == 0:
        output_record['change_status'] = 'insert'
    elif final_record_count == 0:
        output_record['change_status'] = 'delete'
    elif changed_record_count == 0 and final_record_count == original_record_count:
        output_record['change_status'] = 'no_change'
    else:
        output_record['change_status'] = 'update'

    return output_record

def _interleave_shard_and_empower_records(empower_gen, shard_gen,replace_slice_year=None, replace_slice_year_interval_min = None, replace_slice_year_interval_max = None,shard_suffix=None):
    '''
    :param replace_slice_year: Year for the slice we want to replace.  Slices can only span a single year (because multiple years would be slower)
    :param replace_slice_year_interval_min: Start interval (usually month) for the slice we want to replace
    :param replace_slice_year_interval_max:  End interval (usually month) for the slice we want to replace
    :param shard_suffix: Used for logging only
    
    Replacement slice is for when we are replacing a timeslice in Empower with a timeslice from a source,
    We want to clear out that timeslice in the site and replace the time slice with data that exists in the source data.
       
    '''
    log.verbose("Beginning shard/empower interleaving for {}".format(shard_suffix))
    count_keys_same = 0
    count_keys_empower = 0
    count_keys_shard = 0

    try:
        empower_record = next(empower_gen)
        count_keys_empower += 1
    except StopIteration:
        empower_record = None


    try:
        shard_record = next(shard_gen)
        count_keys_shard+=1
    except StopIteration:
        shard_record = None

    previous_shard_key   = bytearray.fromhex('')
    previous_empower_key = bytearray.fromhex('')

    while True:
        if shard_record is None:
            
            if replace_slice_year is None:
                if empower_record is not None:
                    empower_record['change_status'] = 'no_change'
                    empower_record['data'] = empower_record['orig_data']
                    #Emit empower record
                    yield empower_record
            else:
                #Clear timeslice from original empower record
                yield _merge_records(empower_record,shard_record=None,replace_slice_year=replace_slice_year, replace_slice_year_interval_min = replace_slice_year_interval_min, replace_slice_year_interval_max =  replace_slice_year_interval_max)
                
            try:
                empower_record = next(empower_gen)
                count_keys_empower += 1
                continue
            except StopIteration:
                empower_record = None
                break

        if empower_record is None:
            #Emit shard record
            shard_record['change_status'] = 'insert'
            yield shard_record
            try:
                shard_record = next(shard_gen)
                count_keys_shard+=1

            except StopIteration:
                shard_record = None
                break

        elif empower_record['key'] == shard_record['key']:
            count_keys_same +=1
            #Merge records

            yield _merge_records(empower_record,shard_record,replace_slice_year=replace_slice_year, replace_slice_year_interval_min = replace_slice_year_interval_min, replace_slice_year_interval_max =  replace_slice_year_interval_max)

            #Emit merged record


            try:
                empower_record = next(empower_gen)
                count_keys_empower += 1
            except StopIteration:
                empower_record = None
            try:
                shard_record = next(shard_gen)
                count_keys_shard+=1
            except StopIteration:
                shard_record = None

        elif empower_record['key'] < shard_record['key']: 
            
            if replace_slice_year is None:
                empower_record['change_status'] = 'no_change'
                empower_record['data'] = empower_record['orig_data']
                #Emit empower record
                yield empower_record
            else:
                #Clear timeslice from 
                yield _merge_records(empower_record,shard_record=None,replace_slice_year=replace_slice_year, replace_slice_year_interval_min = replace_slice_year_interval_min, replace_slice_year_interval_max =  replace_slice_year_interval_max)
            
            #get next empower record
            try:
                empower_record = next(empower_gen)
                count_keys_empower += 1
            except StopIteration:
                empower_record = None

        elif empower_record['key'] > shard_record['key']: 
            #emit shard record
            shard_record['change_status'] = 'insert'
            yield shard_record

            #get next shard record
            try:
                shard_record['change_status'] = 'insert'
                shard_record = next(shard_gen)
                count_keys_shard+=1
            except StopIteration:
                shard_record = None

        if shard_record is not None  and shard_record['key'] < previous_shard_key:
            print(shard_record['key'])
            print(previous_shard_key)
            raise ValueError('Shard records not sorted by key')
        if empower_record is not None and empower_record['key'] < previous_empower_key:
            print(empower_record['key'])
            print(previous_empower_key)
            raise ValueError('Empower records not sorted by key')

        if shard_record is not None:
            previous_shard_key   = shard_record['key']
        else:
            previous_shard_key = None

        if empower_record is not None:
            previous_empower_key = empower_record['key']
        else:
            previous_empower_key = None

    log.verbose("Interleaved shard {}. Records in Shard Only/Both/Empower Only =  {}/{}/{}".format(shard_suffix, count_keys_shard-count_keys_same, count_keys_same,count_keys_empower-count_keys_same))

def _encode_empower_data(record_data):
    #Turn 'year' :  ,'interval':  ,'intervaltype': ,'value': ,'transactionnumber':
    #records into encoded Empower data bytes
    
    
    number_of_entries = 0
    initial_year = None
    initial_dateindex = None
    previous_year     = None
    previous_interval = None
    dateindex         = None
    interval_type          = 3 #default
    
    byte_records = []
    #Encode each record, keeping track of transaction number, total records inserted, and filling gaps
    previous_output_record_number = None  
    for record in record_data:
        year = record['year']
        interval = record['interval']
        interval_type = record['intervaltype']
        if initial_year is None:
            initial_year = year
            initial_dateindex = interval - 1
            initial_interval = interval
    
        year_offset  = year - initial_year
        month_offset = interval - initial_interval
        current_output_record_number = month_offset+year_offset*12
        if previous_output_record_number is not None:
            for n in range( current_output_record_number - previous_output_record_number-1):
                #print('Filler Record')
                lockmaybe= _int_to_four_bytes(0)
                realnamaybe = _int_to_four_bytes(0)
                value = ZEROVALUEBYTES 
                #transactionnumber = _int_to_two_bytes(record['transactionnumber']+1)
                try:
                    transactionnumber = _int_to_two_bytes(record['transactionnumber']+1)
                except OverflowError:
                    print('transactionnumber',record['transactionnumber']+1)
                    raise
                byte_records.append(lockmaybe+realnamaybe+value+transactionnumber)

                number_of_entries +=1
        
        previous_output_record_number = current_output_record_number 
        
        #print(initial_dateindex + (month_offset+year_offset*12))
        
        lockmaybe= _int_to_four_bytes(0)
        realnamaybe = _int_to_four_bytes(1)
        value = struct.pack('<d', record['value'])
        try:
            transactionnumber = _int_to_two_bytes(record['transactionnumber']+1)
        except OverflowError:
            print('transactionnumber',record['transactionnumber']+1)
            raise

        byte_records.append(lockmaybe+realnamaybe+value+transactionnumber)
        number_of_entries +=1

    
    #year = _four_bytes_to_int(empower_data[0:2])
    #offset = 2
    #
    #datetype = _four_bytes_to_int(empower_data[offset:offset+2])
    ##e.g. may = 4 (5th month using 0 based indexing)
    #dateindex = _four_bytes_to_int(empower_data[offset+2:offset+4])
    #number_of_entries = _four_bytes_to_int(empower_data[offset+4:offset+8])
    #
    #offset +=8
    #
    #while number_of_entries != 0:
    #    
    #    #Surely we can hold more than one datetype that means we will need to emit records per datetype
    #    anotherthing = _four_bytes_to_int(empower_data[offset:offset+4])
   
    #print(number_of_entries)
    #print(len(byte_records))
    #print(byte_records)
    



    #Write initial_year into the first 2 bytes
            
    #write datetype into the next 2 bytes
            
    #write initial date index (i.e. month most of the time) into the next 2 bytes
            
    #write number of entries into the next 4 bytes
            
            
#    #Add the header and footer bytes
#    #Header - the first 14 bytes will tell us how many entries are in the data
#   
    out_initial_year = _int_to_two_bytes(initial_year) #2bytes 
    out_datetype = _int_to_two_bytes(interval_type) #2bytes 
    if initial_dateindex is None:
        initial_dateindex = 0
    out_dateindex = _int_to_two_bytes(initial_dateindex) #2bytes 
    out_number_of_entries = _int_to_four_bytes(len(byte_records)) #four_bytes
    out_anotherthing = _int_to_four_bytes(0)

    out_data_meat = b"".join(byte_records)
    
    #Footer
    out_foot_datetype  = b'\x00' #2bytes #_four_bytes_to_int(empower_data[offset:offset+2])
    out_foot_dateindex = b'\x00' #2bytes #_four_bytes_to_int(empower_data[offset+2:offset+4])
    out_foot_number_of_entries = b'\x00\x00' #_four_bytes_to_int(empower_data[offset+4:offset+8])
    
    return out_initial_year + out_datetype + out_dateindex + out_number_of_entries + out_anotherthing + out_data_meat + out_foot_datetype + out_foot_dateindex + out_foot_number_of_entries

class _SQLServerDataHose():
    def __init__(self, mssql_connection_String, target_table_name,interval_type=3,batchsize = 10000):
        #Initialise these to none, to make disposal easier
        self.bulkcopy = None
        self.workTable = None
        
        #We may as do the cast to Int32 once, rather than once per record
        self.interval_type = Int32(interval_type)
        
        self.mssql_connection_String = mssql_connection_String
        self.target_table_name = target_table_name
        self.batchsize         = batchsize
        
        self.sqlDbConnection = Data.SqlClient.SqlConnection(mssql_connection_String)

        #open connection for the truncate
        self.sqlDbConnection.Open()
        try:
            cmd = Data.SqlClient.SqlCommand("truncate table {}".format(self.target_table_name), self.sqlDbConnection);
            cmd.ExecuteNonQuery()
            
        finally:
            self.sqlDbConnection.Close()    

        self.bulkcopy = Data.SqlClient.SqlBulkCopy(self.mssql_connection_String
                                       ,Data.SqlClient.SqlBulkCopyOptions.TableLock
                                       ,BulkCopyTimeout=0
                                       ,DestinationTableName=self.target_table_name
                                       )
        self.bulkcopy.DestinationTableName=self.target_table_name
        self.count = 0

        
        self.workTable = Data.DataTable()
        self.workTable.Columns.Add("[Dim0]",  Int32)
        self.workTable.Columns.Add("[Dim1]",  Int32)
        self.workTable.Columns.Add("[Dim2]",  Int32)
        self.workTable.Columns.Add("[Dim3]",  Int32)
        self.workTable.Columns.Add("[Dim4]",  Int32)
        self.workTable.Columns.Add("[Dim5]",  Int32)
        self.workTable.Columns.Add("[Dim6]",  Int32)
        self.workTable.Columns.Add("[Dim7]",  Int32)
        self.workTable.Columns.Add("[Dim8]",  Int32)
        self.workTable.Columns.Add("[Dim9]",  Int32)
        self.workTable.Columns.Add("[Dim10]", Int32)
        self.workTable.Columns.Add("[Dim11]", Int32)
        self.workTable.Columns.Add("[Key]",   Array[Byte])
        self.workTable.Columns.Add("[Data]",  Array[Byte])


    
    def _build_insert_array(self,record):
        
        insert_array = [_cast_to_Int32(record['dim0'])  
                       ,_cast_to_Int32(record['dim1'])  
                       ,_cast_to_Int32(record['dim2'])  
                       ,_cast_to_Int32(record['dim3'])  
                       ,_cast_to_Int32(record['dim4'])  
                       ,_cast_to_Int32(record['dim5'])  
                       ,_cast_to_Int32(record['dim6'])  
                       ,_cast_to_Int32(record['dim7'])  
                       ,_cast_to_Int32(record['dim8'])  
                       ,_cast_to_Int32(record['dim9'])  
                       ,_cast_to_Int32(record['dim10'])
                       ,self.interval_type #It looks like Dim11 is holding the interval type - e.g. 3=Month
                       #TODO - see if it is possible to just bass bytes through directly 
                       ,_cast_to_ArrayByte(record['key'])
                       ,_cast_to_ArrayByte(_encode_empower_data(record['data']) )
                       ]
        
        return insert_array
    
    def _add_array_to_worktable(self, insert_array):
        #self.workTable.Rows.Add(Array[object](insert_array))
        #self.workTable.Rows.Add(Array(insert_array))
        self.workTable.Rows.Add(Array[Object](insert_array))

    def _write_batch_to_server(self):
        self.bulkcopy.WriteToServer(self.workTable)
        self.workTable.Clear()         
    
    def insert_record(self, record):
        
        #TODO - Can we multithread this, such that records go onto a queue, and get written on a separate thread?
        
        self.count +=1
        
        #Create the data for the worktable as an array
        insert_array = self._build_insert_array(record)
        
        #Add data to the worktable
        self._add_array_to_worktable(insert_array)
        
        if self.count % self.batchsize == 0:
            self._write_batch_to_server()


    def flush(self):
        # Add in all the remaining rows since the last clear
        if self.workTable.Rows.Count > 0 :
            self.bulkcopy.WriteToServer(self.workTable)
            self.workTable.Clear()

    
    def __del__(self): 
        try:
            if self.bulkcopy:
                self.bulkcopy.Close()
                self.bulkcopy.Dispose()
        except AttributeError:
            pass
        
        try:
            if self.workTable:    
                self.workTable.Dispose()
        except AttributeError:
            pass
        
        #Do Garbage Collection?

def _apply_inserts(cnxn,shard_suffix):

    clustered_pk_sql = '''ALTER TABLE [dbo].[data_{}_inserts] ADD  CONSTRAINT [PK_data_{}_inserts] PRIMARY KEY CLUSTERED 
    (
        [Key] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    '''.format(shard_suffix,shard_suffix) 
    
    #Create insert sql
    insert_sql = '''INSERT into [dbo].[Data]
                    SELECT * FROM [dbo].[data_{}_inserts]
                    '''.format(shard_suffix)  
    
    with cnxn.cursor() as cursor:
        log.verbose('Creating [PK_data_{}_inserts]'.format(shard_suffix))
        cursor.execute(clustered_pk_sql)
        cnxn.commit()    
        log.verbose('Inserting from [data_{}_inserts]'.format(shard_suffix))
        cursor.execute(insert_sql)
        cnxn.commit() 
    
    
def _apply_updates(cnxn,shard_suffix):
    
    clustered_pk_sql = '''ALTER TABLE [dbo].[data_{}_updates] ADD  CONSTRAINT [PK_data_{}_updates] PRIMARY KEY CLUSTERED 
    (
        [Key] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    '''.format(shard_suffix,shard_suffix) 
    
    
    #Create update sql
    update_sql = '''UPDATE [dbo].[Data] 
                    SET [data] = src.[data]
                    FROM [dbo].[data_{}_updates] src
                    where [dbo].[Data].[Key] = src.[Key]    
                    '''.format(shard_suffix) 
    
    with cnxn.cursor() as cursor:
        log.verbose('Creating [PK_data_{}_updates]'.format(shard_suffix))
        cursor.execute(clustered_pk_sql)
        cnxn.commit()    
        log.verbose('Updating from [data_{}_updates]'.format(shard_suffix))
        cursor.execute(update_sql)
        cnxn.commit()    
    
def _apply_deletes(cnxn,shard_suffix):
    #Do inserts, updates and deletes
   
    clustered_pk_sql = '''ALTER TABLE [dbo].[data_{}_deletes] ADD  CONSTRAINT [PK_data_{}_deletes] PRIMARY KEY CLUSTERED 
    (
        [Key] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    '''.format(shard_suffix,shard_suffix) 

    
    #Create delete sql
    delete_sql = '''DELETE FROM [dbo].[Data] 
                    FROM  [dbo].[Data] tgt
                    inner join
                    [dbo].[data_{}_deletes] src
                    ON
                    tgt.[Key] = src.[Key]
                    '''.format(shard_suffix)
    
    with cnxn.cursor() as cursor:
        log.verbose('Creating [PK_data_{}_deletes]'.format(shard_suffix))
        cursor.execute(clustered_pk_sql)
        cnxn.commit()    
        log.verbose('Deleting from [data_{}_deletes]'.format(shard_suffix))
        cursor.execute(delete_sql)
        cnxn.commit()    

def _drop_tables(cnxn,shard_suffix):
    #Do inserts, updates and deletes
   
    clustered_pk_sql = '''ALTER TABLE [dbo].[data_{}_deletes] ADD  CONSTRAINT [PK_data_{}_deletes] PRIMARY KEY CLUSTERED 
    (
        [Key] ASC
    )WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
    '''.format(shard_suffix,shard_suffix) 

    
    #Create delete sql
    delete_sql = '''DELETE FROM [dbo].[Data] 
                    FROM  [dbo].[Data] tgt
                    inner join
                    [dbo].[data_{}_deletes] src
                    ON
                    tgt.[Key] = src.[Key]
                    '''.format(shard_suffix)
    
    with cnxn.cursor() as cursor:
        log.verbose('Creating [PK_data_{}_deletes]'.format(shard_suffix))
        cursor.execute(clustered_pk_sql)
        cnxn.commit()    
        log.verbose('Deleting from [data_{}_deletes]'.format(shard_suffix))
        cursor.execute(delete_sql)
        cnxn.commit() 

def _drop_tables(cnxn,shard_suffix):
    '''Drop work tables if they exists'''
    insert_table_name = 'data_{}_inserts'.format(shard_suffix)
    update_table_name = 'data_{}_updates'.format(shard_suffix)
    delete_table_name = 'data_{}_deletes'.format(shard_suffix)
    
    #Drop target tables
    insert_ddl = "IF OBJECT_ID('{}', 'U') IS NOT NULL  DROP TABLE {}".format(insert_table_name,insert_table_name)
    update_ddl = "IF OBJECT_ID('{}', 'U') IS NOT NULL  DROP TABLE {}".format(update_table_name,update_table_name)
    delete_ddl = "IF OBJECT_ID('{}', 'U') IS NOT NULL  DROP TABLE {}".format(delete_table_name,delete_table_name)

    ddl_cursor = cnxn.cursor()

    for ddl in [insert_ddl,update_ddl,delete_ddl]:
        ddl_cursor.execute(ddl)
    cnxn.commit()  
        
def _apply_data_changes(cnxn,shard_suffix):
    log.verbose('applying changes for {}'.format(shard_suffix))
    log.verbose('starting deletes for {}'.format(shard_suffix))
    _apply_deletes(cnxn,shard_suffix)
    log.verbose('starting updates for {}'.format(shard_suffix))
    _apply_updates(cnxn,shard_suffix)
    log.verbose('starting inserts for {}'.format(shard_suffix))
    _apply_inserts(cnxn,shard_suffix)
    log.verbose('dropping work tables for {}'.format(shard_suffix))
    _drop_tables(cnxn,shard_suffix)
    
    log.verbose('completed applying changes for {}'.format(shard_suffix))

def upsert_shard_merge_bulkload_work(site_locator,shard_directory,shard_prefix,shard_suffix,interval_type = 3,replace_slice_year=None, replace_slice_year_interval_min = None, replace_slice_year_interval_max = None):
    
    split_site_locator = site_locator.split('|')

    #Throw an error if site_locator doesn't begin with {SQL-KVP}
    site_type = split_site_locator[0]
    if site_type != '{SQL-KVP}':
        raise ValueError('Site locator string passed in is not a SQL Key-Value pair type site. Only SQL Key-Value pair type sites can be used with this function. The passed site_locator was "{}"'.format(split_site_locator))
    
    connection_string_template = split_site_locator[1]
    server_name_and_port       = split_site_locator[2]
    database_name              = split_site_locator[3]

    #shard_suffix = '00I' #Rather big
    #r"C:\Users\jonathan.treloar\Desktop\TR Rewrite\data\11.3 Shards Ready to Load\Shard_{}.tsv".format(shard_suffix)
    source_file = os.path.join(shard_directory, shard_prefix+shard_suffix+'.tsv') 

    mssql_connection_String = r"""Server={};
                  Database={};
                  Trusted_Connection=yes;""".format(server_name_and_port,database_name)
    odbc_connection_String = r"""Driver={SQL Server Native Client 11.0};"""+mssql_connection_String
    
    #Open up a sql connection
    cnxn = pyodbc.connect(odbc_connection_String)

    #Merge data from Empwoer with the data from the shard file
    
    first_physid,last_physid = llu.empower_file_suffix_to_physid(shard_suffix)

    generic_ddl = '''CREATE TABLE {}(
        [Dim0] [int] NOT NULL,
        [Dim1] [int] NOT NULL,
        [Dim2] [int] NOT NULL,
        [Dim3] [int] NOT NULL,
        [Dim4] [int] NOT NULL,
        [Dim5] [int] NOT NULL,
        [Dim6] [int] NOT NULL,
        [Dim7] [int] NOT NULL,
        [Dim8] [int] NOT NULL,
        [Dim9] [int] NOT NULL,
        [Dim10] [int] NOT NULL,
        [Dim11] [int] NOT NULL,
        [Key] [binary](46) NOT NULL,
        [Data] [varbinary](max) NULL,
    ) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]'''

    insert_table_name = 'data_{}_inserts'.format(shard_suffix)
    update_table_name = 'data_{}_updates'.format(shard_suffix)
    delete_table_name = 'data_{}_deletes'.format(shard_suffix)

    _drop_tables(cnxn, shard_suffix)
    
    #Create target tables
    insert_ddl = generic_ddl.format(insert_table_name)
    update_ddl = generic_ddl.format(update_table_name)
    delete_ddl = generic_ddl.format(delete_table_name)

    ddl_cursor = cnxn.cursor()

    for ddl in [insert_ddl,update_ddl,delete_ddl]:
        ddl_cursor.execute(ddl)
    cnxn.commit()   

    empower_gen = _yield_empower_records(cnxn,first_physid=first_physid,last_physid=last_physid,interval_type=3)
    shard_gen = _yield_from_ordered_shard(source_file)

    count_inserts = 0
    count_updates = 0
    count_deletes = 0
    count_unchanged = 0

    inserts_hose = _SQLServerDataHose(mssql_connection_String, target_table_name=insert_table_name,interval_type=interval_type)
    updates_hose = _SQLServerDataHose(mssql_connection_String, target_table_name=update_table_name,interval_type=interval_type)
    deletes_hose = _SQLServerDataHose(mssql_connection_String, target_table_name=delete_table_name,interval_type=interval_type)
    n=0
    for r in _interleave_shard_and_empower_records(empower_gen=empower_gen
                                                 ,shard_gen=shard_gen
                                                 ,replace_slice_year=replace_slice_year
                                                 ,replace_slice_year_interval_min = replace_slice_year_interval_min
                                                 ,replace_slice_year_interval_max = replace_slice_year_interval_max
                                                 ,shard_suffix=shard_suffix):

        n+=1
        try:
            change_status = r['change_status']
        except KeyError:
            print(r) 
            print('insert', count_inserts)
            print('update', count_updates)
            print('delete', count_deletes)
            print('no_change', count_unchanged)
            print('n',n)
            raise
        if change_status == 'insert':
            inserts_hose.insert_record(r)
            count_inserts +=1
            if count_inserts % 250000 == 0:
                log.verbose("{} inserts/updates/deletes/nochange  +{}u{}-{}o{}".format(shard_suffix,count_inserts,count_updates,count_deletes,count_unchanged))

        elif change_status == 'update':
            updates_hose.insert_record(r)
            count_updates +=1
            if count_updates % 250000 == 0:
                log.verbose("{} inserts/updates/deletes/nochange  +{}u{}-{}o{}".format(shard_suffix,count_inserts,count_updates,count_deletes,count_unchanged))
        elif change_status == 'delete':
            deletes_hose.insert_record(r)
            count_deletes +=1
            if count_deletes % 250000 == 0:
                log.verbose("{} inserts/updates/deletes/nochange  +{}u{}-{}o{}".format(shard_suffix,count_inserts,count_updates,count_deletes,count_unchanged))
        elif change_status == 'no_change':
            #TODO - remove this
            #deletes_hose.insert_record(r)
            count_unchanged +=1
            if count_unchanged % 250000 == 0:
                log.verbose("{} inserts/updates/deletes/nochange  +{}u{}-{}o{}".format(shard_suffix,count_inserts,count_updates,count_deletes,count_unchanged))
        else:
            raise ValueError()

    inserts_hose.flush()
    updates_hose.flush()
    deletes_hose.flush()

    inserts_hose = None
    updates_hose = None
    deletes_hose = None

    log.verbose("insert {}".format(count_inserts))
    log.verbose("update {}".format(count_updates))
    log.verbose("delete {}".format(count_deletes))
    log.verbose("no_change {}".format(count_unchanged))


    
    cnxn.close()

def upsert_shard_merge_sql_work(site_locator,shard_suffix):
    
    split_site_locator = site_locator.split('|')

    #Throw an error if site_locator doesn't begin with {SQL-KVP}
    site_type = split_site_locator[0]
    if site_type != '{SQL-KVP}':
        raise ValueError('Site locator string passed in is not a SQL Key-Value pair type site. Only SQL Key-Value pair type sites can be used with this function. The passed site_locator was "{}"'.format(split_site_locator))
    
    connection_string_template = split_site_locator[1]
    server_name_and_port       = split_site_locator[2]
    database_name              = split_site_locator[3]

    mssql_connection_String = r"""Server={};
                  Database={};
                  Trusted_Connection=yes;""".format(server_name_and_port,database_name)
    odbc_connection_String = r"""Driver={SQL Server Native Client 11.0};"""+mssql_connection_String
    
    #Open up a sql connection
    with pyodbc.connect(odbc_connection_String) as cnxn:

        _apply_data_changes(cnxn,shard_suffix)
    
    #cnxn.close()
    
def perform_sql_server_work(site_locator = None, sql_work_queue = None, success_queue = None,logging_queue=None):
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
    
    log.verbose('Starting _sqlkvpdirect sql server worker')
    
    exitcode=None
    try:
        
        while True:
            msg=sql_work_queue.get()
            if  msg==FAILED:
                success_queue.put(FAILED)
                raise mpex.UpstreamFailureError('Upstream Queuing Process Failed')
                break
                
            #When DONE (0) stop
            if  msg==DONE:
                success_queue.put(DONE)
                #Put a done message on the sql-server operations queue, so it knows that its work is finished
                break
                
            else:
                #Get a shard off the queue
                shard_suffix=msg

                #TODO - add a 
                upsert_shard_merge_sql_work(site_locator = site_locator
                                     ,shard_suffix = shard_suffix
                                     )
                
                #Record the task completion
                success_queue.put(shard_suffix)
    
        exitcode=0
        log.verbose('Load has completed all work on the queue')
        
    except mpex.UpstreamFailureError:
        log.error('SQL Work stopping because Upstream Process Failed')
        exitcode=1 
    except Exception as e:
        try:
            log.error(str(e)) 
        except Exception:
            pass
    
        exitcode=1 
    
    finally:
        if success_queue:
            try:
                success_queue.close()
            except Exception:
                pass
        
        if exitcode:
            try:
                log.debug('Exiting with exitcode '+str(exitcode))   
            except Exception:
                pass
            sys.exit(exitcode)
    
        log.debug('Exiting with 0')
        sys.exit(0)       


#Version for monkeypatching into low_level_utilities
def msgsink__run_single_sql_empower_bulk_load(bulkload_queue=None
                                             ,empower_main_site=None
                                             #,empower_work_site=None
                                             ,encrypted_empower_user=None
                                             ,encrypted_empower_pwd=None
                                             ,bulk_load_processing_dir=None
                                             ,shard_file_prefix=None
                                             ,empower_importer_executable=None
                                             ,logging_queue=None
                                             ):
    '''
    Poll the bulkload_queue, and bulk load single shards of data into the Empower site
    
    * In a loop, getting messages from the bulkload_queue until the DONE message is received:
    * For each message, which refers to a single shard of data (i.e. a single storage dimension entity, and therefore a single storage file)
    * Bulk load into the work site
        
    .. note::
        Unlike with eks processing, we don't use multiple work sites for bulk loading eks
    
    :param empower_importer_executable: (str) path to the Empower Importer Console executable 
    ..  note::
        This must be the console version of importer, not the GUI version
    :param bulkload_queue: The multiprocessing.Queue which communicates which shards are ready for bulk loading. Shards are pulled from this queue and processed
    :param logging_queue: multiprocessing.Queue, if we are logging to file, we need a queue created in conjunction with the filelogger process to send logging messages to
    '''
    
    #Get a logger for use in this thread
    log = logconfig.get_logger()
    if logging_queue:
        logconfig.add_queue_handler(logging_queue,log)
    
    log.verbose('Running _sqlkvpdirect bulk loader')
    
    exitcode=None
    try:
        while True:
            msg=bulkload_queue.get()
            if  msg==FAILED:
                raise mpex.UpstreamFailureError('Upstream Queuing Process Failed')
                break
                
            #When DONE (0) stop
            if  msg==DONE:
                #Put a done message on the sql-server operations queue, so it knows that its work is finished
                break
                
            else:
                #Get a shard off the queue
                shard_suffix=msg
                
                #Work split into two parts, because SQL work originally run on a different thread, only this caused instability and didn't reduce load time
                upsert_shard_merge_bulkload_work(site_locator = empower_main_site
                            ,shard_directory = bulk_load_processing_dir
                            ,shard_prefix = shard_file_prefix
                            ,shard_suffix = shard_suffix
                            ,interval_type = 3
                            ,replace_slice_year=None
                            ,replace_slice_year_interval_min = None
                            ,replace_slice_year_interval_max = None)
                            
                upsert_shard_merge_sql_work(site_locator = empower_main_site
                                             ,shard_suffix = shard_suffix
                                             )

        exitcode=0
        log.verbose('Load has completed all work on the queue')
        
    except mpex.UpstreamFailureError:
        log.error('Load stopping because Upstream Process Failed')
        if exit_on_failure:
            exitcode=1 
    except Exception as e:
        try:
            log.error(str(e)) 
        except Exception:
            pass
    
        if exit_on_failure:
            exitcode=1 
    
    finally:
        if bulkload_queue:
            try:
                log.debug('Disposing of bulkload queue')
                bulkload_queue.dispose()
                log.debug('Disposed of bulkload queue')
                
            except Exception as e:
                try:
                    log.error(str(e))    
                except Exception:
                    pass
                    
        if exitcode:
            try:
                log.debug('Exiting with exitcode '+str(exitcode))   
            except Exception:
                pass
            sys.exit(exitcode)
    
        log.debug('Exiting with 0')
        sys.exit(0)       
        

#TODO - create a process which         