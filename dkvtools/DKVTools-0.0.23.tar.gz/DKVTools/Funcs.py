# -*- coding: UTF-8 -*-
# 创建时间：2018年3月9日21:29:09
# 创建人：  Dekiven_PC


import os
import sys
import platform
import zipfile
import shutil
# import subprocess
# import tempfile
'''
    常用工具函数
'''

def pathJoin(_dir, fn, abs=False) :
    return formatPath(os.path.join(_dir, fn), abs)

def isPython3():
    '''判断python版本是否是3.x'''
    return sys.version_info >= (3,0)

def isFunc(func):
    '''判断对象是否是函数'''
    return hasattr(func,'__call__')
    # return callable(func)

def getPlatform():
    '''获取python运行平台'''
    return platform.system()

def isWindows():
    '''判断是否是win32平台'''
    return getPlatform().lower() == 'windows'

def isLinux():
    '''判断是否是linux平台'''
    return getPlatform().lower() == 'linux'

def isMac():
    '''判断是否是Mac OS平台'''
    return getPlatform().lower() == 'darwin'

def getUserPath():
    return formatPath(os.path.expanduser('~'))

def getUserName():
    return os.path.split(getUserPath())[-1]

def getDeviceName() :
    import socket
    return socket.getfqdn(socket.gethostname())

def getLocalHost() :
    '''获取设备ip
    '''
    import socket
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def getDesktopPath():
    '''获取桌面的路径，只支持win32、mac'''
    # if isWindows():
    #     if isPython3():
    #         import winreg           # 内置模块，获取windows注册表
    #     else:
    #         import _winreg as winreg
    #     key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    #     return winreg.QueryValueEx(key, "Desktop")[0]
    if isWindows() or isMac():
        return '%s/Desktop'%(getUserPath())
    else:
        # TODO: Linux
        return ''

def addTempPathForOs(path):
    '''添加path到系统的PATH环境变量中，暂时只支持win32'''
    if isWindows():
        os.environ['PATH']+= ';' +path

def addTempPathForPy(path):
    '''添加path到python运行环境的PATH环境变量中'''
    sys.path.append(path)

def getMainCwd():
    '''获取入口脚本的文件夹路径'''
    return os.path.split(sys.argv[0])[0]

def bytes2utf8Str(s, encodingOri='GBK') :
    if (isPython3() and not isinstance(s, str)) or (not isPython3() and not isinstance(s, unicode)) :
        try :
            s = s.decode(encodingOri)
        except Exception as e :
            s = s.decode('utf-8')
    return s.encode('utf-8').decode('utf-8')


def zipFolder(folder, zipPath = None, suffixs = '.*', skipFiles = (), inZipPath=''):
    '''压缩文件夹
    folder:待压缩的文件夹
    zipPath:压缩文件存储路径，默认为文件绝对夹路径加上后缀'.zip'
    suffixs:参与压缩的文件格式后缀，默认为'.*'，表示所有文件都参与压缩，多个后缀用英文逗号（','）隔开，如：'.zip,.txt'
    skipFiles:跳过压缩的文件列表（list或tuple）,在文件夹中的绝对路径
    inZipPath:将所有文件统一放到inZipPath文件夹下
    '''
    if not isinstance(folder, str) :
        print('error:\tfolder [%s] is not a string!'%(str(folder)))
        return
    if not os.path.isabs(folder) :
        folder = os.path.join(pyDir, folder)
    folderLen = len(folder)
    fileInfos = []
    suffixs = (suffixs == '.*') and suffixs or str(suffixs).lower().split(',')

    # list解析操作
    skip = [l.replace('\\', '/').strip() for l in skipFiles]
    if os.path.exists(folder) and os.path.isdir(folder) :
        for _dir, folders, files in os.walk(folder) :
            for f in files :
                suffix = os.path.splitext(f)
                suffix = str(suffix[-1]).lower()
                p = os.path.join(_dir, f)
                # 获取zip文件夹内的路径，去掉前面的/
                absP = p[folderLen+1:].replace('\\', '/').strip()
                if len(inZipPath) > 0 :
                    absP = pathJoin(inZipPath, absP)
                if (suffixs == '.*' or suffix in suffixs) and (not absP in skip):
                    fileInfos.append((p, absP))
                    skip.append(absP)
        if len(fileInfos) > 0 :
            if zipPath is None :
                zipPath = folder + '.zip'
            dirName = os.path.dirname(zipPath)
            if not os.path.exists(dirName) :
                os.makedirs(dirName)
            zipF = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
            # print(password)
            # zipF.setpassword(password)
            for f, af in fileInfos :
                zipF.write(f, af)
            zipF.close()
            print('zip [%s] finished! Total files: %d'%(zipPath, len(fileInfos)))
            return fileInfos
        else :
            print('no files need to zip!')

    else :
        print('error:\tfolder [%s] do not exists!'%(folder))

def tryMakeParentDir(path) :
    d = os.path.dirname(path)
    if not os.path.isdir(d) :
        os.makedirs(d)

def tryMakeDir(path) :
    if not os.path.isdir(path) :
        if not os.path.isfile(path) :
            os.makedirs(path)
        else :
            raise Exception('path "%s" has a file'%path)

def copyTree(srcDir, targetDir, removeBefore=False, suffix='.*', skipDirs=()) :
    '''Copy the srcDir to targetDir.
    参数: srcDir, targetDir, removeBeforee=False, suffix='.*', skipDirs=()
    skipDirs 使用相对于srcDir的路径
    '''

    try :
        import win32api
        import win32con
    except Exception as e :
        win32api = None

    if not os.path.exists(srcDir):
        print('dir ["%s"] do not exists!'%(srcDir))
        return False
    srcDir = formatPath(srcDir)
    targetDir = formatPath(targetDir)
    if removeBefore and os.path.isdir(targetDir):
        shutil.rmtree(targetDir)

    # 如果是文件，拷贝
    if os.path.isfile(srcDir) :
        # print('copyTree 1 ')
        suf = os.path.splitext(srcDir)[1]
        if not targetDir[-len(suf):] == suf :
            # 目标位置是路径
            targetDir = pathJoin(targetDir, os.path.split(srcDir)[-1])
            print('copyTree 2 '+targetDir)
        # print('copyTree 3 ')
        dirname = os.path.dirname(targetDir)
        if not os.path.isdir(dirname) :
            os.makedirs(dirname)
        shutil.copyfile(srcDir, targetDir)
        return True

    # print('copy ["%s"] to ["%s"] ...'%(srcDir, targetDir))
    for curDir, folders, files in os.walk(srcDir) :
        if suffix != '.*' and isinstance(suffix, str):
            suffix = [f.strip().lower() for f in suffix.split(',')]

        # 跳过skipDirs定义的文件夹
        # print('relative dir:'+getRelativePath(curDir, srcDir)[0])
        relativeDir = getRelativePath(curDir, srcDir)[0].strip()
        for sd in skipDirs :
            if formatPath(relativeDir).find(sd) == 0:
                relativeDir = None
                break
        if relativeDir == None :
            continue

        for f in files :
            if suffix == '.*' or str(os.path.splitext(f)[-1]).strip().lower() in suffix:
                p = pathJoin(curDir, f) 
                tp = pathJoin(targetDir, p.replace(srcDir, '')[1:])
                td = os.path.split(tp)[0]
                if not os.path.exists(td) :
                    # print('make '+td)
                    os.makedirs(td)
                if isWindows() and os.path.exists(tp) and win32api is not None :
                    # win32上只能通过下面的方式修改文件显隐性，隐藏文件覆盖会引发权限问题
                    win32api.SetFileAttributes(tp, win32con.FILE_ATTRIBUTE_NORMAL)
                shutil.copyfile(p, tp)
    # print('copy ["%s"] to ["%s"] \tsucceeded!'%(srcDir, targetDir))
    return True

def removeTree(path) :
    if os.path.isdir(path):
        # shutil.rmtree(path)
        if isWindows() :
            tryCmd('rd /s /q "%s"'%(path.replace('/', '\\')))
        else :
            tryCmd('rm -rf "%s"'%(path))

def openFile(path, mode, encoding='utf-8') :
    '''以指定格式打开文件，返回文件'''
    import codecs
    return codecs.open(path, mode, encoding=encoding) 
    
def startFile(path) :
    '''图形系统打开文件或文件夹，目前仅测支持win32和mac
    return ： 如果成功打开文件返回True， 否则返回False
    '''
    if os.path.exists(path) :
        if isWindows() :
            os.startfile(path)
            return True
        elif isMac():
            # path = path.replace(' ', '" "')
            os.system('open "%s"'%(path,))
            return True
    return False

def getCounter(start = 1) :
    '''Get a counter, start is the value returned when first call the counter ,start is 0 if did not set
    '''
    c = [start-1]

    def count() :
        c[0] += 1
        return c[0]

    return count

def formatPath(path, abs=False) :
    path = str(path)
    if abs :
        path = os.path.abspath(path)
    return path.replace('\\', '/')

def getRelativePath(oriPath, relative2) :
    '''return path, success
    path:       the path that oriPath relative to relative2 ,if oriPath do not satrt with relative2,return oriPath
    success:    if oriPath satrt with relative2
    '''
    oriPath = formatPath(oriPath)
    relative2 = formatPath(relative2)
    if oriPath.find(relative2) == 0 :
        return oriPath.replace(relative2, '').strip('/'), True
    else :
        return oriPath, False
        
def modifyFile(path, oldStrs, newStrs) :
    '''modifyFile(path, oldStrs, newStrs)   通过replace修改文件内容，不会有多余的换行符生成
    oldStrs 文件中需要替换的字符串tuple或者list
    newStrs 文件中替换为的字符串tuple或者list，与oldStrs一一对应
    '''
    if os.path.isfile(path) :
        f = open(path, 'rb')
        content = bytes2utf8Str(f.read())
        content = content.replace('\r\n', '\n')
        f.close()
        if newStrs and oldStrs and len(newStrs) == len(oldStrs) :
            for i in range(len(newStrs)) :
                content = content.replace(oldStrs[i], newStrs[i])
        f = None
        if isPython3() :
            f = open(path, 'w', encoding='utf-8')
        else :
            f = open(path, 'w')
        f.write(content)
        f.close()

def tryCmd(cmd) :
    import subprocess
    import traceback
    import tempfile
    out_temp = None
    lines = None
    try:
        out_temp = tempfile.SpooledTemporaryFile()
        fileno = out_temp.fileno()
        obj = subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_temp.seek(0)
        lines = out_temp.readlines()    
        # print (lines)
    except Exception as e:
        print (traceback.format_exc())
        # raise e
        # pass
    finally:
        if out_temp:
            out_temp.close()
        return lines

def getPythonObjByStr(pythonStr) :
    '''将传入的字符串转化为python对象（函数、值等），
    返回值是一个作用域，可使用 getPythonObjByStr('xxxxx')['yy']访问'''
    scope = {}
    exec_code = compile(funcStr, '<string>', 'exec')
    exec(exec_code, scope)
    return scope

def getFuncByStr(funcStr, funcName) :
    '''根据传入的字符串和方法名获取定义的函数'''
    scope = {}
    exec_code = compile(funcStr, '<string>', 'exec')
    exec(exec_code, scope)
    return scope[funcName]

def jsonLoads(jsonStr, **params) :
    '''py2 py3 json.loads'''
    import json
    return json.loads(jsonStr, **params)

def jsonDumps(data, **params) :
    '''py2 py3 json.dumps
    可用参数及默认值：
        skipkeys=False, 
        ensure_ascii=True, 
        check_circular=True, 
        allow_nan=True, 
        cls=None, 
        indent=None, 
        separators=None, 
        encoding="utf-8", 
        default=None, 
        sort_keys=False
    '''
    import json
    if isPython3() and 'encoding' in list(params.keys()) :
        del params['encoding']
    return json.dumps(data, **params)


def CamelCase2UnderLine(s):
    '''驼峰法命名转下划线命名'''
    newStr = ''
    for i in range(len(s)):
        c = s[i]
        v = ord(c)
        if v > 64 and v < 91 :
            if i > 0 and i < len(s) - 1 :
                preV = ord(s[i-1])
                if preV > 96 and preV < 123 :
                    newStr = newStr + '_'
                else :
                    nextV = ord(s[i+1])
                    if nextV > 96 and nextV < 123 and preV != 95:
                        newStr = newStr + '_'
            newStr = newStr + chr(v+32)
        else :
            newStr = newStr + c
    print(newStr)
    return newStr

def isStr(s) :
    if isPython3() :
        return isinstance(s, str)
    else :
        return isinstance(s, str) or isinstance(s, unicode)

def equals(a, b) :
    if isPython3() :
        import operator
        return operator.eq(a, b)
    else :
        return cmp(a, b) == 0

def tryGetDictValue(dic, key, default=None, delete=False) :
    '''从dict中获取key对应的value,
default: 若不存在key则返回传入的默认值,默认 None
delete:  是否在获取到值后删除对应键值对,默认 False
    '''
    if isinstance(dic, dict) :
        if delete :
            return dic.pop(key, default)
        else :
            return dic.get(key) or default
    else :
        return default


# ===========================================================================================================

def Singleton(cls, *args, **kwds):
    '''单例修饰符函数，参考见：
    python 单例：http://ghostfromheaven.iteye.com/blog/1562618
    python @修饰符：http://blog.csdn.net/lainegates/article/details/8166764
    '''
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwds)
        return instances[cls]
    return _singleton

# ===========================================================================================================


# ==================================================测试========================================================
def __main() :
    # startFile(os.path.dirname(__file__))
    # startFile(getDesktopPath())
    print(getLocalHost())

if __name__ == '__main__':
    __main()