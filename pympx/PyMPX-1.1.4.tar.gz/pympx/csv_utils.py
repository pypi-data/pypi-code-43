''' Utilities to validate files - beta version - not ready for release

/****************************************************************************/
/* Metapraxis Limited                                                       */
/*                                                                          */
/* Copyright (©) Metapraxis Ltd, 1991 - 2018, all rights reserved.          */
/****************************************************************************/
/* NOTICE:  All information contained herein is, and remains the property   */
/* of Metapraxis Limited and its suppliers, if any.                         */
/* The intellectual and technical concepts contained herein are proprietary */
/* to Metapraxis Limited and its suppliers and may be covered by UK and     */
/* Foreign Patents, patents in process, and are protected by trade secret   */
/* or copyright law.  Dissemination of this information or reproduction of  */
/* this material is strictly forbidden unless prior written permission is   */
/* obtained from Metapraxis Limited.                                        */
/*                                                                          */
/* This file is subject to the terms and conditions defined in              */
/* file "license.txt", which is part of this source code package.           */
/****************************************************************************/    

'''


'''There are various types of file we may wish to read
 * Fixed length
 * Delimited
 * Formatted (e.g. xml/json)
 * Excel/Spreadsheet
 * Other e.g. loose text
 
 
'''

import os
import datetime
import math
import re
import json
import inspect

STANDARD_ENCODINGS=['utf-8']


class ProfilerJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        #if hasattr(obj, "to_json"):
        #    return self.default(('~~'+str(type(obj))+'~~',obj.to_json()))
        
        if type(obj) is FileProfile or type(obj) is FileInstanceProfile or type(obj) is TypeStats or type(obj) is FieldProfile:
        
            return ('~~'+obj.__class__.__name__+'~~', obj.as_dict)
        else:
            #Let the base class raise the type error
            return json.JSONEncoder.default(self, obj)
        
#For use as a JSON decoder custom object hook    
def profile_from_json(json_object):
        if 'fname' in json_object:
            return FileItem(json_object['fname'])


class TypeStats():
    '''Statistics for a single column or cell, on a single file instance'''
    def __init__(self,type,number,min=None,max=None,first=None,last=None,min_row=None,max_row=None,number_unique=None,values_found=None,values_file=None):
        self.type=type
        self.number=number
        self.min=min
        self.max=max
        self.first=first
        self.last=last
        self.min_row=min_row
        self.max_row=max_row
        self.number_unique=number_unique
        self.values_found=values_found

    @property
    def as_dict(self):
    
        inner_dict={'number':self.number}
        if self.min is not None:
            inner_dict['min']=self.min
        if self.max is not None:
            inner_dict['max']=self.max
        if self.first is not None:
            inner_dict['first']=self.first
        if self.last is not None:
            inner_dict['last']=self.last
        if self.min_row is not None:
            inner_dict['min_row']=self.min_row
        if self.max_row is not None:
            inner_dict['max_row']=self.max_row
        if self.number_unique is not None:
            inner_dict['number_unique']=self.number_unique
        if self.values_found is not None:
            inner_dict['values_found']=self.values_found
                            
        return {self.type:  inner_dict}        
            
class FileProfile():
    '''A file profile will have general information about a file, and detailed information about columns and so on'''

    def __init__(self,file_instances=None,json_profile=None):
        
        #The instances of this file
        self.file_instances=[]
        self.name=None
        self.encoding=None
        self.delimiter=None
        self.quotechar=None
        self.most_common_column_count=None
        self.header=[]
        self.columns=[]

        if json_profile:
            input_json_dict=json.loads(json_profile)
            self.name=input_json_dict['name']
            
            fileinfo=input_json_dict['fileinfo']
            #fileinfo['type']='delimited'
            self.encoding=fileinfo['encoding']
            self.delimiter=fileinfo['delimiter']
            self.quotechar=fileinfo['quotechar']
            
            ##In future may have multiple datablocks per file - especially excel
            datablocks=input_json_dict['datablocks']
            db1=datablocks[0]
            self.header=db1['header']
            self.columns=db1['columns']
            self.column_count=len(self.columns)
            
        elif file_instances:
            self.build_from_instances(file_instances)
        
    
    def build_from_instances(self, fileinstanceprofiles):
        
        if fileinstanceprofiles is str:
            self.file_instances=[fileinstanceprofiles]
        else:
            self.file_instances=[f for f in fileinstanceprofiles]
        
        if len(self.file_instances) > 0:
            self.name=self.file_instances[0].name
        
        encodings={}
        delimiters={}
        quotechars={}
        column_counts={}
        for fp in self.file_instances:
            try:
                encodings[fp.encoding]+=1
            except KeyError:
                encodings[fp.encoding]=1
            try:
                delimiters[fp.chosen_delimiter]+=1
            except KeyError:
                delimiters[fp.chosen_delimiter]=1
            try:
                quotechars[fp.chosen_quotechar]+=1
            except KeyError:
                quotechars[fp.chosen_quotechar]=1
            try:
                column_counts[fp.column_count]+=1
            except KeyError:
                column_counts[fp.column_count]=1
        
        encodings=[(v,k) for k,v in encodings.items()]
        encodings.sort(reverse=True)
        #Get the second part, the encoding, after we have sorted by size
        self.encoding=encodings[0][1]
            
        delimiters=[(v,k) for k,v in delimiters.items()]
        delimiters.sort(reverse=True)
        #Get the second part, the delimiter, after we have sorted by size
        self.delimiter=delimiters[0][1]
        
        quotechars=[(v,k) for k,v in quotechars.items()]
        quotechars.sort(reverse=True)
        #Get the second part, the quote character, after we have sorted by size
        self.quotechar=quotechars[0][1]
        
        column_counts=[(v,k) for k,v in column_counts.items()]
        column_counts.sort(reverse=True)
        #Get the second part, the delimiter, after we have sorted by size
        self.most_common_column_count=column_counts[0][1]


    @property
    def as_dict(self):
        output_json_dict={}
        #output_json_dict['profiled_file_path']=self._filepath
        #output_json_dict['profiled_modified_date']=self.date_modified.isoformat()
        output_json_dict['name']=self.name
        fileinfo={}
        fileinfo['type']='delimited'
        fileinfo['encoding']=self.encoding
        fileinfo['delimiter']=self.delimiter
        fileinfo['quotechar']=self.quotechar
        output_json_dict['fileinfo']=fileinfo
        #In future may have multiple datablocks per file - especially excel
        datablocks=[]
        db1={}
        db1['header']=self.header
        db1['columns']=self.columns
        datablocks=[db1]
        
        output_json_dict['datablocks']=datablocks
        return output_json_dict
        
        
class FileInstanceProfile():
    '''A file instance profile will have general information about a single example of a file, and further detailed information about columns and so on'''

    def __init__(self,filepath=None,json_profile=None):
        
        if json_profile:
            input_json_dict=json.loads(json_profile)
            self._filepath=input_json_dict['profiled_file_path']
            self.name=input_json_dict['name']
            self.date_modified= datetime.datetime.strptime(input_json_dict['profiled_modified_date'],'%Y-%m-%dT%H:%M:%S.%f')
            
            fileinfo=input_json_dict['fileinfo']
            #fileinfo['type']='delimited'
            self.chosen_encoding=fileinfo['encoding']
            self.chosen_delimiter=fileinfo['delimiter']
            self.chosen_quotechar=fileinfo['quotechar']
            
            ##In future may have multiple datablocks per file - especially excel
            datablocks=input_json_dict['datablocks']
            db1=datablocks[0]
            self.header=db1['header']
            self.columns=db1['columns']
            self.column_count=len(self.columns)
            
        else:
            self._filepath=filepath
            self.chosen_encoding=None
            self.chosen_delimiter=None
            self.chosen_quotechar=None
            #header is separate to columns
            #header may be empty
            #header may not match the column defniitions we found (especially if there were more/less headers than columns
            self.header=[]
            self.columns=[]
            self.name=os.path.basename(os.path.abspath(filepath))
            self.date_modified=datetime.datetime.fromtimestamp(os.path.getmtime(filepath) )

                    
        
    def profile_self(self,line_endings=['\n'],delimiters=['\t',',',';','|'],quote_chars=['"'],encodings=STANDARD_ENCODINGS,stop_at_first_good_encoding=True):
    
        self.chosen_quotechar='"'
        
        #Create a dictionary for holding the results of various encodings
        encoding_results={}
    
        compiled_regexes={}
        #TODO use itertools product to combine with different quote_chars
        for d in delimiters:
            #Create a lookup for combination of delimiter and quote character
            q='"'
            #compiled_regexes[(d,'"')]=  re.compile(r'((?:[^'+d+q+r']|'+q+r'[^'+q+']*'+q+')+)')
            #regex='''['''+d+r'''](?=(?:[^"]"[^"]*")*$)'''
            regex=r'''(?:^|'''+d+r''')(?=[^'''+q+r''']|('''+q+r''')?)'''+q+r'''?((?(1)[^'''+q+r''']*|[^'''+d+q+r''']*))'''+q+r'''?(?='''+d+r'''|$)'''
            #print(regex)
            compiled_regexes[(d,'"')]=  re.compile(regex)
            #PATTERN = re.compile(r'((?:[^;"]|"[^"]*")+)')           
    
        for encoding in encodings:
            #Hold the results in a dictionary
            this_encoding_results={}
            encoding_results[encoding]=this_encoding_results
            with open(self._filepath,mode='r',encoding=encoding) as f:
                delimiter_results={d:{'number_of_columns':{}} for d in delimiters}
                this_encoding_results['delimiter_results']=delimiter_results
                try:
                    for line_number, line in enumerate(f):
                        for delimiter in delimiters:
                            #get the single_line_delimiter_result results
                            delimiter_result=delimiter_results[delimiter]
                            #Treat regex special characters differently - we can't build special regexes for each of them yet
                            if delimiter in ['|','^','$']:
                                line_as_list=line.split(delimiter)
                            else:
                                #Replace double quotes - ideally we'd replace with something recoverable - like a glagolitic character
                                line=line.replace('""','').replace('\n','')
                                line_as_list=compiled_regexes[(delimiter,'"')].split(line)[2::3]
                                
                            #print(delimiter)
                            #print(line)
                            #print(line_as_list)
                            #print()
                            number_of_columns=len(line_as_list)
                            try:
                                delimiter_result['number_of_columns'][number_of_columns].append(line_number)
                            except KeyError:
                                delimiter_result['number_of_columns'][number_of_columns]=[line_number]
                        
                    this_encoding_results['decoded_correctly']=True
                    if stop_at_first_good_encoding:
                        break
                except EncodingError:
                    this_encoding_results['decoded_correctly']=False
                    
                finally:
                    this_encoding_results['line_count']=line_number

        
        self.chosen_encoding='utf-8'
        self.chosen_line_count=encoding_results[self.chosen_encoding]['line_count']
        self.chosen_delimiter=FileInstanceProfile._choose_delimiter(encoding_results,self.chosen_encoding)
        
        delimiter_result=delimiter_results[self.chosen_delimiter]    
        possible_column_lengths=encoding_results[self.chosen_encoding]['delimiter_results'][self.chosen_delimiter]['number_of_columns']
        
        #If there is only one possible column length, use it 
        if len(possible_column_lengths)==1:
            self.column_count=list(possible_column_lengths.keys())[0]
        else:
            self.column_count=FileInstanceProfile._choose_column_count(possible_column_lengths,total_number_of_records=self.chosen_line_count)

        self.column_lengths = {k:len(v) for k,v in possible_column_lengths.items()}
        
        self.contiguous_ranges = []
        for col_length, row_nums in possible_column_lengths.items():
            previous_row_num = None
            current_range_start = row_nums[0]
            current_range_end = row_nums[0]
            
            for row_num in row_nums:
            
                if previous_row_num is None or row_num == previous_row_num+1:
                    current_range_end = row_num
                else:
                    self.contiguous_ranges.append((current_range_start,current_range_end,col_length))
                    current_range_start = row_num
                    current_range_end = row_num
                
                previous_row_num=row_num
            
            self.contiguous_ranges.append((current_range_start,current_range_end,col_length))

        self.contiguous_ranges.sort()

        
    def _choose_column_count(possible_column_lengths,total_number_of_records):
        number_of_columns_sorted_by_frequency=sorted([(len(v),k) for k,v in possible_column_lengths.items()],reverse=True)
        most_common_column_count=number_of_columns_sorted_by_frequency[0][1]
        return most_common_column_count
        
    def _choose_delimiter(encoding_results,chosen_encoding):
        '''Choose a delimiter, based on the column statistics
        
        * If a delimiter result is consistent
        '''
        total_number_of_records=encoding_results[chosen_encoding]['line_count']
        
        delimiter_scores=[]
        for delimiter, delimiter_result in encoding_results[chosen_encoding]['delimiter_results'].items():
            #append a tuple of score and delimiter
            delimiter_scores.append((FileInstanceProfile._score_delimiter_result(delimiter_result,total_number_of_records),delimiter))
        
        delimiter_scores.sort(reverse=True)
        
        #Get the delimiter, the second element of the highest delimiter score
        return delimiter_scores[0][1]
        
    def _score_delimiter_result(delimiter_result,total_number_of_records):
        number_of_columns_sorted_by_frequency=sorted([(v,k) for k,v in delimiter_result['number_of_columns'].items()],reverse=True)
        
        #number_of_columns_sorted_by_frequency[0] is the highest tuple on the list. [1] is the column count
        most_common_column_count=number_of_columns_sorted_by_frequency[0][1]
        count_different_column_lengths=len(number_of_columns_sorted_by_frequency)
        
        score=(most_common_column_count/total_number_of_records) / math.sqrt(count_different_column_lengths)
        
        return score

    @property
    def as_dict(self):
        output_json_dict={}
        output_json_dict['profiled_file_path']=self._filepath
        output_json_dict['profiled_modified_date']=self.date_modified.isoformat()
        output_json_dict['name']=self.name
        fileinfo={}
        fileinfo['type']='delimited'
        fileinfo['encoding']=self.chosen_encoding
        fileinfo['delimiter']=self.chosen_delimiter
        fileinfo['quotechar']=self.chosen_quotechar
        output_json_dict['fileinfo']=fileinfo
        #In future may have multiple datablocks per file - especially excel
        datablocks=[]
        db1={}
        db1['header']=self.header
        db1['columns']=self.columns
        datablocks=[db1]
        
        output_json_dict['datablocks']=datablocks
        return output_json_dict
        
class FieldProfile():
    '''A field will have a type (column,row or cell) and a name, when used in a file instance it will have a column position'''
    pass
    
    def __init__(self,source_dict=None):
        if source_dict is not None:
            self.from_dict(source_dict)
    
    @property    
    def as_dict(self):
        result={}
        result['sample_method']=self.sample_method
        result['sample_size']=self.sample_size
        result['type_stats']={}
        for ts in self.type_stats:
            for k,v in ts.as_dict.items():
                result['type_stats'][k]=v
        
        return result
    
    def from_dict(self,source_dict):
        pass
        

class DataProfile():
    '''A data profile '''
    pass
    
#def profile_a_file(filename):
#    file_profile=FileProfile()
#    
#    return file_profile
    
    
if __name__=='__main__':    
    
    filename='.\test_data\test_single_column_with_header.csv'
    file_profile=profile_a_file(filename)
    print(file_profile)
    