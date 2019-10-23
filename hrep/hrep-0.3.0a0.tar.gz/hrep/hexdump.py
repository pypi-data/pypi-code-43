HEXDIGITS = "0123456789abcdef"

MARK_ON = u'\ufff9'
SEPERATOR = u'\ufffa'
MARK_OFF = u'\ufffb'
UNPRINTABLE = u'\ufffd'
UNPRINTABLE_MARKED = u'\ufffc'

class HexDumper(object):
    line_fmt = SEPERATOR.join((u"{addr}", u"{dump}" , u"{ascii}" , u""))

    def __init__(self, width, align, before, after):
        self.width = width
        self.align = align
        self.before = before
        self.after = after
        self.btrans = bytearray(x if 32 <= x < 127 else 0xff for x in range(256))

    def dump(self, data, offset, start, end):
        lines = []
        width = self.width

        # take only relevant data
        dstart = ((start - self.before) // self.align) * self.align
        dend = ((end + self.after + self.align - 1) // self.align) * self.align
        dstart = max(0, dstart)

        for i in range(dstart, dend, width):
            bs = [u'{:02x}'.format(x) for x in bytearray(data[i:i + width])]
            ss = (data[i:i+width]).translate(self.btrans).decode('ascii', 'replace')
            # padding
            bs += [u'  '] * (width - len(bs))
            ss = ss.ljust(width)

            addr_mark = addr_end = start_mark = end_mark = ''

            if start - width < i < end:
                # mark appears on this line
                addr_mark, addr_end = MARK_ON, MARK_OFF

                mark_start, mark_end = start - i, end - i
                
                ss = (ss[:max(mark_start, 0)] 
                    + MARK_ON
                    + ss[max(mark_start, 0):mark_end].replace(UNPRINTABLE, UNPRINTABLE_MARKED)
                    + MARK_OFF
                    + ss[mark_end:])

                if mark_end <= width:
                    # mark ends after this byte
                    bs[mark_end-1] = bs[mark_end-1] + MARK_OFF
                else:
                    # mark continues to next line
                    end_mark = MARK_OFF

                if mark_start >= 0:
                    # mark starts at this byte
                    bs[mark_start] = MARK_ON + bs[mark_start]
                else:
                    # mark started in previous line
                    start_mark = MARK_ON
                # need to override unprintable character color

            # group by pairs, then groups of 4 pairs
            dump = [u''.join(bs[j:j+2]) for j in range(0, len(bs), 2)]
            dump = [u' '.join(dump[j:j+4]) for j in range(0, len(dump), 4)]
            dump = u'  '.join(dump)


            addr = u"{}{:#x}{}".format(addr_mark, offset + i, addr_end).rjust(10 + len(addr_mark + addr_end))
            dump = u"{} {} {}".format(start_mark, dump, end_mark)
            lines.append(self.line_fmt.format(addr=addr, dump=dump, ascii=ss))
        return u'\n'.join(lines)
