"""
#                     *Colour-printing Reference*
#########################################################################################
#   @'fore': # 前景色         @'back':# 背景              @'mode':# 显示模式               # 
#            'black': 黑色            'black':  黑色              'normal': 终端默认设置   # 
#            'red': 红色              'red':  红色                'bold':  高亮显示        # 
#            'green': 绿色            'green': 绿色               'underline':  使用下划线 #
#            'yellow': 黄色           'yellow': 黄色              'blink': 闪烁           # 
#            'blue':  蓝色            'blue':  蓝色               'invert': 反白显示       #    
#            'purple':  紫红色        'purple':  紫红色            'hide': 不可见          #    
#            'cyan':  青蓝色          'cyan':  青蓝色                                     #
#            'white':  白色           'white':  白色                                     #
#########################################################################################
"""


from colour_printing.config import CPConfig, Term

from datetime import datetime

from colour_printing import Mode, Fore, Back

get_time = lambda: datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f')[:-3]

TEMPLATE = "{message}{good}"
CP = CPConfig(TEMPLATE)  # 我才是主角,从其他地方导入我

#        +------------------------->  doesn't matter,不用实例化
#        |
#        V

class Paper(object):

    @CP.wrap
    def info(self):
        self.message = Term()
        self.good = Term()

    @CP.wrap
    def success(self):
        self.message = Term()
        self.good = Term()

    @CP.wrap
    def warning(self):
        self.message = Term()
        self.good = Term()

    @CP.wrap
    def error(self):
        self.message = Term()
        self.good = Term()

    @CP.wrap
    def debug(self):
        self.message = Term()
        self.good = Term()