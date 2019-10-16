""" functions to open the device list excel sheet 

device_dictionary = open_device_list(file_path)

"""

from openpyxl import load_workbook
from . import io 
from . import keys as K

COVER_SHEET = "Cover Sheet"
DEVICELIST_SHEET = "DeviceList"

VERSION_CELL = 'G7'

def version2rules(version):
    """ from a file version create the rules to read the data sheet 
    
    This should be replace by some rules writen inside the excel data sheet
    """
    if version in ('1D5', '1D6'):
        # from A to Z
        columns = [chr(x) for x in range(65, 65+26)]
        #from AA to AP
        columns +=  ['A'+chr(x) for x in range(65, 65+18)]
        rows = list(range(4, 138))
        return {'columns':columns, 
                'rows':rows, 
                'header_row': 2, # the row where to find the header
                'key_col': 'E',   # the column which correspond to the dictionary key e.i. a unique name id
                'column_patch': {'T':'#2'}
                }
    raise ValueError('version %s cannot be read. version2rules function need to be updated to read the given version'%version)


def open_device_list(file_path, version_cell=None, rules=None):
    f""" open the excel sheet device list into a python dictionary 
    
    A version number is checked on the coversheet at #G7 in order to load the 
    right columns and row of the device list. 
    
    If the version is not recognized one have to edit the version2rules function
    
    Args
    ----
    file_path: string, excel file path of device list. 
    version_cell : string, optional. default is {VERSION_CELL} the column where to find the version information 
    rules: None or dict, optional, default is None. 
        if a dictionary it may contain 'columns', 'rows', 'header_row' and 'key_col' keywords to set 
        the a list of columns to read, a list of rows to read, the table header_row and the column containing unique name
        if None the rules will be set according to version (see function version2rules)
    """
    wb = load_workbook(file_path, data_only=True)
    version_cell = version_cell or VERSION_CELL
    
    # loock for a version in Cover Sheet
    if rules is None:
        try:
            cvs = wb[COVER_SHEET]
        except (ValueError, KeyError):
            raise IOError('the excel file does not contain a %r sheet, cannot check version'%COVER_SHEET)
        else:
            version = cvs[version_cell].value.strip()
            if not version:
                raise IOError('cannot find version information at %s from the %r'%(version_cell, COVER_SHEET))
            rules = version2rules(version)
    
        
    try:
        dvl = wb[DEVICELIST_SHEET]
    except (ValueError, KeyError):
        raise IOError('the excel file does not contain a %r sheet, cannot check version'%DEVICELIST_SHEET)
    else:        
        data_dict, header_dict = read_device_list(dvl, **rules)
    return data_dict, header_dict     
    
    

def read_device_list(sheet, header_row=1, key_col='A', columns=None, rows=None, column_patch=None):
    """read the device list sheet
    
    Args
    ----
    sheet: excel sheet containing dvice list 
    header_row: row where to find the dictionary header 
    key_col: column containing a unique device id 
    columns: list of string of columns to read 
    rows: list of int of rows to read
    
    Returns
    -------
    data_dict : dictionary containing devices, keys are unique name device id
    header_dict:  dictionary containing columns (device properties) information
    
    """
    # arbitrary columns and rows, normaly should depend on version 
    if columns is None: columns=[chr(x) for x in range(65, 65+26)]
    if rows is None: rows=list(range(2,100))
    
    # at time of writing progam some columns had the same name 
    # this will go away when column will have correct name in the spread sheet
    if column_patch is None:
        column_patch = {}
    
    
    device_conf = io.load_device_conf('devices.yaml')
    
    device_colum_to_python_loockup = {d['xls_col_name']:k for k,d in device_conf.items()}
    
    # read the header 
    header = {}
    fields = {}
    for col in columns:
        try:
            k = column_patch[col]
        except KeyError:
            k = sheet['%s%d'%(col,header_row)].value.strip() 
        
        pk = device_colum_to_python_loockup.get(k, k)
        
        header[col] = {'name':pk, 'xls_name':k, 'xls_col':col}
        if pk in device_conf:
            header[col].update(device_conf[pk])
        else:
            header[col].update(io.FType().init_field(pk,{}))        
        fields[header[col]['name']] = header[col]
    
    data = {}    
    
    for row in rows:
        
        key = sheet['%s%d'%(key_col,row)].value 
        if key is None: continue
        
        key = ("%s"%key).strip()    
        line = data.setdefault(key, {})
        for col, field in header.items():                        
            parser = field[K.PARSER]
            cell = '%s%d'%(col, row)
            line[field['name']] =   { K.VALUE: parser(field, sheet[cell].value), K.FIELD:field, K.CELL:cell }        
        #line['xls_row'] = row                
    return data, fields
    
