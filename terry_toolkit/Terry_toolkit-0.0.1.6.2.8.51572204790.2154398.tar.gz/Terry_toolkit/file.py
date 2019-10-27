# -*- coding: utf-8 -*-
# 对文件进行预处理
import os,re
import json


class File:
    def __init__(self):
        pass
 
    
    def mkdir(self,path):
        """创建文件夹

        >>> mkdir('test/1')

        """
    
        folder = os.path.exists(path)
    
        if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
            os.makedirs(path)            #makedirs 创建文件时如果路径不存在会创建这个路径
            print ("---  new folder...  ---")
            print ("---  OK  ---")
            # return true
    
        else:
            print ('---  There is this folder!  ---')
    





    def all_path(self ,dirname):
        """遍历文件夹下的所有文件

        >>> all_path(dirname)
        """

        result = []#所有的文件

        for maindir, subdir, file_name_list in os.walk(dirname):

            # print("1:",maindir) #当前主目录
            # print("2:",subdir) #当前主目录下的所有目录
            # print("3:",file_name_list)  #当前主目录下的所有文件

            for filename in file_name_list:
                apath = os.path.join(maindir, filename)#合并成一个完整路径
                result.append(apath)

        return result

    # 遍历目录文件夹
    def file_List(self, path, type='txt'):
        """
        遍历目录文件夹
        支持潜逃目录

        >>> file_List('/home/','txt')


        """
        files = []
        
        for file in self.all_path(dirname = path):

            if file.endswith("." + type):
                # print(path+file)
                files.append(file)
        return files

    #打开文件
    def open_file(self, file):
        """

        多编码兼容打开文件

        >>> open_file('a.txt'):
        """
        # print('open_file',file)
        if os.path.isfile(file):
            # print('open_file 存在',file)
            try:
                fileObj = open(file, encoding='utf-8').read()  # 读入文件
                # print('utf8',file)
            except:
                fileObj = open(file, encoding='gbk').read()  # 读入文件
                # print('尝试gbk打开',file)
            # print('open_file 成功',file)
            return fileObj
        else:
            # print('open_file 失败',file)
            return False
    # 清理多余的换行空格等
    def clear(self, string):
        """Summary of class here.

        Longer class information....
        Longer class information....

        Attributes:
            likes_spam: A boolean indicating if we like SPAM or not.
            eggs: An integer count of the eggs we have laid.
        """

        # return string.strip()
        # for line in string.readlines():
        # string = re.sub('[\n]+', '\n', string)
        string = string.replace('\n', '').replace(
            '\n\n', '\n').replace('\r\n', '\n').replace('   ', '\n')
        # string = string.replace('\n\n', ' ').replace('\n', '')
        string = re.sub(' +', ' ', string)
        return string
