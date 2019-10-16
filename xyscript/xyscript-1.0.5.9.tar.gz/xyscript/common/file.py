#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xyscript.config import Config
import stat
from xyscript.common.xylog import *
from xyscript.common.interaction import Interaction
import zipfile
import itertools as its
from progressbar import *
from xyscript.common.timeusage import func_time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, as_completed

class File:
    def compress_file_with_password(self,path,password):
        file_name = path.split("/")[-1]
        zip_file_name = ".".join(file_name.split(".")[0:-1]) + ".zip"
        shell = "zip -re " + zip_file_name 
        os.system(shell)
    
    @func_time
    def uncompress_file(self,path):
        try:
            file_name = path.split("/")[-1]
            sup_path = path[0:-(len(file_name))]
            pwd_file_name = ".".join(file_name.split(".")[0:-1]) + ".txt"
            pwd_file_path = sup_path + pwd_file_name
            zf = self.get_zfile(file_name,path)
            self.make_pw_file(pwd_file_path,zf)
            

            # pwd_file = open(pwd_file_path)

            # executor = ThreadPoolExecutor(max_workers=10)
            # all_task = [executor.submit(self.extractFile,(zf),(line.strip('\n')),(index)) for (index,line) in enumerate(pwd_file.readlines()[0:-2])]
            # for future in as_completed(all_task):
            #     data = future.result()
            #     if data is not None:
            #         #print(format(data))
            # pwd_file.close()
        except BaseException as error:
            faillog("uncompress file failed:" + format(error))

    def get_zfile(self,file_name,path):
        zf = None
        if file_name.endswith(".zip"):
            zf = zipfile.ZipFile(path)
        elif file_name.endswith(".rar"):
            try:
                from unrar import rarfile
            except:
                path = 'pip3 install --upgrade pip'
                os.system(path)
                path = 'pip3 install unrar'
                os.system(path)
                from unrar import rarfile
                zf = rarfile.RarFile(path)
        return zf
        
    def extractFile(self,zfile,password,current):
        try:
            zfile.extractall(pwd=password.encode('utf-8'))
            return 'Found password :'+ password +'\n'
        except:
            return None

    def make_pw_file(self,path,zfile):
        num_array = "1234567890"
        capital_case_array = "ZXCVBNMASDFGHJKLQWERTYUIOP"
        lower_case_array = "zxcvbnmasdfghjklqwertyuiop"
        special_character_array = "~!@#$%^&*()_+;:\'\",./<>?\|\b"

        inter = Interaction()
        num = inter.get_user_input("是否存在数字(y/n)")
        capital_case = inter.get_user_input("是否存在大写字母(y/n)")
        lower_case = inter.get_user_input("是否存在小写字母(y/n)")
        special_character = inter.get_user_input("是否存在特殊字符(y/n)")
        max_length = inter.get_user_input("最大长度")
        min_length = inter.get_user_input("最小长度")
        repeated_cha = inter.get_user_input("重复字符个数")
        
        words = ""
        if num == "y":
            words = words + num_array
        if capital_case == "y":
            words = words + capital_case_array
        if lower_case == "y":
            words = words + lower_case_array
        if special_character == "y":
            words = words + special_character_array

        words = "10245678WEIwei"
        
        maxlen = 12
        minlen = 1
        if max_length is not None:
            maxlen = int(max_length)
        if min_length is not None:
            minlen = int(min_length)

        try:
            # dic = open(path,"a")
            # #清空文件
            # dic.seek(0)
            # dic.truncate()
            # warninglog("This will take a few minutes. Wait a moment")
            executor = ThreadPoolExecutor(max_workers=100)
            for count in range(minlen,maxlen +1):
                #print("\n正在生成 %d 位密码，时间可能有点长，请耐心等待..." %(count))
                r = its.product(words,repeat=count)

                array = []
                for i in r:
                    array.append("".join(i))

                all_task = [executor.submit(self.extractFile,(zfile),(line),(index)) for (index,line) in enumerate(array)]

                for index,future in enumerate(as_completed(all_task)):
                    sys.stdout.write("\r正在尝试: %d 位数，进度:%d / %d" %(count,index+1, len(all_task)))
                    sys.stdout.flush()
                    data = future.result()
                    if data is not None:
                        #print("\n %s" %(format(data)))
                        return
                    # dic.write("".join(i))
                    # dic.write("\n")
            # dic.close()
            #print("\n")
            warninglog("Please confirm the correct rules")
        except BaseException as error:
            #print("\n")
            faillog("make password file failed:" + format(error))


    def progressbar(self,nowprogress,total):
        get_progress = int((nowprogress + 1) * (50/total))
        get_pro = int(50 - get_progress)
        percent = (nowprogress + 1) * (100/total)
        #print(" " + "[" + ">" + get_progress + "-" + get_pro + ']' + "%.2f" % percent + "%")

    def find_files_contain(self,path,name):
        """找到目录下包含name的所有文件"""
        result_array = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if name in file:
                    result_array.append(os.path.join(root, file))
        return result_array

    def creat_folder(self,path):
        from pathlib import Path

        try:
            #创建目录
            if Path(path).exists():
                # warninglog(path + " is exists")
                pass
            else:
                os.makedirs(path)
                # successlog("creat folder success:" + path)

            # 更改权限
            os.chmod(path, stat.S_IRWXU)
        except BaseException as error:
            faillog(format(error))


if __name__ == "__main__":
    File().uncompress_file("/Users/v-sunweiwei/Desktop/extension/test/1.rar")

    # File().creat_folder("~/xycache/test")
    # File().make_pw_file("/Users/v-sunweiwei/Desktop/extension/test/ziptest.txt")

    # path = '"'+os.path.dirname(sys.executable)+'\\scripts\\pip3" install --upgrade pip'
    # #print(path)
    # for i in range(1000):
    #     percent = 1.0 * i / 1000 * 100
    #     sys.stdout.write("\r 你好: %d / %d" %(percent, 100))
    #     sys.stdout.flush()
    #     time.sleep(0.01)
    # #print("\n")

