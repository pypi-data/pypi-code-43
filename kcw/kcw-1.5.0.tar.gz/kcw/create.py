import os,re,traceback,shutil,platform,stat
# import config
from kcw.common.autoload import *
from kcw.config import *
from .exec import Exec
class create:
    name="home"  #应用模块名字
    appname="application"
    runtimepath='runtime/app'  #应用生成目录
    host='0.0.0.0' #绑定ip
    port='39001' #绑定端口
    path=os.path.split(os.path.realpath(__file__))[0] #当前文件目录
    framepath="."#框架目录
    def init(self):
        try:
            if 'Windows' in platform.system():
                PATH=os.environ['PATH']
                PATH=PATH.split(";")[-1]
                try:
                    os.remove(PATH+"/kcw.exe")
                except:pass
                shutil.copy(get_folder()+'/kcw/file/dist/kcw.exe',PATH)
                # print("命令行已添加到",PATH+"/kcw.exe")
            elif 'Linux' in platform.system():
                try:
                    os.remove("/usr/bin/kcw")
                except:pass
                shutil.copy(get_folder()+"/kcw/file/dist/kcw","/usr/bin/")
                os.chmod("/usr/bin/kcw", stat.S_IRWXO)
                # print("命令行已添加到","/usr/bin//kcw")
        except:pass
        if not os.path.exists(self.framepath+"/common"):
            os.makedirs(self.framepath+"/common")
        if not os.path.isfile(self.framepath+"/common/__init__.py"):
            f=open(self.framepath+"/common/__init__.py","a",encoding='utf-8')
            f.write("from kcw.common import *")
            f.close()
        if not os.path.exists(self.framepath+"/config"):
            os.makedirs(self.framepath+"/config")
        if not os.path.isfile(self.framepath+"/config/__init__.py"):
            f=open(self.framepath+"/config/__init__.py","a",encoding='utf-8')
            f.write("from kcw.config import *")
            f.close()
        # if not os.path.isfile(self.framepath+"/config/__init__.py"):
        #     f=open(self.framepath+"/config/__init__.py","a",encoding='utf-8')
        #     f.write("from .conf import *")
        #     f.close()
    def cliapp(self):
        # self.init()
        "创建cli应用"
        framepath=self.framepath+"/"+self.appname+"/"+self.name+"/"
        if os.path.exists(framepath):
            print(framepath,"cli应用和模块已存在，已跳过")
            # exit()
        else:
            shutil.copytree(self.path+"/app/cli",self.appname+'/'+self.name)
            self.__execcommon(self.appname+'/'+self.name+"/common/__init__.py")
            self.__cli_exec_start(self.appname+'/'+self.name+"/start/start.py")
    def __cli_exec_start(self,pathfile):
        "处理cli下start.py文件"
        filecon=''
        f=open(pathfile,"r",encoding='utf-8')
        filecon='# -*- coding: utf-8 -*-\nimport sys\nsys.path.append("../../../")\nfrom '+self.appname+'.'+self.name+'.common import *\n'
        while True:
            line = f.readline()
            if not line:
                break
            filecon=filecon+line
        f.close()
        f=open(pathfile,"w+",encoding='utf-8')
        f.write(filecon)
        f.close()

        
    def webapp(self):
        """创建web应用 """
        # self.init()
        framepath=self.framepath+"/"+self.appname+"/"+self.name+"/"
        if os.path.exists(framepath):
            print(framepath,"web应用和模块已存在，已跳过")
            # exit()
        else:
            shutil.copytree(self.path+"/app/web", "./"+self.appname+'/'+self.name)
            self.__execview(self.appname+'/'+self.name+"/view")
            self.__execcommon(self.appname+'/'+self.name+"/common/__init__.py")
            if not os.path.exists(framepath+"/cli"):
                os.makedirs(framepath+"/cli")
            f=open(framepath+"/cli/server.py","w+",encoding='utf-8')
            f.write('import sys\n'+
            'sys.path.append("../../../")\n'+
            'from '+self.appname+'.'+self.name+'.common import *\n'+
            'if config.app["app_debug"]:\n'+
            '    from kcw.exec import Exec\n'+
            '    e=Exec()\n'+
            '    e.runtimepath="../../../'+self.runtimepath+'"\n'+
            '    e.sourcepath="../"\n'+
            '    e.appname="'+self.appname+'"\n'+
            '    e.name="'+self.name+'"\n'+
            '    e.init(config)\n'+
            '    from '+self.appname+'.'+self.name+'.view import '+self.name+'app\n'+
            'from kcw.packages.flask import Flask\n'+
            'from runtime.app.'+self.appname+'.'+self.name+'.view import '+self.name+'app\n'+
            'kcwapp =Flask(__name__)\n'+
            'kcwapp.register_blueprint('+self.name+'app)\n'+
            'class flaskconfig():\n'+
            '    DEBUG=config.app["app_debug"]\n'+
            '    SECRET_KEY=config.app["SECRET_KEY"]\n'+
            'kcwapp.config.from_object(flaskconfig)\n'+
            '@kcwapp.errorhandler(404)\n'+
            'def err404(err):\n'+
            '    return returnjson([],404,"访问的URL地址错误",404)\n'+
            '@kcwapp.errorhandler(403)\n'+
            'def err403(err):\n'+
            '    return returnjson([],403,"资源不可用",403)\n'+
            '@kcwapp.errorhandler(500)\n'+
            'def err500(err):\n'+
            '    return returnjson([],500,"内部服务器错误，请稍后在试一试",500)\n'+
            '@kcwapp.before_request\n'+
            'def handel_before_request():\n'+
            '    "签权验证"\n'+
            '    if app.oauth(request.path,config):\n'+
            '       try:\n'+
            '           oa=oauth(request.path)\n'+
            '       except NameError:\n'+
            '           print("您已开启签权验证，但您却没有定义签权方法，您应该在'+self.appname+'/'+self.name+'/common/__init__.py文件中定义oauth方法并且接收一个参数")\n'+
            '       else:\n'+
            '           if not oa[0]:\n'+
            '               return oa[1]\n'+
            '@kcwapp.after_request  #请求后执行\n'+
            'def after_request(response):\n'+
            '    return response\n'+
            'if __name__ == "__main__":\n'+
            '    kcwapp.run(host="'+self.host+'",port="'+self.port+'")\n')
            f.close()
        self.__execruntimepath()
    def __execview(self,path):
        "处理视图文件"
        lists=os.listdir(path)
        for files in lists:
            if os.path.isfile(path+"/"+files):
                filecon=''
                f=open(path+"/"+files,"r",encoding='utf-8')
                if files=='__init__.py':
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if 'Blueprint(' in line and '=' in line:
                            line="from "+self.appname+"."+self.name+".config import app\n"+self.name+line
                        filecon=filecon+line
                else:
                    filecon='from '+self.appname+'.'+self.name+'.common import *\n'
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        filecon=filecon+line
                f.close()
                f=open(path+"/"+files,"w+",encoding='utf-8')
                f.write(filecon)
                f.close()
            elif files != '__pycache__':
                if not os.path.exists(path+"/"+files):
                    os.makedirs(path+"/"+files)
                else:
                    self.__execview(path+"/"+files)
    def __execcommon(self,pathfile):
        f=open(pathfile,"r",encoding='utf-8')
        filecon='from common import *\n'+'from '+self.appname+'.'+self.name+' import config\n'
        while True:
            line = f.readline()
            if not line:
                break
            filecon=filecon+line
        f.close()
        f=open(pathfile,"w+",encoding='utf-8')
        f.write(filecon)
        f.close()
    def __execruntimepath(self):
        e=Exec()
        e.runtimepath=self.framepath+"/"+self.runtimepath
        e.sourcepath=self.framepath+"/"+self.appname+"/"+self.name
        e.appname=self.appname
        e.name=self.name
        e.init()
        