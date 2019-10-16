#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,sys,re
import platform
from xyscript.common.xylog import faillog,successlog,warninglog


class SysEvn():
    def get_system_environment(self,name):
        if len(name) >0:
            home = os.environ['HOME'] + "/.bash_profile"
            if not os.path.exists(home):
                return None
            Ropen=open(home,'r')
            for line in Ropen:
                if name + "=" in line:
                    result = re.findall(r'export ' + name + '=\'(.+?)\'',line, re.M|re.I)
                    if len(result) == 1 and '#' not in line:
                        Ropen.close() 
                        return result[0]
                    
            Ropen.close()
            return None
        else:
            faillog("变量名不能为空")
            return None

    def set_system_environment(self,name,value):
        env = self.get_system_environment(name)
        print(env)
        platform = System().get_platform()
        if env != None and env != value:
            warninglog("当前值为：" + env)
            if  platform in ["Windows/Cygwin","Windows"]:
                self.remove_win_env(name,value)
                self.modification_win_env(name,value)
            elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
                self.remove_linux_and_macos_env(name,value)
                self.modification_linux_and_macos_env(name,value)
            else:
                faillog("删除环境变量失败，当前平台暂时不支持此功能！")
        elif env != None and  env == value:
            pass
        else:
            if  platform in ["Windows/Cygwin","Windows"]:
                self.modification_win_env(name,value)
            elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
                self.modification_linux_and_macos_env(name,value)
            else:
                faillog("修改环境变量失败，当前平台暂时不支持此功能！")

    def remove_system_environment(self,name,value):
        env = self.get_system_environment(name)
        if env == None:
            return
        platform = System().get_platform()
        if  platform in ["Windows/Cygwin","Windows"]:
            self.modification_win_env(name,value)
        elif platform in ["Mac OS X","OS/2","OS/2 EMX","Linux"]:
            self.modification_linux_and_macos_env(name,value)
        else:
            faillog("修改环境变量失败，当前平台暂时不支持此功能！")

    def modification_win_env(self,name,value):
        print("win下修改环境变量")

    def remove_win_env(self,name,value):
        print("win下修改环境变量")

    def modification_linux_and_macos_env(self,name,value):
        try:
            file_data = ""
            home = os.environ['HOME'] + "/.bash_profile"
            if not os.path.exists(home):
                open(home,'w')
            Ropen=open(home,'r')
            for line in Ropen:
                file_data += line
            Ropen.close()
            file_data = file_data + "\nexport " + name + "='" + value + "'\n"

            Wopen=open(home,'w')
            Wopen.write(file_data)
            Wopen.close()

            os.system("source " + home)
            os.environ[name] = value
            successlog("修改环境变量成功")
        except BaseException as error:
            faillog("mac下修改环境变量失败：" + format(error))
            return None
    
    def remove_linux_and_macos_env(self,name,value):
        try:
            file_data = ""
            home = os.environ['HOME'] + "/.bash_profile"
            Ropen=open(home,'r')
            for line in Ropen:
                if name + "=" not in line:
                    file_data += line
            Ropen.close()

            Wopen=open(home,'w')
            Wopen.write(file_data)
            Wopen.close()
            os.unsetenv[name]
            successlog("删除环境变量成功")
            os.system("source " + home)
        except BaseException as error:
            faillog("mac下删除环境变量失败" + format(error))



class System():
    def get_platform(self):
        sys_platform = sys.platform
        if sys_platform == "linux2" :
            return "Linux" 
        elif sys_platform == "win32" :
            return "Windows" 
        elif sys_platform == "cygwin" :
            return "Windows/Cygwin"
        elif sys_platform == "darwin" :
            return "Mac OS X"
        elif sys_platform == "os2" :
            return "OS/2"
        elif sys_platform == "os2emx" :
            return "OS/2 EMX"
        elif sys_platform == "riscos" :
            return "RiscOS"
        elif sys_platform == "atheos" :
            return "AtheOS"

    

if __name__ == "__main__":
    pass
    # SysEvn().set_system_environment('MATCH_PASSWORD','123456')
    # name = "MATCH_PASSWORD"
    # result = re.findall(r'export ' + name + '=\'(.+?)\'',line, re.M|re.I)
    # print(len(result)) 
    # print(SysEvn().get_system_environment("MATCH_PASSWORD"))

    home = '/Users/v-sunweiwei/Desktop/extension/test.rb'
    open(home,'w')
    