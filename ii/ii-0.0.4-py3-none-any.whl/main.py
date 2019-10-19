import os
import sys
import shutil
import zipfile
import platform

if platform.architecture()[0].startswith('32'):
    _ver = '32'
elif platform.architecture()[0].startswith('64'):
    _ver = '64'

curr = os.path.dirname(__file__)
targ = os.path.join(os.path.dirname(sys.executable), 'Scripts')

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) > 1:
                shutil.copy2(s, d)

def install_upx():
    _upx = 'upx-3.95-{}.zip'.format(_ver)
    print('init upx tool: {}'.format(_upx))
    upx = os.path.join(curr, _upx)
    zf = zipfile.ZipFile(upx)
    zf.extractall(path = targ)
    print('upx file in {}'.format(targ))
    print()

def install_tcc():
    _tcc = 'tcc-0.9.27-win{}-bin.zip'.format(_ver)
    print('init tcc tool: {}'.format(_tcc))
    tcc = os.path.join(curr, _tcc)
    zf = zipfile.ZipFile(tcc)
    zf.extractall(path = targ)
    winapi = os.path.join(curr, 'winapi-full-for-0.9.27.zip')
    zf = zipfile.ZipFile(winapi)
    zf.extractall(path = targ)
    fd = 'winapi-full-for-0.9.27'
    finclude = os.path.join(targ, fd, 'include')
    tinclude = os.path.join(targ, 'tcc', 'include')
    copytree(finclude, tinclude)
    shutil.rmtree(os.path.join(targ, fd))
    tccenv = os.path.join(targ, 'tcc')
    copytree(tccenv, targ)
    print('tcc in {}'.format(targ))
    shutil.rmtree(tccenv)
    print()

def install_nasm():
    _nasm = 'nasm-2.14.02-win{}.zip'.format(_ver)
    print('init nasm tool: {}'.format(_nasm))
    nasm = os.path.join(curr, _nasm)
    zf = zipfile.ZipFile(nasm)
    zf.extractall(path = targ)
    tccenv = targ + '\\nasm-2.14.02'
    copytree(tccenv, targ)
    print('nasm in {}'.format(targ))
    shutil.rmtree(tccenv)
    print()

def install_ollydbg():
    _ollydbg = 'ollydbg.zip'
    _targ = os.path.dirname(sys.executable)
    print('init ollydbg tool: {}'.format(_ollydbg))
    ollydbg = os.path.join(curr, _ollydbg)
    zf = zipfile.ZipFile(ollydbg)
    zf.extractall(path = _targ)
    print('ollydbg file in {}'.format(_targ))
    print('ollydbg ollydbg can only parse win32 execfile now.')
    print()

def install(install_pkg='all'):
    if install_pkg == 'upx':
        install_upx()
    elif install_pkg == 'tcc':
        install_tcc()
    elif install_pkg == 'nasm':
        install_nasm()
    elif install_pkg == 'ollydbg':
        install_ollydbg()
    elif install_pkg == 'all':
        install_upx()
        install_tcc()
        install_nasm()
        install_ollydbg()
    else:
        print('unknown pkg:{}'.format(install_pkg))

def execute():
    if not platform.platform().lower().startswith('windows'):
        print('only work in windows platform.')
        exit(0)
    argv = sys.argv
    if len(argv) > 1:
        if argv[1] == 'install':
            if len(argv) > 2:
                install(argv[2])
            else:
                install(install_pkg='all')
    else:
        print('pls use "ii install" to install all upx,tcc,nasm,ollydbg.')

if __name__ == '__main__':
    install(install_pkg='ollydbg')
    pass