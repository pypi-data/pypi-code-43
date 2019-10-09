#!/usr/bin/env python
# coding: utf-8



import os
def Get_all_file(path):
    paths,files = [],[]
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:    
            #print (file)
            p = os.path.join(r, file)
            paths.append(os.path.abspath(p))
            files.append(file)
    for f in files:
        #print(f)
        pass
    return paths, files



path = '/work/06021/kh36969/lonestar/test/flank'
paths_flank, files_flank = Get_all_file(path)

with open("commend.sh", "w") as text_file:
    for x in paths_flank:
        text_file.write("python3 run.py "+x+'\n')



