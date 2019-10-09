import os
import Get_every_protein
from Get_every_protein import *
from Bio import SeqIO
import csv
def protein(index):
    path=index+'.fna' 
    print(path)
    threshold  = 0
    protein_fasta(path ,threshold)

#infile = './work/csv_file/test_infile0.csv'
#protein(infile)