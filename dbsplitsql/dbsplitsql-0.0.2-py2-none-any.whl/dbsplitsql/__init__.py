#!/usr/bin/env python

import re
import os
import errno
import sys
import glob

def write_data_to_file(folder,file_name, list_data):
    if not os.path.exists("./"+folder):
        try:
            os.makedirs("./"+folder)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise
    with open("./"+ folder + "/" + file_name + ".sql", 'a+') as my_file:
        my_file.writelines(list_data)
        my_file.close()

def write_ddl_to_file(x,y,lines,f_extns,extn):
     if x != 0 :
        match = re.findall(r"CREATE (.*)", str(lines[y]))
        if match:
            file=str(match).split() 
            file_name = file[1].strip().replace(";\']","")
            file_name = file_name.replace(f_extns[0] + ".","")
            if y == x-1 :
                write_data_to_file(extn+f_extns[0],str(file_name), lines[y])
            else:
                write_data_to_file(extn+f_extns[0],str(file_name), lines[y: x-1])

def convert_semi_to_newline(filename):  
    localFile = open(filename, 'r')
    data=localFile.read()
    data = data.replace(';',';\n') 
    fin = open(filename, "wt")
    fin.write(data)
    fin.close()
    f_extns = filename.split(".")
    with open(filename) as f:
        count = sum(1 for _ in f)
    
    localFile = open(filename, 'r')
    lines = localFile.readlines()
    return [filename , lines , count, f_extns]

def check_table_view(lines,f_extns,extn,count):
    line_numbers = 0
    x = 0
    y = 0
    for line in lines:
        if '-- DDL Statements for Table' in line:
            del lines[line_numbers]
        if 'CREATE TABLE' in line:            
            y = x
            x = line_numbers
            write_ddl_to_file(x,y,lines,f_extns,extn)            

        if 'CREATE VIEW' in line:
            y = x
            x = line_numbers
            write_ddl_to_file(x,y,lines,f_extns,extn)

        line_numbers = line_numbers+1
    write_ddl_to_file(count,x,lines,f_extns,extn)

def create_files_using_file(filename):
    responseData=convert_semi_to_newline(filename)
    filename=responseData[0]
    lines=responseData[1]
    count=responseData[2]
    f_extns=responseData[3]
    extn=""
    check_table_view(lines,f_extns,extn,count)
    
def create_files_using_directory(directory):
    if not os.path.exists("./Output/"):
        try:
            os.makedirs("./Output")
        except OSError as error:
                    if error.errno != errno.EEXIST:
                        raise
    filenames= glob.glob('./' + directory + '/*.*')   
    for filename in filenames:     
        f=open(filename, 'r')  
        directory, folder=os.path.split(filename)
        print(filename)
        f.read()
        f.close() 
        f_extns = folder.split(".")
        extn="./Output/"  
        responseData=convert_semi_to_newline(filename)
        filename=responseData[0]
        lines=responseData[1]
        count=responseData[2]            
        check_table_view(lines,f_extns,extn,count)

def main(args):
    print(len(args))
    for index,arg in enumerate(args):
        if '-f' in arg:
            create_files_using_file(args[index+1])
        if '-D' in arg:
            create_files_using_directory(args[index+1])

if __name__ == "__main__":
    main(sys.argv)