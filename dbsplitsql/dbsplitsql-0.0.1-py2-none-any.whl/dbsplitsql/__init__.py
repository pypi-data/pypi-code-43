import re
import os
import errno
import sys


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

def main():
    filename = raw_input("Input the Filename: ")
    if len(filename) == 0 :
        print("Please enter filename ")
        exit()
    localFile = open('./' + filename, 'r')
    f_extns = filename.split(".")
    lines = localFile.readlines()
    line_numbers = 0
    x = 0
    y = 0
    match = []
    for line in lines:
        if '-- DDL Statements for Table' in line:
            del lines[line_numbers]
        if 'CREATE TABLE' in line:
            # print("Table at line " + str(line_numbers))
            y = x
            x = line_numbers
            # print(x)
            # print(y)
            #print(lines[y: x-1])
            #print(lines[y])
            match = re.findall(r"CREATE (.*)", str(lines[y]))
            file=str(match).split()
            #print(file[1])            
            file_name = file[1].strip().replace(";\']","")
            write_data_to_file(f_extns[0],str(file_name), lines[y: x-1])

        if 'CREATE VIEW' in line:
            y = x
            x = line_numbers
            match = re.findall(r"CREATE (.*)", str(lines[y]))
            file=str(match).split()
            file_name = file[1].strip().replace(";\']","")
            write_data_to_file(f_extns[0],str(file_name), lines[y: x-1])

        line_numbers = line_numbers+1


if __name__ == "__main__":
    main()
