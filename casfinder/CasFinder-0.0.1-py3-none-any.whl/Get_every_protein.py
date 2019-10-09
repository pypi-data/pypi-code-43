from Bio import SeqIO
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC


def translater(sequence,threshold): #sequence = protein seq, threshold = min len
    protein_box = []
    protein_seq = []
    position = []
    count = -1
    for x in sequence:
        count = count + 1
        if protein_seq != [] and x != '*':
            protein_seq[0] = protein_seq[0] + x
        if protein_seq == [] and x =='M':
            protein_seq.append(x)
            front = count
        if x == '*' and protein_seq != []:
            protein_seq[0] = protein_seq[0] + x
            if len(protein_seq[0]) >= 0:
                back = count
                protein_box.append(protein_seq[0])
                position.append([front*3,back*3])
                front = 0
                back = 0
            protein_seq = []
    
    return protein_box ,position


def every_protein(sequence, threshold):
    sequence_1 = sequence.seq
    x = len(sequence_1)%3
    if x ==0:
        sequence_2 = sequence.seq[1:]+'N'
        sequence_3 = sequence.seq[2:]+'NN'
        sequence_4 = (sequence.seq.reverse_complement())
        sequence_5 = (sequence.seq.reverse_complement())[1:]+'N'
        sequence_6 = (sequence.seq.reverse_complement())[2:]+'NN'
    elif x ==1:
        sequence_1 = sequence.seq + 'NN'
        sequence_2 = sequence.seq[1:]
        sequence_3 = sequence.seq[2:]+'N'
        sequence_4 = (sequence.seq.reverse_complement())+ 'NN'
        sequence_5 = (sequence.seq.reverse_complement())[1:]
        sequence_6 = (sequence.seq.reverse_complement())[2:]+'N'
    else:
        sequence_1 = sequence.seq + 'N'
        sequence_2 = sequence.seq[1:] + 'NN'
        sequence_3 = sequence.seq[2:]
        sequence_4 = (sequence.seq.reverse_complement()) + 'N'
        sequence_5 = (sequence.seq.reverse_complement())[1:] + 'NN'
        sequence_6 = (sequence.seq.reverse_complement())[2:]
    sequence_1_pro = sequence_1.translate()
    sequence_2_pro = sequence_2.translate()
    sequence_3_pro = sequence_3.translate()
    sequence_4_pro = sequence_4.translate()
    sequence_5_pro = sequence_5.translate()
    sequence_6_pro = sequence_6.translate()
    protein_box1, position1 = translater(sequence_1_pro,threshold)
    protein_box2, position2 = translater(sequence_2_pro,threshold)
    protein_box3, position3 = translater(sequence_3_pro,threshold)
    protein_box4, position4 = translater(sequence_4_pro,threshold)
    protein_box5, position5 = translater(sequence_5_pro,threshold)
    protein_box6, position6 = translater(sequence_6_pro,threshold)
    for x in position1:
        x[0] = x[0] + 1
        x[1] = x[1] + 3
    for x in position2:
        x[0] = x[0] + 2
        x[1] = x[1] + 4
    for x in position3:
        x[0] = x[0] + 3
        x[1] = x[1] + 5
    for x in position4:
        x[0] = len(sequence.seq)- x[0] 
        x[1] = len(sequence.seq)- x[1] -2
    for x in position5:
        x[0] = len(sequence.seq)- x[0] -1
        x[1] = len(sequence.seq)- x[1] -3
    for x in position6:
        x[0] = len(sequence.seq)- x[0] -2
        x[1] = len(sequence.seq)- x[1] -4
    protein = protein_box1 + protein_box2 + protein_box3 + protein_box4 + protein_box5 + protein_box6
    position_all = position1 + position2 + position3 + position4 + position5 + position6
    return protein, position_all

def protein_fasta(file_name ,threshold):
    records_box = list(SeqIO.parse(file_name,"fasta"))
    Protein_seq = []
    position_all_box = []
    for sequence in records_box:
       protein, position_all = every_protein(sequence, threshold)
       Protein_seq = Protein_seq +protein
       position_all_box = position_all_box +position_all
    organism_name = records_box[0].description
    id_num = 0
    record_box = []
    for sequence in Protein_seq:
        record = SeqRecord(Seq(sequence,
                               IUPAC.protein),
                           id=str(position_all_box[id_num][0])+'-'+str(position_all_box[id_num][1]), name='unknown_protein',
                           description= organism_name)
        id_num = id_num +1
        record_box.append(record)
    out_file = file_name[0:-3] + "faa"
    SeqIO.write(record_box, out_file, "fasta")

#test part
'''
file_name = '/home/hk/cripsr/test/NC_023011.fna'
threshold  = 50
protein_fasta(file_name ,threshold)
'''
