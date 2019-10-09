from . import block

class Scripts:
    def __init__(self, all_json, target_index):
        self.all_json = all_json
        self.target_index = target_index
        self.sprite_json = self.all_json['targets'][target_index]

        self.event_method_counts = {
            'event_whenflagclicked': -1,
            'event_whenkeypressed': -1,
            'event_whenthisspriteclicked': -1,
            'event_whenbackdropswitchesto': -1,
            'event_whengreaterthan': -1,
            'event_whenbroadcastreceived': -1,
        }

        self.blocks = self.get_blocks()


        self.scripts, self.event_adders = self.get_scripts_and_event_adders()

    def generate_event_adders_code(self):
        return '\n'.join(self.event_adders)

    def generate_scripts_code(self):
        return '\n\n'.join(self.scripts)
        


    def get_blocks(self):
        block_dictionary = {}
        for block_md5 in self.sprite_json['blocks']:
            block_json = self.sprite_json['blocks'][block_md5]
            temporary_block = block.Block(self, self.all_json, self.target_index, block_md5)
            block_dictionary[block_md5] = temporary_block
        return block_dictionary

    def get_scripts_and_event_adders(self):
        scripts = []
        event_adders = []
        for block_md5 in self.blocks:
            temporary_block = self.blocks[block_md5]
            if temporary_block.top_level: # is top level block
                event_adder_code = temporary_block.generate_event_adder(2)
                event_adders.append(event_adder_code)

                script_code = temporary_block.generate_script_code(1) # makes all code below
                scripts.append(script_code)
        return scripts, event_adders