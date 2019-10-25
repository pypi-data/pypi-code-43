import argparse
from . import gene as Gene


"""" This script will take a .rds file and translate every read. It will then
return all amino acid sequences of length >= 11. AA sequences are broken up
first by reading frame, then by stop codon.

By Pavel Vaysberg
pvaysberg@gmail.com
Last updated: 4/9/14

Edited by Maximilian Miller
mmiller@bromberglab.org
Last updated: 4/18/18
"""


# DNA codon table
bases = ['T', 'C', 'A', 'G']
codons = [a+b+c for a in bases for b in bases for c in bases]
amino_acids = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
codon_table = dict(zip(codons, amino_acids))


# Function to translate a DNA sequence, looking at all 6 reading frames
# Will return a list of all AA sequences >= 11, separated by stop codons

class Peptide:
    chain = ""
    genes = []

    def __init__(self, chain):
        self.chain = str(chain)
        self.genes = []

    def addgene(self, gene):
        self.genes.append(gene)
        return

    def getgenenames(self):
        names = []
        for gene in self.genes:
            names.append(gene.name)
        return names


def replace(sequence):
    new_seq = ''
    for x in sequence:
        if x == 'A':
            new_seq += 'T'
            continue
        if x == 'T':
            new_seq += 'A'
            continue
        if x == 'C':
            new_seq += 'G'
            continue
        if x == 'G':
            new_seq += 'C'
            continue
    return new_seq


def trim(sequence):
    # EDITED by czhu@bromberglab.org:    trim the reads on both sides, removing the "n"s
    # EDITED by mmiller@bromberglab.org: trim the reads on both sides, removing all alternatives
    alternatives_zero = ["Z"]
    alternatives_two = ["W", "S", "M", "K", "R", "Y"]
    alternatives_three = ["B", "D", "H", "V"]
    alternatives_four = ["N"]
    alternatives_all = alternatives_zero + alternatives_two + alternatives_three + alternatives_four
    mid = int(len(sequence)/2)
    seq_1 = sequence[:mid]
    seq_2 = sequence[mid:]
    index_left = 0
    index_right = len(seq_2)
    for alterative in alternatives_all:
        if alterative in sequence:
            index_1 = seq_1.rfind(alterative)
            if (index_1 + 1) > index_left:
                index_left = index_1 + 1
            index_2 = seq_2.find(alterative)
            if index_2 != -1 and index_2 < index_right:
                index_right = index_2
    seq_1_trim = seq_1[index_left:]
    seq_2_trim = seq_2[:index_right]
    seq_trim = seq_1_trim + seq_2_trim
    return seq_trim


def translate(sequence, genes):
    # return value
    peptidelist = []

    # 2 strands
    for s in range(0, 2):
        # 3 reading frames
        for n in range(0, 3):

            sequence1 = trim(sequence.upper())

            if s == 1:  # opposite strand
                sequence1 = replace(sequence1[::-1])

            presequence = ""
            for c in range(0, len(sequence), 3):

                codon = sequence1[c+n:(c+n)+3]
                # we've reached the end
                if len(codon) < 3:
                    break

                # building our peptide sequence
                presequence = presequence + codon_table[codon]

            fraglist = presequence.split('*')

            # this pointer tracks the location in the gene that our slices of AA sequences correspond to
            pointer = 1

            # assign genes to each peptide
            for x in fraglist:

                # accounting for stop codon
                if not pointer == 1:
                    pointer += 1

                if len(x) < 11:
                    # this accounts for multiple stop codons
                    if x == '':
                        pointer += 1
                    pointer += len(x)
                    continue
                else:
                    peptide = Peptide(x)

                for gene in genes:
                    # gene is in opposite strand, don't need it
                    if (gene.strand == '+' and s == 1) or (gene.strand == '-' and s == 0):
                        continue

                    pepstart = 1 + 3*(pointer-1)
                    pepend = (pointer + len(x))*3

                    # looking for gene on opposite strand
                    if s == 1 and gene.strand == '-':
                        mstrand_start = len(sequence1) - gene.locOnReadEnd
                        mstrand_end = len(sequence1) - gene.locOnReadStart

                        # checks if the amino acid sequence is NOT in range of the gene
                        if (pepstart + n) > mstrand_end or (pepend + n) < mstrand_start:
                            continue
                        else:
                            peptide.addgene(gene)

                    # checks if the amino acid sequence is NOT in range of the gene
                    elif (pepstart + n) > gene.locOnReadEnd or (pepend + n) < gene.locOnReadStart:
                        continue
                    else:
                        peptide.addgene(gene)

                pointer += len(x)
                peptidelist.append(peptide)
    return peptidelist


def process_line(outfile, readline, sequence):
    genes = []
    for n in range(3, len(readline) - 1, 3):
        locsonread = readline[n + 2].split('-')
        genes.append(Gene.Gene(readline[n], readline[n + 1], int(locsonread[0]), int(locsonread[1])))
    peptides = translate(sequence, genes)
    for idx, peptide in enumerate(peptides, 1):
        outfile.writelines([
            f'>{",".join(readline)},P_{idx},{",".join(map(str, peptide.getgenenames()))}\n',
            f'{peptide.chain}\n'
        ])


def main(organism, rdsfile, result_path):
    with open(result_path + organism + '.prd', 'w') as outfile:
        with open(rdsfile, 'r') as reads:
            sequence = ''
            readline = None
            for line in reads:
                line = line.strip()
                if line:
                    if line[0] == '>':
                        if sequence:
                            process_line(outfile, readline, sequence)
                            sequence = ''
                        header = line[1:].replace(' ', '')
                        readline = header.split(',')
                    else:
                        sequence += line

                if sequence:
                    next_line = next(reads, None)
                    if next_line is None:
                        process_line(outfile, readline, sequence)
                    else:
                        next_line = next_line.strip()
                        if next_line:
                            if next_line[0] == '>':
                                process_line(outfile, readline, sequence)
                                sequence = ''
                                header = next_line[1:].replace(' ', '')
                                readline = header.split(',')
                            else:
                                sequence += next_line


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script will take an .rds file and translate the sequences within. "
                    "It will return an output file containing all peptides of length >= 11"
    )

    parser.add_argument('-o', '--org', help="The metagenome, format: metagenomeid_lane")
    parser.add_argument('-r', '--rds', help="The .rds file you'd like to translate (include path)")
    parser.add_argument('-p', '--pth', help="The path to store the result file (include the final '/')")

    args = parser.parse_args()
    rdsfile_ = args.rds
    organism_ = args.org
    result_path_ = args.pth

    if not organism_:
        organism_ = input("Enter an metagenome id , format: metagenomeid_lane: ")

    if not rdsfile_:
        rdsfile_ = input("Enter an .rds file (include path): ")

    if not result_path_:
        result_path_ = input("Path to store the result file (include the final '/').")

    main(organism_, rdsfile_, result_path_)
