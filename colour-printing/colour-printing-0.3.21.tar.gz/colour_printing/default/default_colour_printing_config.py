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

get_time = lambda: datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f")[:-3]
fill = 7

TEMPLATE = "{time} {flag} {message}"
CP = CPConfig(TEMPLATE)


@CP.wrap
def info(cp):
    cp.time = Term(Fore.CYAN)
    cp.flag = Term(Fore.BLUE, Mode.INVERT, default="INFO".center(fill, "-"))
    cp.message = Term(Fore.BLUE)


@CP.wrap
def error(cp):
    cp.time = Term(Fore.CYAN)
    cp.flag = Term(Fore.RED, Mode.INVERT, default="ERROR".center(fill, "-"))
    cp.message = Term(Fore.RED)


@CP.wrap
def success(cp):
    cp.time = Term(Fore.CYAN)
    cp.flag = Term(Fore.GREEN, Mode.INVERT, default="SUCCESS".center(fill, "-"))
    cp.message = Term(Fore.GREEN)


@CP.wrap
def debug(cp):
    cp.time = Term(Fore.CYAN)
    cp.flag = Term(Fore.PURPLE, Mode.INVERT, default="DEBUG".center(fill, "-"))
    cp.message = Term(Fore.PURPLE)


@CP.wrap
def warning(cp):
    cp.time = Term(Fore.CYAN)
    cp.flag = Term(Fore.YELLOW, Mode.INVERT, default="WARNING".center(fill, "-"))
    cp.message = Term(Fore.YELLOW)


CP.set_all_default(time=get_time)
