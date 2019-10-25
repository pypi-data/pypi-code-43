import os
import argparse


def parse_fasta(fastafile):
    records = []
    input_file = open(fastafile, 'r')
    header = input_file.readline().rstrip()
    while True:
        sequence = input_file.readline().rstrip()
        line = input_file.readline().rstrip()
        while line and line[0] != '>':
            sequence += line
            line = input_file.readline().rstrip()
        if not line:
            records.append((header[1:], sequence))
            break
        if line and line[0] == '>':
            records.append((header[1:], sequence))
            header = line
    return records


def main(analyzed, fasta_file):
    result_file = "%s/analysis.tsv" % analyzed
    map_file = "%s/ec_count.tsv" % analyzed

    read_mapping_path = "%s/read_map/" % analyzed
    if not os.path.exists(read_mapping_path):
        os.mkdir(read_mapping_path)

    d_EC = {}
    fh = open(result_file, 'r')
    fh.readline()
    for line in fh:
        line = str.strip(line)
        (EC, count) = line.split('\t')
        d_EC[EC] = int(count)
    fh.close()

    d = {}
    fh = open(map_file, 'r')
    for line in fh:
        line = str.strip(line)
        line_list = line.split('\t')
        if len(line_list) != 2:
            continue
        rid = line_list[0]
        EC = line_list[1]
        if not EC in d_EC.keys():
            continue
        if not rid in d.keys():
            d[rid] = EC
        else:
            print(rid)
    fh.close()

    d_to_write = {}
    for description, sequence in parse_fasta(fasta_file):
        rid = ''.join(str(description).split(' '))
        if rid in d.keys():
            EC = d[rid]
            if not EC in d_to_write.keys():
                d_to_write[EC] = ""
            d_to_write[EC] = d_to_write[EC] + ">" + rid + "\n" + sequence + "\n"

    for EC in sorted(d_to_write):
        fhw = open(read_mapping_path + EC + ".fasta", 'w+')
        fhw.write(d_to_write[EC])


if __name__ == "__main__":
    parser = argparse.ArgumentParser("""This script maps generates multifasta file of reads that are mapped to the ECs.""")

    parser.add_argument('-a', '--analyzed', help = "The path to the analyzed result.")
    parser.add_argument('-i', '--input', help = "The input DNA read file.")

    args = parser.parse_args()
    analyzed = args.analyzed
    fasta_file = args.input

    if not analyzed:
        analyzed = input("Enter path to the analyzed result: ")
    if not fasta_file:
        fasta_file = input("Enter input DNA read file:")

    main(analyzed, fasta_file)
