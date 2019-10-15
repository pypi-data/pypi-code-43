from datetime import datetime


class ConsoleColorMixin:
    text_colorful_fmt = {
        'black': '\033[30m{text}\033[0m',
        'red': '\033[31m{text}\033[0m',
        'green': '\033[32m{text}\033[0m',
        'yellow': '\033[33m{text}\033[0m',
        'blue': '\033[34m{text}\033[0m',
        'purple': '\033[35m{text}\033[0m',
        'black_green': '\033[36m{text}\033[0m',
        'white': '\033[37m{text}\033[0m',
        'h_black': '\033[90m{text}\033[0m',
        'h_red': '\033[91m{text}\033[0m',
        'h_green': '\033[92m{text}\033[0m',
        'h_yellow': '\033[93m{text}\033[0m',
        'h_blue': '\033[94m{text}\033[0m',
        'h_purple': '\033[95m{text}\033[0m',
        'h_black_green': '\033[96m{text}\033[0m',
        'h_white': '\033[97m{text}\033[0m',
    }
    bg_colorful_fmt = {
        'black': '\033[40m{text}\033[0m',
        'red': '\033[41m{text}\033[0m',
        'green': '\033[42m{text}\033[0m',
        'yellow': '\033[43m{text}\033[0m',
        'blue': '\033[44m{text}\033[0m',
        'purple': '\033[45m{text}\033[0m',
        'black_green': '\033[46m{text}\033[0m',
        'white': '\033[47m{text}\033[0m',
        'h_black': '\033[100m{text}\033[0m',
        'h_red': '\033[101m{text}\033[0m',
        'h_green': '\033[102m{text}\033[0m',
        'h_yellow': '\033[103m{text}\033[0m',
        'h_blue': '\033[104m{text}\033[0m',
        'h_purple': '\033[105m{text}\033[0m',
        'h_black_green': '\033[106m{text}\033[0m',
        'h_white': '\033[107m{text}\033[0m',
    }

    def text_colorful(self, text, color):
        return self.text_colorful_fmt.get(color, '{text}').format(
            text=text) if text else ''

    def bg_colorful(self, text, color):
        return self.bg_colorful_fmt.get(color, '{text}').format(
            text=text) if text else ''

    def __getattr__(self, item):
        if item.startswith('text_'):
            return lambda text: self.text_colorful(text, item[5:])
        elif item.startswith('bg_'):
            return lambda text: self.bg_colorful(text, item[3:])
        else:
            raise AttributeError(
                "'ProcessBar' object has no attribute '%s'" % item)


class ProcessBar(ConsoleColorMixin):
    fmt = '\r{complete}{incomplete} {percent} ({cur}/{total})'
    fmt2 = 'Begin: {begin} Estimated: {estimated} Elapsed: {elapsed}'

    def __init__(self, total, cur=0, msg=''):
        self.begin_time = None
        self.total = total
        self.cur = cur
        self.msg = msg
        self.bar_length = 100

    def print(self, cur):
        if self.begin_time is None:
            self.begin()
        du = datetime.now() - self.begin_time
        percent = cur / self.total
        string = self.fmt2.format(**{
            'begin': self.begin_time,
            'elapsed': du,
            'estimated': self.begin_time + (du / percent) if cur else '--',
        }) + ' ' * self.bar_length
        complete = string[0:int(percent * self.bar_length)]
        incomplete = string[int(percent * self.bar_length):self.bar_length]
        print(self.fmt.format(**{
            'complete': self.text_h_white(self.bg_h_blue(complete)),
            'incomplete': self.text_h_white(self.bg_white(incomplete)),
            'percent': self.text_h_purple('{:.2%}'.format(percent)),
            'cur': self.text_h_black_green(cur),
            'total': self.text_h_red(self.total),
        }), end='')

    def begin(self):
        self.begin_time = datetime.now()
        if self.msg:
            print(self.text_h_yellow('>>> %s <<<' % self.msg))
        self.print(self.cur)

    def end(self):
        self.print(self.total)
        print()
