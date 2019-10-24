# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 09:51:45 2018

@author: kunlin.l
"""

# noinspection PyUnresolvedReferences
from atrader.tframe import sysclsbase as cnt
# noinspection PyUnresolvedReferences
from atrader.tframe.sysclsbase import smm
# noinspection PyUnresolvedReferences
from atrader.tframe.sysclsbase import gv
# noinspection PyUnresolvedReferences
from atrader.tframe.language import text
# noinspection PyUnresolvedReferences
from atrader.tframe.utils.argchecker import apply_rule, verify_that
from atrader.tframe import ufuncs

__all__ = [
    'clear_cache'
]


@smm.force_phase(gv.RUMMODE_PHASE_DEFAULT)
def clear_cache():
    import os
    import shutil
    from .comm import atcmd
    atcmd.atSendCmdTest('', [])
    ufuncs.enter_function_log(text.LOG_CLEAN_CACHE, console=text.LOG_CLEAN_CACHE)
    root_dir = cnt.env.fm.root_sub_dir()
    for d in os.listdir(root_dir):
        try:
            if d.startswith('record_'):
                shutil.rmtree(os.path.join(root_dir, d))
        except OSError:
            pass

    # cnt.env.fm.cls_root_sub_dir('log')
    cnt.env.fm.cls_root_sub_dir('mat')
    ufuncs.quit_function_log(text.LOG_CLEAN_CACHE_END, console=text.LOG_CLEAN_CACHE_END)
