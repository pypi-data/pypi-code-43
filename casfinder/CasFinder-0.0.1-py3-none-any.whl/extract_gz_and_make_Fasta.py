import os
import Get_every_protein
from Get_every_protein import *
from Bio import SeqIO
import gzip
from cleaner import *
def file_name_finder():
    file_name = os.getcwd()  
    return file_name

def list_all_files(rootdir):
    _files = []
    list = os.listdir(rootdir) 
    for i in range(0,len(list)):
           path = os.path.join(rootdir,list[i])
           if os.path.isdir(path):
              _files.extend(list_all_files(path))
           if os.path.isfile(path):
              _files.append(path)
    file_name_filter = []
    for file in _files:
        if file[-3:] == ".gz":
            file_name_filter.append(file)

    return file_name_filter

def modif(str_1):
    for x in range(len(str_1)):
        if str_1[x] == '.':
            num = x
            break
        else:
            pass
    str_need = str_1[:num]
    return str_need

def un_gz(file_name):
    clear_dir('./genome/genome_temp')
    num = 0
    file_box = []
    for file in file_name:
        g = gzip.GzipFile(mode="rb", fileobj=open(file, 'rb'))
        open(r"./genome/genome_temp/%d.fna"%(num), "wb").write(g.read())
        g.close()
        file_box.append("./genome/genome_temp/%d.fna"%(num))
        num=num +1
    file_name_box = []
    for file_x in file_box:
        records_box = list(SeqIO.parse(file_x,"fasta"))
        str_need = modif(records_box[0].id)
        file_y = './genome/'+ str_need + '.fna'
        SeqIO.write(records_box, file_y , "fasta")
        file_name_box.append(file_y)
        print(file_y)
    return file_name_box

from Bio import SeqIO
import csv    
def write_csv(file_box):
    total_list = [['','Path','organism']]
    count = 0
    for file_name in file_box:
        row_list = []
        seq_record = next(SeqIO.parse(file_name, "fasta"))
        row_list.append(str(count))
        row_list.append(file_name[0:-4])
        row_list.append(seq_record.description)
        total_list.append(row_list)
        count = count+1
    
    with open('./genome/test_infile.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for row in total_list:
            writer.writerow(row)
def extract_fasta(rootdir):
    file_name = list_all_files(rootdir)
    file_name_box = un_gz(file_name)
    write_csv(file_name_box)
    clean_dir('./genome/genome_temp')



