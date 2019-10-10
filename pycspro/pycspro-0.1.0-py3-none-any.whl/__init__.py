name = 'pycspro'

__all__ = [
    'DictionaryParser', 
    'CaseParser'
]

from transitions import Machine
import configparser
from collections import OrderedDict
import json
import functools

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(OrderedDict, self).__setitem__(key, value)
    def keys(self):
        return super(OrderedDict, self).keys()


class DictionaryBuilder:
    ATTRIBUTE_TYPES = {
        'to_int': {'Start', 'Len', 'RecordTypeStart', 'RecordTypeLen', 'MaxRecords', 'RecordLen', 'Occurrences'}, 
        'strip_quotes_str': {'Name', 'Label', 'Note', 'Version', 'Positions', 'RecordTypeValue', 'ItemType', 'DataType'},
        'word_to_bool': {'ZeroFill', 'DecimalChar', 'Required'},
    }
    
    def __init__(self):
        self.tree = {}
        self.is_built = False
        
    def word_to_bool(self, arg):
        return arg == 'Yes'

    def pass_through(self, arg):
        return arg

    def strip_quotes_str(self, arg):
        return str(arg.strip("'"))
    
    def to_int(self, arg):
        return int(arg)

    def get_casting_function(self, key):
        for type, pool in self.ATTRIBUTE_TYPES.items():
            if key in pool:
                return type
            else:
                continue
        return 'pass_through'

    def flatten_and_cast_values(self, attributes):
        if attributes == None:
            return None
        else:
            attribs = []
            for attribute in attributes:
                key, value = attribute
                if (len(value) == 1 and key != 'Value'):
                    attribs.append(([key, getattr(self, self.get_casting_function(key), self.pass_through)(value[0])]))
                else:
                    attribs.append(attribute)
            return attribs
    
    def add_section(self, section_received, attributes):
        getattr(self, section_received, self.pass_through)(self.flatten_and_cast_values(attributes))
        
    # attributes will come as a list of tuples [('key', [values])]
    def dictionary_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Version': '',
            'RecordTypeStart': 1,
            'RecordTypeLen': 0,
            'Positions': 'Relative',
            'ZeroFill': True,
            'DecimalChar': False,
            'Languages': [],
            'Relation': [],
        }
        section.update(attributes)
        self.tree['Dictionary'] = section
        
    def level_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
        }
        section.update(attributes)
        self.tree['Dictionary']['Level'] = section

    def iditems_received(self, attributes):
        self.tree['Dictionary']['Level']['IdItems'] = []
        
    def item_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Len': 0,
            'ItemType': 'Item',
            'DataType': 'Numeric',
            'Occurrences': 1,
            'Decimal': 0,
            'DecimalChar': False,
            'ZeroFill': False,
            'OccurrenceLabel': [],
        }
        section.update(attributes)
        #self.tree['Dictionary']['Level']['IdItems'].append({'Item': section})
        self.tree['Dictionary']['Level']['IdItems'].append(section)
        
    def valueset_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Value': [],
        }
        section.update(attributes)
        #value_sets = self.tree['Dictionary']['Level']['IdItems'][-1]['Item'].get('ValueSets', [])
        value_sets = self.tree['Dictionary']['Level']['IdItems'][-1].get('ValueSets', [])
        value_sets.append(section)
        #self.tree['Dictionary']['Level']['IdItems'][-1]['Item']['ValueSets'] = value_sets
        self.tree['Dictionary']['Level']['IdItems'][-1]['ValueSets'] = value_sets
        
    def record_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'RecordTypeValue': '',
            'Required': False,
            'MaxRecords': 1,
            'RecordLen': 0,
            'OccurrenceLabel': []
        }
        section.update(attributes)
        records = self.tree['Dictionary']['Level'].get('Records', [])
        records.append(section)
        self.tree['Dictionary']['Level']['Records'] = records
        
    def record_item_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Len': 0,
            'ItemType': 'Item',
            'DataType': 'Numeric',
            'Occurrences': 1,
            'Decimal': 0,
            'DecimalChar': False,
            'ZeroFill': False,
            'OccurrenceLabel': [],
        }
        section.update(attributes)
        #items = self.tree['Dictionary']['Level']['Records'][-1]['Record'].get('Items', [])
        items = self.tree['Dictionary']['Level']['Records'][-1].get('Items', [])
        items.append(section)
        self.tree['Dictionary']['Level']['Records'][-1]['Items'] = items
        
    def record_valueset_received(self, attributes):
        section = {
            'Name': '',
            'Label': '',
            'Note': '',
            'Value': [],
        }
        section.update(attributes)
        value_sets = self.tree['Dictionary']['Level']['Records'][-1]['Items'][-1].get('ValueSets', [])
        value_sets.append(section)
        self.tree['Dictionary']['Level']['Records'][-1]['Items'][-1]['ValueSets'] = value_sets

    def completed(self, attributes):
        self.is_built = True

class CSProDictionary(object):
    def __init__(self):
        self.builder = DictionaryBuilder()
        
    def build_dictionary(self, section, section_items):
        self.builder.add_section(self.state, section_items)

class DictionaryParser:
    def __init__(self, raw_dictionary):
        self.parsed_dictionary = None
        # If present, remove BOM.
        # BOM is the character code (such as U+FEFF) at the beginning of a data stream
        # that is used to define the byte order and encoding form.
        if raw_dictionary.startswith('\ufeff'):
            self.raw_dictionary = raw_dictionary[1:]
        else:
            self.raw_dictionary = raw_dictionary
        
    def parse(self):
        model = CSProDictionary()
        states = ['empty', 'dictionary_received', 'level_received', 'iditems_received', 'item_received', 
                  'valueset_received', 'record_received', 'record_item_received', 'record_valueset_received', 'completed']
        transitions = [
            {'trigger': 'Dictionary', 'source': 'empty', 'dest': 'dictionary_received'},
            {'trigger': 'Level', 'source': 'dictionary_received', 'dest': 'level_received'},
            {'trigger': 'IdItems', 'source': 'level_received', 'dest': 'iditems_received'},
            {'trigger': 'Item', 'source': 'iditems_received', 'dest': 'item_received'},
            {'trigger': 'Item', 'source': 'item_received', 'dest': 'item_received'},
            {'trigger': 'ValueSet', 'source': 'item_received', 'dest': 'valueset_received'},
            {'trigger': 'ValueSet', 'source': 'valueset_received', 'dest': 'valueset_received'},
            {'trigger': 'Item', 'source': 'valueset_received', 'dest': 'item_received'},
            {'trigger': 'Record', 'source': 'valueset_received', 'dest': 'record_received'},
            {'trigger': 'Record', 'source': 'item_received', 'dest': 'record_received'},
            {'trigger': 'Item', 'source': 'record_received', 'dest': 'record_item_received'},
            {'trigger': 'Item', 'source': 'record_item_received', 'dest': 'record_item_received'},
            {'trigger': 'ValueSet', 'source': 'record_item_received', 'dest': 'record_valueset_received'},
            {'trigger': 'ValueSet', 'source': 'record_valueset_received', 'dest': 'record_valueset_received'},
            {'trigger': 'Item', 'source': 'record_valueset_received', 'dest': 'record_item_received'},
            {'trigger': 'Record', 'source': 'record_item_received', 'dest': 'record_received'},
            {'trigger': 'Record', 'source': 'record_valueset_received', 'dest': 'record_received'},
            {'trigger': 'EOF', 'source': 'record_valueset_received', 'dest': 'completed'},
            {'trigger': 'EOF', 'source': 'record_item_received', 'dest': 'completed'}
        ]

        parser_machine = Machine(model=model, states=states, transitions=transitions, 
                                 initial='empty', after_state_change='build_dictionary')

        section_parser = configparser.RawConfigParser(strict=False, dict_type=MultiOrderedDict)
        # Maintain case as is in the incoming text. Without this option set, 
        # it will convert to lower case
        section_parser.optionxform = str
        section_separator = '\n\n' # Dictionary files tend to have this
        if self.raw_dictionary.find('\r\n\r\n') != -1: 
            section_separator = '\r\n\r\n' # but csweb db dictionaries have this
        sectioned_dictionary = self.raw_dictionary.split(section_separator)
        
        try:
            for section in sectioned_dictionary:
                section_parser.clear()
                section_parser.read_string(section)
                section_name = section_parser.sections()[0]
                items = section_parser.items(section_name)
                model.trigger(section_name, section_name, items)
            model.trigger('EOF', None, None)
        except Exception as err:
            return "Parsing error. " + str(err)

        self.parsed_dictionary = model.builder.tree if model.builder.is_built else None
        return self.parsed_dictionary
    
    def get_column_labels(self, record_name):
        if self.parsed_dictionary is not None:
            result = list(filter(lambda r: r['Record']['Name'] == record_name, self.parsed_dictionary['Dictionary']['Level']['Records']))
            if len(result) > 0:
                items = result[0]['Record']['Items']
                return dict(list(
                    map(lambda i: (i['Name'], i['Label']), items)
                ))
            else:
                return None
        else:
            return None
    
    def cast(self, value, item):
        if item['DataType'] == 'Numeric' and value != '':
            try:
                value = float(value) if item['Decimal'] else int(value)
            except ValueError:
                pass
        else:
            value = str(value)
        return value
    
    def get_value_labels(self, record_name, desired_columns = None):
        if self.parsed_dictionary is not None:
            result = list(filter(lambda r: r['Name'] == record_name, self.parsed_dictionary['Dictionary']['Level']['Records']))
            value_labels = {}
            if len(result) > 0:
                items = result[0]['Items']
                for item in items:
                    if desired_columns is not None and item['Name'] not in desired_columns:
                        continue
                    valuesets = item.get('ValueSets', None)
                    if valuesets is not None:
                        values = valuesets[0]['Value']
                        # Handle these conditions separately
                        # value = 1;Male, value = 0:120, value = 1:49;Line number, value = '   ';N/A
                        dictified = []
                        for value in values:
                            if value.find(';') != -1:
                                v, l = (value.split(';', maxsplit = 1))
                                
                                # Rethink this block 
                                try:
                                    dictified.append((self.cast(v, item), l))
                                except:
                                    pass
                            
                            
                        value_labels[item['Name']] = dict(dictified)        
                return value_labels
            else:
                return None
            
        else:
            return None


 

class CaseParser:
    def __init__(self, parsed_dictionary, cutting_mask = {}):
        self.parsed_dictionary = parsed_dictionary
        self.cutting_mask = cutting_mask
        self.is_multi_rec_type = self.parsed_dictionary['Dictionary']['RecordTypeLen'] > 0
        self.rec_type_start = self.parsed_dictionary['Dictionary']['RecordTypeStart']
        self.rec_type_len = self.parsed_dictionary['Dictionary']['RecordTypeLen']
        self.main_table_name = self.parsed_dictionary['Dictionary']['Level']['Name']
        self.iditems_columns = self.make_iditems_columns()
        self.cutters = self.make_cutters()
        
    def make_column_tuples(self, items):
        return list(map(lambda item: tuple([
                                            item['Name'], 
                                            item['Start'], 
                                            item['Len'],
                                            item['DataType'],
                                            item['DecimalChar']]), items))
        
    def make_iditems_columns(self):
        return self.make_column_tuples(self.parsed_dictionary['Dictionary']['Level']['IdItems'])
        
    def make_caseid_column_cutter(self):
        span = functools.reduce(lambda accumulator, y: accumulator + y[2], self.iditems_columns, 0)
        return [tuple(['CASE_ID', self.iditems_columns[0][1], span, 'Alpha', False])]
    
    def make_cutters(self):
        # columns is [('Name', 'Start', 'Len', 'DataType', 'DecimalChar'), ...]
        caseid_column_cutter = self.make_caseid_column_cutter()
        cutters = {}
        cutters[self.parsed_dictionary['Dictionary']['Level']['Name']] = {
            'marker': None,
            'columns': caseid_column_cutter + self.iditems_columns,
        }
        for record in self.parsed_dictionary['Dictionary']['Level']['Records']:
            columns = self.make_column_tuples(record['Items'])
            if record['Name'] in self.cutting_mask:
                desired_columns = self.cutting_mask[record['Name']]
                columns = list(filter(lambda column: column[0] in desired_columns, columns))
            cutters[record['Name']] = {
                'marker': record['RecordTypeValue'],
                'columns': caseid_column_cutter + columns,
            }
        return cutters
        
    def cut_columns(self, record, table, column_cutters):
        for column_cutter in column_cutters:
            column_name, start, span, data_type, decimal = column_cutter
            column_data = table.get(column_name, [])
            value = record[(start - 1) : (start - 1) + span].strip()
            if data_type == 'Numeric' and value != '':
                try:
                    value = float(value) if decimal else int(value)
                except ValueError:
                    pass
            else:
                value = str(value)
            column_data.append(value)
            table[column_name] = column_data
        return table
    
    def parse(self, cases):
        tables = {}
        categories = {
            self.main_table_name: self.tables_builder(tables, self.main_table_name)
        }
        next(categories[self.main_table_name])
        for case in cases:
            records = case.split('\n')
            categories[self.main_table_name].send(records[0])
            for record in records:
                marker = record[(self.rec_type_start - 1) : (self.rec_type_start - 1) + self.rec_type_len]
                record_name = list(filter(lambda k: self.cutters[k]['marker'] == marker, self.cutters))[0]
                if categories.get(record_name, None) is None:
                    categories[record_name] = self.tables_builder(tables, record_name)
                    next(categories[record_name])
                categories[record_name].send(record)
        for _, category in categories.items():
            category.send(None)
        return tables
    
    def tables_builder(self, tables, name):
        while True:
            cutter = self.cutters[name]
            tables[name] = yield from self.table_builder(cutter)
            
    def table_builder(self, cutter):
        table = {}
        while True:
            record = yield
            if record is None:
                break
            table = self.cut_columns(record, table, cutter['columns'])
        return table