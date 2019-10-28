import os,re,shutil
from kcw import config as conf
from kcw.common.autoload import *
class Exec:
    runtimepath='runtime/app'
    sourcepath=''
    appname="application" #应用名
    name='home' #应用模块名字
    config=conf
    def init(self,config=None):
        if config:
            self.config=config
        path=self.runtimepath+'/'+self.appname+'/'+self.name
        plists=['view'] #模块下要执行的文件夹
        for sourcep in plists:
            if not os.path.exists(path+'/'+sourcep):
                os.makedirs(path+"/"+sourcep)
            if sourcep=='view':
                self.__copyview(sourcep)
            elif sourcep=='config' or sourcep=='common':
                self.__copyweb(sourcep)
    def __copyweb(self,sourcep):
        "处理web模块"
        path1=self.sourcepath+"/"+sourcep
        path2=self.runtimepath+'/'+self.appname+'/'+self.name+"/"+sourcep
        # print(path1,path2)
        if os.path.exists(path1):
            lists=os.listdir(path1)
            for files in lists:
                # print(files)
                if os.path.isfile(path1+"/"+files):
                    f=open(path1+"/"+files,"r",encoding='utf-8')
                    filecon=f.read()
                    f.close()
                    f=open(path2+"/"+files,"w+",encoding='utf-8')
                    f.write(filecon)
                    f.close()
                elif files!='__pycache__':
                    if not os.path.exists(path2+"/"+files):
                        os.makedirs(path2+"/"+files)
                    self.__copyweb(sourcep+"/"+files)
    def __copyview(self,sourcep):
        """处理视图文件"""
        path1=self.sourcepath+"/"+sourcep
        path2=self.runtimepath+'/'+self.appname+'/'+self.name+"/"+sourcep
        lists=os.listdir(path1)
        route=self.config.route
        wjjs=sourcep.split("/")
        qmly=''
        i=0
        while i < len(wjjs):
            if i>0:
                qmly=qmly+"/"+wjjs[i]
            i=i+1
        for files in lists:
            if os.path.isfile(path1+"/"+files):
                if '.py' in files:  #只操作包含 .py 的文件
                    filecon=''
                    f=open(path1+"/"+files,"r",encoding='utf-8')
                    fileind=re.sub('.py','',files)
                    if files == '__init__.py':
                        filecon=""
                        # print(files)
                        while True:
                            line = f.readline()
                            if not line:
                                break
                            if 'Blueprint(' in line:
                                # print(files)
                                line=(self.name+"app = Blueprint(\n"+
                                    "   'application',\n"+
                                    "   __name__,\n"+
                                    "   static_folder='../../../../../"+self.appname+"/"+self.name+"/'+app['static_folder'],#设置静态url目录\n"+
                                    "   template_folder='../../../../../"+self.appname+"/"+self.name+"/'+app['template_folder'],#设置模板文件目录\n"+
                                    ")")
                                filecon=filecon+line+"\n"
                            else:
                                filecon=filecon+line
                    else:
                        ddddddd=''
                        for k in wjjs:
                            ddddddd=ddddddd+"."
                        filecon='from '+ddddddd+' import '+self.name+'app\n'
                        while True:
                            line = f.readline()
                            # if(files=='__init__.py'):
                            #     print(line)
                            if not line:
                                break
                            if 'def ' in line[0:4]:
                                strs=re.sub('def ','',line)
                                fun=strs[0:strs.rfind('(')]
                                fun=re.sub(' ','',fun)
                                ly=''
                                routebs=qmly+"/"+fileind+"/"+fun
                                cs=re.findall(re.compile(r'[(](.*?)[)]', re.S), line)[0]
                                if routebs in route:# and 'route' in route[routebs]:# and route[routebs]['route']:  #添加配置里的路由
                                    if isinstance(route[routebs],dict):
                                        if 'methods' in route[routebs]:
                                            methods=str(route[routebs]['methods'])
                                        else:
                                            methods=str(route['methods'])
                                        ly=ly+'@'+self.name+'app.route("'+route[routebs]['route']+'",methods='+methods+',strict_slashes=False)\n'
                                        if '<' in route[routebs]['route'] and '>' in route[routebs]['route']:
                                            pass
                                        else:
                                            if cs:
                                                cs=cs.split(",")
                                                s=''
                                                # for kkk in cs:
                                                #     kkk=kkk.split("=")
                                                #     s=s+kkk[0]+'/<'+kkk[0]+'>'
                                                for kkk in cs:
                                                    kkk=kkk.split("=")
                                                    if route['defaultparam']==1:
                                                        s=s+'/'+kkk[0]+'/<'+kkk[0]+'>'
                                                    else:
                                                        s=s+'/<'+kkk[0]+'>'
                                                    ly=ly+'@'+self.name+'app.route("'+route[routebs]['route']+""+s+'",methods='+methods+',strict_slashes=False)\n'
                                                    # ly=ly+'@'+self.name+'app.route("'+qmly+"/"+fileind+'/'+fun+s+'",methods='+methods+',strict_slashes=False)\n'
                                    elif isinstance(route[routebs],list):
                                        for v in route[routebs]:
                                            if 'methods' in v:
                                                methods=str(v['methods'])
                                            else:
                                                methods=str(route['methods'])
                                            ly=ly+'@'+self.name+'app.route("'+v['route']+'",methods='+methods+',strict_slashes=False)\n'
                                            # # print("*"*5)
                                            # if '<' in v['route'] and '>' in v['route']:
                                            #     pass
                                            # else:
                                            #     if cs:
                                            #         cs=cs.split(",")
                                            #         s=''
                                            #         for kkk in cs:
                                            #             kkk=kkk.split("=")
                                            #             s=s+kkk[0]+'/<'+kkk[0]+'>'
                                            #             ly=ly+'@'+self.name+'app.route("'+v['route']+s+'",methods='+methods+',strict_slashes=False)\n'
                                elif route['default']:  #添加默认路由
                                    methods=str(route['methods'])
                                    if fun =='index':
                                        ly=ly+'@'+self.name+'app.route("'+qmly+"/"+fileind+'",methods='+methods+',strict_slashes=False)\n'
                                        if fileind == 'index':
                                            if not qmly:
                                                ly=ly+'@'+self.name+'app.route("/",methods=["POST","GET"],strict_slashes=False)\n'
                                            else:
                                                ly=ly+'@'+self.name+'app.route("'+qmly+'",methods=["POST","GET"],strict_slashes=False)\n'
                                    ly=ly+'@'+self.name+'app.route("'+qmly+"/"+fileind+'/'+fun+'",methods='+methods+',strict_slashes=False)\n'
                                    if cs:
                                        cs=cs.split(",")
                                        s=''
                                        for kkk in cs:
                                            kkk=kkk.split("=")
                                            if route['defaultparam']==1:
                                                s=s+'/'+kkk[0]+'/<'+kkk[0]+'>'
                                            else:
                                                s=s+'/<'+kkk[0]+'>'
                                            # print(fun+s)
                                            ly=ly+'@'+self.name+'app.route("'+qmly+"/"+fileind+'/'+fun+s+'",methods='+methods+',strict_slashes=False)\n'
                                line=re.sub('def ','',line)
                                qmlys=re.sub('/','_',qmly)
                                filecon=filecon+ly+'def kcw_'+self.appname+"_"+self.name+qmlys+"_"+fileind+"_"+line
                            else:
                                filecon=filecon+line
                    f.close()
                    f=open(path2+"/"+files,"w+",encoding='utf-8')
                    f.write(filecon)
                    f.close()
            elif files != '__pycache__':
                if not os.path.exists(path2+"/"+files):
                    os.makedirs(path2+"/"+files)
                self.__copyview(sourcep+"/"+files)