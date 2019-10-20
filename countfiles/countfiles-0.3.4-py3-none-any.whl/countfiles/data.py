data_types = ['byte', 'kilobyte', 'megabyte', 'gigabyte', 'terabyte', 'petabyte']


def get_shorthand(name):
    s = '?'
    if name == 'byte':
        s = 'b'
    elif name == 'kilobyte':
        s = 'kb'
    elif name == 'megabyte':
        s = 'mb'
    elif name == 'gigabyte':
        s = 'gb'
    elif name == 'terabyte':
        s = 'tb'
    elif name == 'petabyte':
        s = 'pb'
    return s


def get_name(shorthand):
    n = '?'
    if shorthand == 'b':
        n = 'byte'
    elif shorthand == 'kb':
        n = 'kilobdyte'
    elif shorthand == 'mb':
        n = 'megabyte'
    elif shorthand == 'gb':
        n = 'gigabyte'
    elif shorthand == 'tb':
        n = 'terabyte'
    elif shorthand == 'pb':
        n = 'petabyte'
    return n


class Data:

    def __init__(self, value=0, start_type='byte'):
        self.value = value
        if isinstance(value, str):
            value = bytearray(value, 'utf-8')
        if isinstance(value, (bytes, bytearray)):
            self.value = len(value)
        if start_type in data_types:
            s = start_type
            if s == 'kilobyte':
                self.value *= 1024
            elif s == 'megabyte':
                self.value *= 1024 * 1024
            elif s == 'gigabyte':
                self.value *= 1024 * 1024 * 1024
            elif s == 'terabyte':
                self.value *= 1024 * 1024 * 1024 * 1024
            elif s == 'petabyte':
                self.value *= 1024 * 1024 * 1024 * 1024 * 1024

    def __repr__(self):
        return self.value
    
    def __str__(self):
        a = self.simplify()
        return str(a[0]) + a[1]

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def simplify(self, value=None):
        t = 0
        v = self.value if value is None else value
        while v >= 1024 and t < len(data_types):
            v /= 1024
            t += 1
        return v, get_shorthand(data_types[t])
    
    def convert(self, value=None, conv_type='byte'):
        if conv_type not in data_types:
            conv_type = 'byte'
        c = conv_type
        out = value
        if c == 'kilobyte':
            out /= 1024
        elif c == 'megabyte':
            out /= 1024
            out /= 1024
        elif c == 'gigabyte':
            out /= 1024
            out /= 1024
            out /= 1024
        elif c == 'terabyte':
            out /= 1024
            out /= 1024
            out /= 1024
            out /= 1024
        elif c == 'petabyte':
            out /= 1024
            out /= 1024
            out /= 1024
            out /= 1024
            out /= 1024
        return out, get_shorthand(c)
