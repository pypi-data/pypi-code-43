#submodules
from easilyb.net import requestqueue
#imports
from subprocess import Popen as popen
from random import choice as _rchoice
from time import time as _time
from logging import getLogger
logger = getLogger(__name__)

_ANDROID_VERSIONS = ['3.2', '3.2.1', '3.2.2', '3.2.3', '3.2.4', '3.2.5', '3.2.6', '4.0', '4.0.1', '4.0.2', '4.0.3', '4.0.4', '4.1', '4.1.1', '4.1.2', '4.2', '4.2.1', '4.2.2', '4.3', '4.3.1', '4.4', '4.4.1', '4.4.2', '4.4.3', '4.4.4', '5.0', '5.0.1', '5.0.2', '5.1', '5.1.1', '6.0', '6.0.1']
_FIREFOX_VERSIONS = None
_FIREFOX_M0 = 560.0
_FIREFOX_ANDROID_AGENT = 'Mozilla/5.0 (Android %s; Mobile; rv:%s) Gecko/%s Firefox/%s'

def wget(url, filepath=None, referer=None, useragent=None, basedir=None, echo=False):
    if useragent is None:
        useragent = get_useragent()
    cmd = ['wget', url ]
    if filepath:
        cmd += ['-O', filepath]
    elif basedir:
        cmd += ['-P', basedir]
    cmd += ['-U', useragent]
    if referer:
        cmd += ['--referer', referer]
    if echo:
        cmd = ['echo'] + cmd
    logger.debug("wget command: %s", cmd)
    try:
        return popen(cmd).wait()
    except:
        logger.warning('error running wget.', exc_info=True)
        return 999
def _generate_firefox_versions():
    global _FIREFOX_VERSIONS
    t1 = _time()
    m1 = t1/3600/24/30
    _max = int(44 +(m1 - _FIREFOX_M0)*2.0/3.0)
    _min = max(_max-16, 10)
    _FIREFOX_VERSIONS = [str(i)+'.0' for i in range(_min, _max)]

def get_useragent():
    if _FIREFOX_VERSIONS is None:
        _generate_firefox_versions()
    fv = _rchoice(_FIREFOX_VERSIONS)
    av = _rchoice(_ANDROID_VERSIONS)
    return _FIREFOX_ANDROID_AGENT%(av, fv, fv, fv)