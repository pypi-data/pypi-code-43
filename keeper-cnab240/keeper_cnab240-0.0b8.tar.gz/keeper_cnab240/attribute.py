from unicodedata import normalize


class Attribute:
    def __init__(self, name, attr_type, length, start, end, default_value='', pad_content=0, pad_direction='left',
                 required=False):
        self.name = name
        self.type = attr_type
        self.length = length
        self.start = start
        self.end = end
        self.default_value = default_value
        self.pad_content = str(pad_content)
        self.pad_direction = pad_direction
        self.required = required
        self.value = None

    def is_required(self):
        return self.required
    
    def get_value(self):
        if self.value:
            return self.value
        self.set_value(self.default_value)
        return self.value
    
    def set_value(self, new_value):
        if new_value is None:
            new_value = self.default_value
        
        if self.type == 'int':
            self.value = int(new_value)
        elif self.type == 'string':
            self.value = str(new_value)
        elif self.type == 'float':
            self.value = int(round(float(new_value), 2) * 100) if (type(new_value) is not str) else int(new_value)
        elif self.type == 'whites':
            self.value = ' '
        elif self.type == 'zeros':
            self.value = '0'
        elif self.type == 'date':
            self.value = str(new_value)
        
        self.value = str(self.value)
        self.clean_value()
        self.pad_value()
        self.value = self.value.upper()

    def clean_value(self):
        special_chars = [',', '.', '-', '_', '*', '&', '´', '`', "'", '"', '!', '?', '/', ':', ';', '>', '<',
                         '^', '~', ']', '}', '{', '[', 'ª', 'º', '#', '%', '¨', '(', ')', '+', '=', '§', '¬',
                         '£', '¹', '²', '³', '°']
        for char in special_chars:
            self.value = self.value.replace(char, '')
        self.value = normalize('NFKD', self.value).encode('ASCII', 'ignore').decode('ASCII')
    
    def pad_value(self):
        if len(self.value) < self.length:
            if self.pad_direction == 'left':
                self.value = self.value.rjust(self.length, self.pad_content)
            else:
                self.value = self.value.ljust(self.length, self.pad_content)
        elif len(self.value) > self.length:
            self.value = self.value[:self.length]
