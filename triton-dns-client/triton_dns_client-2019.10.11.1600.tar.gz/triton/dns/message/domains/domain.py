import bitstring


class Domain:
    class _Binary:
        def __init__(self, domain):
            self.domain = domain

    def __init__(self, label, pos=None):
        self.injected = False
        self.label = label.replace('"', '').replace("'", '')
        self.pos = pos
        self.Binary = Domain._Binary(self)

    @classmethod
    def decode(cls, message):
        domain = []
        cut_last_octet = True
        if message.stream.peek('bin:8')[0:2] == '11':
            found_in_storage = message.domains.find_pos(int(message.stream.read('bin:16')[2:], 2))
            if found_in_storage:
                return found_in_storage
        else:
            while message.stream.peek('int:8'):
                subdomain = ''
                position = message.stream.pos
                for c in range(message.stream.read('uint:8')):
                    subdomain += chr(message.stream.read('uint:8'))
                domain.append((subdomain, position))
                if message.stream.peek('bin:8')[0:2] == '11':
                    found_in_storage = message.domains.find_pos(int(message.stream.read('bin:16')[2:], 2))
                    if found_in_storage:
                        domain.append((found_in_storage.label, message.stream.pos - 16))
                        cut_last_octet = False
                    break
                if not message.stream.peek('uint:8'):
                    break
        _domain = Domain('', None)
        try:
            if cut_last_octet:
                message.stream.read('bin:8')  # last 00000000 of length octet
        except bitstring.ReadError:
            pass
        for n, (label, pos) in enumerate(domain):
            _ = Domain('.'.join([x for m, (x, y) in enumerate(domain) if m >= n]), int(pos / 8))
            message.domains.append(_)
            if n == 0:
                _domain = _
        return _domain

    @staticmethod
    def sub_encode(label):
        if label == '' or label == '.':
            return str('').zfill(8)
        binary_string = ''
        parts = label.split('.')
        for domain_part in parts:
            binary_string += str(bin(len(domain_part))[2:]).zfill(8)
            for char in domain_part:
                binary_string += str(bin(ord(char))[2:]).zfill(8)
        binary_string += str(bin(0)[2:]).zfill(8)
        return binary_string

    def encode(self, message):
        ## TODO clean this mess maybe? but it works
        if self.label == '' or self.label == '.':
            return str('').zfill(8)
        binstring = ''
        search_result = message.domains.find(self.label)
        if isinstance(search_result, Domain):
            if search_result:
                binstring += f'11{bin(int(search_result.pos))[2:].zfill(14)}'
                return binstring
            else:
                binstring = self.sub_encode(self.label)
                return binstring
        else:
            resulting_label = ''
            for n, x in enumerate(['.'.join(self.label.split('.')[n:]) for n, x in
                                   enumerate(self.label.split('.'))]):
                subsearch_result = message.domains.find(x)
                if subsearch_result:
                    binstring += self.sub_encode(resulting_label)[:-8]
                    binstring += f'11{bin(int(subsearch_result.pos))[2:].zfill(14)}'
                    dmn = Domain('.'.join([resulting_label, subsearch_result.label]),
                                 message.offset + len(resulting_label) + 1 * n)
                    message.domains.append(dmn)
                    return binstring
                else:
                    dmn = Domain(x, message.offset + len(resulting_label) + 1 * n)
                    dmn.injected = True
                    message.domains.append(dmn)
                    resulting_label += x.split('.')[0]
            binstring += self.sub_encode(self.label)
        self.injected = True
        self.pos = message.offset
        # message.domains.append(self)
        return binstring

    @property
    def binary_raw(self):
        if self.label == '' or self.label == '.':
            return str('').zfill(8)
        binary_string = ''
        parts = self.label.split('.')
        for domain_part in parts:
            binary_string += str(bin(len(domain_part))[2:]).zfill(8)
            for char in domain_part:
                binary_string += str(bin(ord(char))[2:]).zfill(8)
        binary_string += str(bin(0)[2:]).zfill(8)
        return binary_string

    @property
    def __dict__(self):
        return self.label

    def __repr__(self):
        return f'"{self.label}"'
