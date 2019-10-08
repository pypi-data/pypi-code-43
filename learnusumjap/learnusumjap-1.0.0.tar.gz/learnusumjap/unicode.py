
class BaseUnicodeRanges(object):
    def regex_string(self):
        return '[{}]'.format(''.join(
            '\\u{:04x}-\\u{:04x}'.format(start, end)
            for start, end in self.ranges))

class CJKUnicodeRanges(BaseUnicodeRanges):
    # TODO: add comments for each section source
    ranges = ((0x2e80, 0x2fd5),
              (0x2ff0, 0x2ffb),
              (0x3000, 0x3020),
              (0x3040, 0x309f),
              (0x30a0, 0x30ff),
              (0x31f0, 0x31ff),
              (0x3400, 0x4dbf),
              (0x4e00, 0x9faf),
              (0xff01, 0xff20),
              (0xff3b, 0xff40),
              (0xff5b, 0xff65))

