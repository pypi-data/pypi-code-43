#!/usr/bin/env python

import os
import re
import pandas as pd
import numpy as np
pd.set_option("display.max_colwidth", 800) #prevents truncated reads
from concurrent import futures
from collections import namedtuple 
import gzip
import argparse
import textwrap
import humanize


class Container:
    #Provide nested dot notation to object for each read with stats, fq.read1.fastq --> 'sample_S25_L001_R1.fastq.gz'
    def __init__(self, sample_name, fastq, file_size, total_read_count, sampling_size, length_mean, read_average, reads_gt_q30):
        self.sample_name = sample_name
        self.fastq = fastq
        self.file_size = file_size
        self.total_read_count = total_read_count
        self.sampling_size = sampling_size
        self.length_mean = length_mean
        self.read_average = read_average
        self.reads_gt_q30 = reads_gt_q30


class FASTQ_Quality:
    '''
    Files must be .gz zipped
    Paired reads must contain _R1 or _R2 in file name

    Along with the FASTQ file and sample name 5 FASTQ attributes are obtained:
        file_size --> FASTQ file size (human readable)
        total_read_count --> Total read count within each FASTQ file
        sampling_size  --> Random analyzed read count
        length_mean --> Average read length
        read_average --> Average read quality
        reads_gt_q30 --> Read counts with an average quality greater than 30

    Note: when calculating percent of reads above Q30 use reads_gt_q30/sampling_size

    After ran object will contain nested dot notation for each read, fq.read1.fastq --> 'sample_S25_L001_R1.fastq.gz'
    '''
    def __init__(self, read1, read2=None, sampling_number=10000):
        quality_key = {'!':'0', '"':'1', '#':'2', '$':'3', '%':'4', '&':'5', "'":'6', '(':'7', ')':'8', '*':'9', '+':'10', ',':'11', '-':'12', '.':'13', '/':'14', '0':'15', '1':'16', '2':'17', '3':'18', '4':'19', '5':'20', '6':'21', '7':'22', '8':'23', '9':'24', ':':'25', ';':'26', '<':'27', '=':'28', '>':'29', '?':'30', '@':'31', 'A':'32', 'B':'33', 'C':'34', 'D':'35', 'E':'36', 'F':'37', 'G':'38', 'H':'39', 'I':'40'}
        self.fastq_list = []
        for read in [read1, read2]:
            if read: #append if not None
                self.fastq_list.append(read)
        if read2:
            self.paired = True
        self.sample_name = re.sub('_.*', '', os.path.basename(read1))
        self.sampling_number = sampling_number
        self.root_dir = str(os.getcwd())
        self.quality_key = quality_key

    
    def fastq_stats(self, fastq):
        #Determine read type
        read1_pattern = re.compile('.*_R1.*')
        read2_pattern = re.compile('.*_R2.*')
        if read1_pattern.match(fastq):
            read = "read1"
        elif read2_pattern.match(fastq):
            read = "read2"
        else:
            read = fastq
        file_size = humanize.naturalsize(os.path.getsize(fastq))
        df = pd.read_csv(gzip.open(fastq, "rt"), header=None, sep='^') #basically set sep to None
        #Starting at row 3, keep every 4 row
        #Random sample specified number of rows
        total_read_count = int(len(df.index)/4)
        sampling_size = int(self.sampling_number)
        if sampling_size > total_read_count:
            sampling_size = total_read_count
        df = df.iloc[3::4].sample(sampling_size)
        dict_mean={}
        list_length=[]
        for index, row in df.iterrows():
            base_qualities=[]
            for base in list(row.to_string(index=False))[1:]:
                base_qualities.append(int(self.quality_key[base]))
            #mean quality of read
            dict_mean[index] = np.mean(base_qualities)
            list_length.append(len(base_qualities))
        length_mean = np.mean(list_length)
        df_mean = pd.DataFrame.from_dict(dict_mean, orient='index', columns=['ave'])
        read_average = df_mean['ave'].mean()
        reads_gt_q30 = len(df_mean[df_mean['ave'] >= 30])
        print(f'{fastq} --> File Size: {file_size}, Total Reads: {total_read_count:,}, Random Analyzed Reads: {sampling_size:,}, Mean Read Length: {length_mean:.1f}, Mean Read Quality: {read_average:.1f}, Reads Passing Q30: {reads_gt_q30/sampling_size:0.1%}')
        container = Container(self.sample_name, fastq, file_size, total_read_count, sampling_size, length_mean, read_average, reads_gt_q30)
        with open (f'{self.sample_name}_stats.txt', 'a') as stat_file:
            print(f'FASTQ:\t{fastq}', file=stat_file)
            print(f'File Size: {file_size}', file=stat_file)
            print(f'Total Reads: {total_read_count:,}', file=stat_file)
            print(f'Random Analyzed Reads: {sampling_size:,}', file=stat_file)
            print(f'Mean Read Length: {length_mean:.1f}', file=stat_file)
            print(f'Mean Read Quality: {read_average:.1f}', file=stat_file)
            print(f'Reads Passing Q30: {reads_gt_q30/sampling_size:0.1%}\n', file=stat_file)

        return read, container

    def run(self):

        for myfastq in self.fastq_list:
            read, container = self.fastq_stats(myfastq)

        # with futures.ProcessPoolExecutor() as pool:
        #     for read, container in pool.map(self.fastq_stats, self.fastq_list):
        #         setattr(self, read, container)

if __name__ == "__main__": # execute if directly access by the interpreter

    #from sbio.fastq_quality import FASTQ_Quality

    parser = argparse.ArgumentParser(prog='PROG', formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\

    ---------------------------------------------------------
    Files must be .gz zipped
    Paired reads must contain _R1 or _R2 in file name

    Usage: fastq_quality.py -r1 *R1*.fastq.gz -r2 *R2*.fastq.gz
    Can specify sampling number: fastq_quality.py -r1 *R1*.fastq.gz -r2 *R2*.fastq.gz -n 100
    or use kwarg when creating object:
        fq = FASTQ_Quality(read1, read2, sampling_number=100)
        fq.run()
    single read can be called
        fq = FASTQ_Quality(read)
        fq = FASTQ_Quality(read, sampling_number=100)

    '''), epilog='''---------------------------------------------------------''')
    
    parser.add_argument('-r1', '--read1', action='store', dest='read1', required=True, help='Required: single read')
    parser.add_argument('-r2', '--read2', action='store', dest='read2', default=None, required=False, help='Optional: paired read')
    parser.add_argument('-n', '--sampling_number', action='store', dest='sampling_number', required=False, default=10000, help='Optional: number of random reads selected')

    args = parser.parse_args()
    read1 = args.read1
    read2 = args.read2
    sampling_number = args.sampling_number
    
    print("\nSET ARGUMENTS: ")
    print(args)

    fq = FASTQ_Quality(read1, read2, sampling_number)
    fq.run()