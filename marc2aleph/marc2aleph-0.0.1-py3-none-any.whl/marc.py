class Converter:
    """A class for converting MARC(2709) to Aleph sequential and vice-versa"""

    def __init__(self, format=None):
        self._GS = '\x1D'
        self._RS = '\x1E'
        self._US = '\x1F'
        self._format = format

    def to_aleph(self, marc: str, asn: int = 1, fmt: str = 'BK') -> str:
        """Convert MARC(2709) to Aleph sequential.
        :param marc: MARC(2709) record
        :param asn: Aleph system number
        :param fmt: FMT field that specifies the format of the record
        :return: Aleph sequential record
        """

        if not marc:
            return ''
        marc = marc.strip('\n').replace(self._US, '$$')
        sno = str(asn % 999999999).zfill(9) + ' '
        records = [sno + 'FMT   L ' + fmt]
        base = marc.find(self._RS)
        if base == -1 or base % 12 != 0:
            return ''
        field_count = marc.count(self._RS)
        if field_count != base / 12 - 1:
            return ''
        for i in range(24 + 3, base, 12):
            if not marc[i:i + 9].isdigit():
                return ''
        leader = marc[0:24].replace(' ', '^')
        records.append(sno + 'LDR   L ' + leader)
        fields = marc[base + 1:].split(self._RS)
        for i in range(0, field_count - 1):
            tag = marc[i * 12 + 24:i * 12 + 27]
            label = sno + tag
            if tag.startswith('00'):
                records.append(label + '   L ' + fields[i].replace(' ', '^'))
                continue
            lang = ' L '
            content = fields[i][2:]
            if self._format == 'cnmarc':
                if not fields[i].isascii():
                    lang = ' C '
                if tag in ('100', '105'):
                    content = content.replace(' ', '^')
                elif tag in ('461', '462', '463'):
                    content = content.replace(' $$', '^$$')
            records.append(label + fields[i][0:2] + lang + content)
        return '\n'.join(records)

    def to_marc(self, record: str, encoding: str = 'UTF-8') -> str:
        """Convert Aleph sequential to MARC(2709).
        :param record: Aleph sequential record
        :param encoding:
        :return: MARC(2709) record
        """
        if not record:
            return ''
        directory = ''
        variable = ''
        start = 0
        leader = ''
        lines = record.replace('$$', self._US).split('\n')
        for line in lines:
            if not line:
                continue
            if len(line) < 19:
                return ''
            tag = line[10:13]
            if tag == 'LDR':
                leader = line[23:].replace('^', ' ')
            if not tag.isdigit():
                continue
            field = line[18:].replace('^', ' ') if tag.startswith(
                '00') else line[13:15] + line[18:]
            if self._format == 'cnmarc':
                if tag in ('100', '105', '461', '462', '463'):
                    field = field.replace('^', ' ')
            field += self._RS
            if len(field) > 9999:
                return ''
            directory += tag + str(len(field.encode(encoding))).zfill(4) + str(
                start).zfill(5)
            start += len(field.encode(encoding))
            if start > 99999:
                return ''
            variable += field
        if not leader:
            return ''
        marc = directory + self._RS + variable + self._GS
        if 40 < len(marc) + 24 > 99999:
            return ''
        leader = leader[0:7] + str(len(directory) + 25).zfill(5) + leader[12:]
        leader = str(len(marc.encode(encoding)) + 24).zfill(5) + leader
        return leader + marc
