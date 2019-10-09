from . import conversion_tables
from .prefs import prefs

class Block:
    def __init__(self, parent_script, all_json, target_index, block_md5):
        self.parent_script = parent_script
        self.all_json = all_json
        self.target_index = target_index
        self.sprite_json = all_json['targets'][self.target_index]
        self.name = self.sprite_json['name']
        self.block_md5 = block_md5
        self.block_json = self.sprite_json['blocks'][self.block_md5]

        self.opcode = self.find_opcode()
        self.top_level = self.find_top_level()
        self.above_block_id = self.find_above_block_id()
        self.above_block = None
        self.below_block_id = self.find_below_block_id()
        self.below_block = None
        self.inputs = self.find_inputs()
        self.indent_level = None

    def generate_event_adder(self, indent_level):
        if self.top_level:
            self.parent_script.event_method_counts[self.opcode] += 1

            self.indent_level = indent_level
            unformatted_code = conversion_tables.block_to_code[self.opcode]['event']
            formatted_code = self.format_fields_in_code(unformatted_code)

            return formatted_code
        return None

    def generate_script_code(self, indent_level):
        self.indent_level = indent_level

        self.update_neighbour_block_indexes()

        self.code = self.generate_own_code()
        below_code = self.generate_below_code()

        script_code = '{0}{1}'.format(self.code, below_code)
        return script_code


    def generate_own_code(self):
        unformatted_code = conversion_tables.block_to_code[self.opcode]['code']
        formatted_code = self.format_fields_in_code(unformatted_code)
        return formatted_code

    def format_fields_in_code(self, code):
        field_dictionary = self.generate_field_dictionary()
        for key in field_dictionary:
            if type(key).__name__ == 'str': # key needs to have '{}' around it
                find_term = '{{{0}}}'.format(key)
            elif type(key).__name__ == 'tuple': # key 
                find_term = key[0]
            replace_term = field_dictionary[key]
            code = code.replace(find_term, replace_term)
        return code

    def generate_field_dictionary(self):
        custom_fields = self.get_custom_fields()
        formatted_input_fields = self.get_formatted_input_fields()
        field_dictionary = {
            **formatted_input_fields,
            **custom_fields
        }
        return field_dictionary

    def get_custom_fields(self):
        custom_fields = {
            'project': prefs['project_variable_name'],
            'green_flag_method_prefix': prefs['green_flag_method_prefix'],
            'sprite_clicked_method_prefix': prefs['sprite_clicked_method_prefix'],
            'receive_broadcast_method_prefix': prefs['receive_broadcast_method_prefix'],
            'backdrop_switches_to_method_prefix': prefs['backdrop_switches_to_method_prefix'],
            'more_than_method_prefix': prefs['more_than_method_prefix'],
            'key_pressed_method_prefix': prefs['key_pressed_method_prefix'],
            'clone_method_name': prefs['clone_method_name'],
            'sprite_variable_prefix': prefs['sprite_variable_prefix'],
            'col_option': prefs['col_option'],
            'attribute_variable_prefix': prefs['attribute_variable_prefix'],
            'indent': prefs['indent'] * self.indent_level,
            'extra_indent': prefs['indent'] * (self.indent_level+1),
            'sprite_variable_name': self.name,
            ('_mouse_',): '\'mouse_pointer\'',
            ('_random_',): '\'random_position\''
        }
        if self.top_level:
            custom_fields['current_method_count'] = str(self.parent_script.event_method_counts[self.opcode])
        return custom_fields

    def get_formatted_input_fields(self):
        formatted_input_fields = {}
        for key in self.inputs:
            value = self.inputs[key]
            if type(value).__name__ == 'list': # is an md5 code, so replace with code
                block_md5 = value[0]
                temporary_block = self.parent_script.blocks[block_md5]
                value = temporary_block.generate_script_code(self.indent_level + 1) # increase indent as its nested
            formatted_input_fields[key] = value
        return formatted_input_fields

    def generate_below_code(self):
        if self.below_block is not None: # has a block below
            if self.top_level:
                new_indent_level = self.indent_level + 1
            else:
                new_indent_level = self.indent_level
            return self.below_block.generate_script_code(new_indent_level)
        return ''


    def update_neighbour_block_indexes(self): # is called externally afterwards
        if self.above_block_id is not None:
            self.above_block = self.parent_script.blocks[self.above_block_id]
        if self.below_block_id is not None:
            self.below_block = self.parent_script.blocks[self.below_block_id]

    def find_opcode(self):
        return self.block_json['opcode']

    def find_top_level(self):
        return self.opcode in [
            'event_whenflagclicked',
            'event_whenthisspriteclicked',
            'event_whenstageclicked',
            'event_whenbroadcastreceived',
            'event_whenbackdropswitchesto',
            'event_whengreaterthan',
            'event_whenkeypressed',
        ]

    def find_above_block_id(self):
        above_block_id = self.block_json['parent']
        return above_block_id

    def find_below_block_id(self):
        below_block_id = self.block_json['next']
        return below_block_id

    def find_inputs(self):
        input_json = self.block_json['inputs']
        field_json = self.block_json['fields']

        input_values = self.extract_input_values(input_json)
        field_values = self.extract_input_values(field_json)
        other_values = {'project': prefs['project_variable_name']}

        return {**input_values, **field_values, **other_values}

    def extract_input_values(self, input_json):
        return_inputs = {}

        for input_key in input_json:
            first_value = input_json[input_key][0]
            first_value_type = type(first_value).__name__
            second_value = input_json[input_key][1]
            second_value_type = type(second_value).__name__

            if first_value_type == 'str': # is field
                input_value = first_value

            elif second_value_type == 'list': # is value
                input_value = second_value[1]

            elif second_value_type == 'str': # is md5 id
                input_value = [second_value] # make it a list, so you know its an md5 value

            return_inputs[input_key.lower()] = input_value

        return return_inputs


"""

<md5 id>: {
  'opcode': <opcode>,
  'inputs': {
    <input name>: [<index>, [<value type>, <value>]],
    <input name>: [<index>, <md5 id>],
  },
  'fields': {
    <field name>: [<choice>, <additional info>]
  },
}


<value type>:
3 = md5 id
4 = number

10 = string




"EfOy{q7?Pg_vh^HN|+!9": {
    "shadow": false,
    "next": null,
    "inputs": {
        "SECS": [
            1,
            [
                4,
                "1"
            ]
        ],
        "TO": [
            3,
            "|p2Hs!q~bJuEm4DIPu/4",
            "sa5r,f[QsY9$(TVESgI]"
        ]
    },
    "opcode": "motion_glideto",
    "y": 379,
    "x": 142,
    "topLevel": true,
    "parent": null,
    "fields": {}
}





    def generate_add_event_code(self):
        if self.top_level:

        else:
            return

    def generate_script_code(self, indent_level):
        unformatted_code = conversion_tables.block_to_code[self.opcode]['code']
        custom_input_field = {
            **self.scripts.event_method_indexes,
            'indent_level': indent_level
        }
        formatted_code = self.fill_in_code_inputs(unformatted_code, custom_input_field)

        if self.top_level: # top level blocks are method definitions, so 1 less indented
            indentation = prefs.indent * (indent_level - 1)
        elif self.indented:
            indentation = prefs.indent * indent_level
        else:
            indentation = ''

        if self.below_block != None: # there are blocks below
            below_blocks_code = self.below_block.generate_script_code(indent_level)

        script_code = '\n'.join(this_block_code, below_block_code)
        return script_code

    def fill_in_code_inputs(self, code, custom_input_field):
        input_fields = {**self.inputs, **custom_input_field}
        input_fields['indentation'] = 
        for key in input_fields:
            find_term = '{{0}}'.format(key)
            replace_term = input_fields[key]
            if type(replace_term).__name__ == 'list': # is md5 code
                block_id = replace_term[0]
                temporary_block = self.block_dictionary[block_id]
                below_blocks_code = temporary_block.generate_script_code(indent_level+1) # recursively generate code
                replace_code = block_code
            code.replace(find_term, replace_term)
        return code
"""