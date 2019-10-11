import os
import sys
import shutil
import zipfile
import platform

if platform.architecture()[0].startswith('32'):
    _ver = '64'
elif platform.architecture()[0].startswith('64'):
    _ver = '32'

curr = os.path.dirname(__file__)
targ = os.path.join(os.path.dirname(sys.executable), 'Scripts')

def init_upx():
    print('init upx tool.')
    upx = os.path.join(curr, 'upx-3.95-{}.zip'.format(_ver))
    zf = zipfile.ZipFile(upx)
    zf.extractall(path = targ)
    print('upx file in {}.'.format(upx))
    print()

def init_tcc():
    print('init tcc tool.')
    tcc = os.path.join(curr, 'tcc-0.9.27-win{}-bin.zip'.format(_ver))
    zf = zipfile.ZipFile(tcc)
    zf.extractall(path = targ)
    winapi = os.path.join(curr, 'winapi-full-for-0.9.27.zip')
    zf = zipfile.ZipFile(winapi)
    zf.extractall(path = targ)
    fd = 'winapi-full-for-0.9.27'
    finclude = os.path.join(curr, fd, 'include')
    tinclude = os.path.join(targ, 'tcc\\include')
    for x, _, z in os.walk(finclude):
        v = tinclude + x.split(fd)[1].split('include')[1]
        for i in z:
            if not os.path.isfile(os.path.join(v, i)):
                shutil.copy(os.path.join(x, i), v)
    shutil.rmtree(os.path.join(targ, fd))
    tccenv = targ + '\\tcc'
    print('tcc forlder in {}.'.format(tccenv))
    def add_env():
        import winreg as wg
        key_test = wg.OpenKey(wg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",0,wg.KEY_ALL_ACCESS)
        path_str = wg.QueryValueEx(key_test,'path')
        if tccenv not in path_str[0]:
            path_str_new = path_str[0] + ';' + tccenv
            wg.SetValueEx(key_test,'path','',path_str[1],path_str_new)
            wg.FlushKey(key_test)
            wg.CloseKey(key_test)
            os.popen(r'setx Path /K "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment\Path" /M').read() # 使注册表修改立即生效
            print('add forlder {} in env.'.format(tccenv))
    add_env()
    print()

def init_all():
    init_upx()
    init_tcc()

if __name__ == '__main__':
    init_all()