import csv
import numpy as np
import os 
import stat  
import shutil
from cleaner import *

def separater(PATH,csv_file_path,file_size):
    clear_dir(PATH)
    with open (csv_file_path, newline = '') as csvfile:
        pamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        row_list = []
        for row in pamreader:
            print(row)
            row_list.append(row)
        title = row_list[0]
        row_list = row_list[1:]
    
    os.makedirs(PATH+'csv_file')
    size = len(row_list)
    file_num = int(size/file_size)
    file_name_box = []
    for order in np.arange(0,file_num-1,1):
        temp_list = []
        temp_list.append(title)
        for content in row_list[order*file_size:(order*file_size + file_size)]:
            temp_list.append(content)
        file_name = PATH +'csv_file/'+ 'test_infile%d.csv'%order    
        with open(file_name, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for content in temp_list:
                spamwriter.writerow(content)
        file_name_box.append(file_name)
    if (file_num-1) ==0:
        order = -1
    file_name = PATH +'csv_file/'+ 'test_infile%d.csv'%(order+1)
    file_name_box.append(file_name)
    with open(file_name, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(title)
        for content in row_list[(order+1)*file_size:]:
            spamwriter.writerow(content)
            
    return file_name_box

def SH_generater(PATH,file_name_box):
    f = open("commend.sh","a+")
    count = 0
    for csv_name in file_name_box:
        clear_dir(PATH+"workspace/working%d"%count)
        clear_dir(PATH+"output/result%d"%count)
        f.write("python3 main.py --workingdir "+PATH+"workspace/working%d"%count +" --outdir " +
                PATH +"output/result%d"%count+" "+csv_name+"\n")
        count= count +1

#python main.py --workingdir ./test/test_temp --outdir ./test/test_output ./test/test_infile.csv
def task_generater():
    PATH = './work/'
    csv_file_path="./genome/test_infile.csv"
    file_size = 1
    file_name_box = separater(PATH,csv_file_path,file_size)
    SH_generater(PATH,file_name_box)

'''  
PATH = './work/'
csv_file_path="./genome/test_infile.csv"
file_size = 1
file_name_box = separater(PATH,csv_file_path,file_size)
SH_generater(PATH,file_name_box)        
'''
