from conlog import Conlog
from functools import lru_cache 
from .TimeTools import Timetools
from itertools import repeat

def test_fngrp():
    conlog = Conlog(__name__, Conlog.DEBUG, enabled=True)

    timetools = conlog.fngrp(Timetools, Conlog.DEBUG, enabled=True)
    timetools.wait(5)
    linebreak= ''.join(repeat(  '-'  ,60)) + '\n'
    print( linebreak )
    timetools.retry(9)
    print(linebreak)  
    # Say you want to trace a Conlog implemented object
    # Just add this line 
    conlog.trace(timetools.sleep)
    timetools.sleep(4, 5 )
    print(linebreak)
 