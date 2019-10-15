import re

filter_loockup = {}
class Filter:
    def __init__(self, data):
        self.data =  data
    
    def check(self, value):
        raise NotImplementedError('check')
    
class LEFilter(Filter):
    symbol = '<='
    def check(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            return False
        return v <= self.data
filter_loockup['<='] = LEFilter

class GEFilter(Filter):
    symbol = '>='
    def check(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            return False
        return v >= self.data
filter_loockup['>='] = GEFilter

class LTFilter(Filter):
    symbol = '<'
    def check(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            return False
        return v < self.data
filter_loockup['<'] = LTFilter

class GTFilter(Filter):
    symbol = '>'
    def check(self, value):
        try:
            v = float(value)
        except (ValueError, TypeError):
            return False
        return v > self.data
filter_loockup['>'] = GTFilter

class EQFilter(Filter):
    symbol = '=='
    def check(self, value):
        if isinstance(self.data, (float,int)):
            try:
                v = float(value)
            except (ValueError, TypeError):
                return v == self.data
            return v == self.data
        else:
            return value == self.data
filter_loockup['=='] = EQFilter


class SMFilter(Filter):
    symbol = '~'
    def __init__(self, data, treshold=80):
        """ 
        Args
        ----
        data: string to compare with 
        treshold: percentil keeper of string match 
        
        """
        self.data =  data
        self.treshold = treshold
    
    def check(self, value):
        return similarity(self.data, value)>=self.treshold
filter_loockup['~'] = SMFilter


class REFilter(Filter):
    symbol = '%'
    
    def __init__(self, re_exp):
        if isinstance(re_exp, re.Pattern):
            self.data = re_exp
        else:
            self.data = re.compile('.*'+re_exp, re.IGNORECASE)
    
    def check(self, value):
        try:
            return self.data.match(value) is not None
        except TypeError:
            return False
    
filter_loockup['%'] = REFilter

# ##############################################################
#
#   Some functions 
#
# ##############################################################


def _longest_common_substring(s1, s2):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def similarity(s1, s2):
     return 2. * len(_longest_common_substring(s1, s2)) / (len(s1) + len(s2)) * 100




