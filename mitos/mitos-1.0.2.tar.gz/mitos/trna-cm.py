from ete2 import layouts, Tree
import re
import glob
import os
import argparse
import cPickle
import itertools
import logging
import os.path
import random
import sys
import time
import re
import multiprocessing
import numpy
from Bio import SeqIO
from Bio.Seq import Seq
import rna.forester
import mitofile
import cPickle as pickle
from os import listdir
import multiprocessing as mp
import random
import rpy2.robjects as ro
import numpy as np
from rpy2.robjects.packages import importr
from Bio.Align.Applications import ClustalwCommandline
from Bio import AlignIO

##### Tasks to do in Lebanon
# 1- Install infernal and hmmer on the mac
# 2- fix the fasta format when sequences are taken to the parent nodes
# 3- fix the model building and add the --mapali to the CMalign call to take the previous sequences up in the tree
# 4- implement the model building up on the tree
# 5- try the models on small dataset and check how to play around with the priori distributions of infernal models
# 6-
# ##


#-------------------------------------------------------
# def align_trna(outdir, node1, node2, gene1_seq, gene2_seq):  # ready -- only tRNA
#       global tree_file
#       result = ""
#       tmp_tree = Tree(tree_file, format=1)
#       total_bit_score1 = 0
#       total_bit_score2 = 0
#       fout = open(outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas", "w")
#       # input="> "+node1+"\n"+gene1_seq+"\n"
#       # input+=node2+"\n"+gene2_seq+"\n"
#       input = node1.seq
#       input += node2.seq
#       fout.write(input)
#       fout.close()
#       model_name1 = node1.model.split("/")[-1].strip(".cm")
#       model_name2 = node2.model.split("/")[-1].strip(".cm")
#       ancestor = tmp_tree.get_common_ancestor(node1.name, node2.name)  # find first common ancestor
#       os.system("cmalign " + node1.model + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas > " + outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth")
#       os.system("cmalign " + node2.model + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas > " + outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth")
#
#       os.system("cmalign -o "+ outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth " + node1.model + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas")
#       os.system("cmalign -o "+ outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth " + node2.model + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas")
#       print node1.name, node2.name
#       fin = open(outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth")
#       for line in fin:
#          if not line.startswith("#") and not line.startswith("NC") and not line == "\n" and not line.startswith("/"):
#              if len(line.split()) > 2:
#                  total_bit_score1 += float(line.split()[3])
#
#       fin = open(outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth")
#       for line in fin:
#          if not line.startswith("#") and not line.startswith("NC") and not line == "\n" and not line.startswith("/"):
#              if len(line.split()) > 2:
#                  total_bit_score2 += float(line.split()[3])
#
#       if total_bit_score1 > total_bit_score2:
#            os.system("cmbuild " + outdir + "/test/test-align/" + ancestor.name + ".cm" + " " + outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth")
#            result = outdir + "/test/test-align/" + ancestor.name + ".cm"
#       else:
#            os.system("cmbuild " + outdir + "/test/test-align/" + ancestor.name + ".cm" + " " + outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth")
#            result = outdir + "/test/test-align/" + ancestor.name + ".cm"
#       return result

#
# def align_trna_old2(outdir, node1, node2,g1,g2):  # ready -- only tRNA
#       global tree_file
#       result = ""
#       tmp_tree = Tree(tree_file, format=1)
#       total_bit_score1 = 0
#       total_bit_score2 = 0
#       fout = open(outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas", "w")
#
#
#       input="> "+node1.name+"\n"+node1.arr[g1]['seq']+"\n"
#       input+="> "+node2.name+"\n"+node2.arr[g2]['seq']+"\n"
#       fout.write(input)
#       fout.close()
#       model_name1 = node1.arr[g1]['model'].split("/")[-1].strip(".cm")
#       model_name2 = node2.arr[g2]['model'].split("/")[-1].strip(".cm")
#       ancestor = tmp_tree.get_common_ancestor(node1.name, node2.name)  # find first common ancestor
#       os.system("cmalign " + node1.arr[g1]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas > " + outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth")
#       os.system("cmalign " + node2.arr[g2]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas > " + outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth")
#
#       os.system("cmalign -o "+ outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth " + node1.arr[g1]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas")
#       os.system("cmalign -o "+ outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth " + node2.arr[g2]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas")
#
#       fin = open(outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth")
#       for line in fin:
#          if not line.startswith("#") and not line.startswith("NC") and not line == "\n" and not line.startswith("/"):
#              if len(line.split()) > 2:
#                  total_bit_score1 += float(line.split()[3])
#
#       fin = open(outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth")
#       for line in fin:
#          if not line.startswith("#") and not line.startswith("NC") and not line == "\n" and not line.startswith("/"):
#              if len(line.split()) > 2:
#                  total_bit_score2 += float(line.split()[3])
#
#       if total_bit_score1 > total_bit_score2:
#            os.system("cmbuild " + outdir + "/test/test-align/" + ancestor.name + ".cm" + " " + outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name1 + ".sth")
#            result = outdir + "/test/test-align/" + ancestor.name + ".cm"
#       else:
#            os.system("cmbuild " + outdir + "/test/test-align/" + ancestor.name + ".cm" + " " + outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_" + model_name2 + ".sth")
#            result = outdir + "/test/test-align/" + ancestor.name + ".cm"
#       return result
#

#
#
# def align_trna(t,outdir, node1, node2,g):  # ready -- only tRNA
#       #print "---------------------------------",node1.name, node2.name, node1.arr['trnF'], node2.arr['trnF']
#
#
#       ### do if only different model is used
#       global tree_file
#
#
#       ancestor = t.get_common_ancestor(node1.name, node2.name)  # find first common ancestor
#       total_bit_score1 = 0
#       total_bit_score2 = 0
#
#       fout = open(outdir + "/test/test-align/"+ ancestor.name + ".fas", "w")
#       fout.write(ancestor.arr[g]['seq'])
#       fout.close()
#       #print node1.arr, node2.arr, ancestor.arr[g]
#       model_name1 = node1.arr[g]['model'].split("/")[-1].strip(".cm")
#       model_name2 = node2.arr[g]['model'].split("/")[-1].strip(".cm")
#
#       ### add --mapali parametere to cmalign as the alignment constructed in the previous run (to get all the sequences progressively when goinf up on the tree)
#       os.system("cmalign " + node1.arr[g]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas > " + outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_m" + model_name1 + ".sth")
#       os.system("cmalign " + node2.arr[g]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas > " + outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_m" + model_name2 + ".sth")
#
#       os.system("cmalign -o "+ outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_m" + model_name1 + ".sth " + node1.arr[g]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas")
#       os.system("cmalign -o "+ outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_m" + model_name2 + ".sth " + node2.arr[g]['model'] + " " + outdir + "/test/test-align/" + node1.name + "_" + node2.name + ".fas")
#
#       #print "n1",node1.name, "n2",node2.name, "m1",model_name1, "m2",model_name2
#       fin = open(outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_m" + model_name1 + ".sth")
#       for line in fin:
#          if not line.startswith("#") and not line.startswith("NC") and not line == "\n" and not line.startswith("/"):
#              if len(line.split()) > 2:
#                  total_bit_score1 += float(line.split()[3])
#
#       fin = open(outdir + "/test/test-align/test-align-score" + node1.name + "_" + node2.name + "_m" + model_name2 + ".sth")
#       for line in fin:
#          if not line.startswith("#") and not line.startswith("NC") and not line == "\n" and not line.startswith("/"):
#              if len(line.split()) > 2:
#                  total_bit_score2 += float(line.split()[3])
#
#       if total_bit_score1 > total_bit_score2:
#            os.system("cmbuild -F " + outdir + "/test/test-align/" + ancestor.name + ".cm" + " " + outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_m" + model_name1 + ".sth")
#            result = outdir + "/test/test-align/" + ancestor.name + ".cm"
#       else:
#            os.system("cmbuild -F " + outdir + "/test/test-align/" + ancestor.name + ".cm" + " " + outdir + "/test/test-align/test-align" + node1.name + "_" + node2.name + "_m" + model_name2 + ".sth")
#            result = outdir + "/test/test-align/" + ancestor.name + ".cm"
#       return result
#
# def trav_tree0(n):
#    if not n.is_leaf():
#        trav_tree(n.get_children()[0])
#    sisters=[]
#    sisters=n.get_sisters()
#    for sis in sisters:
#        print "sis: ",sis.name
#        if  sis.is_leaf():
#            #call align function here
#               n.score=sis.score=3;
#        else:
#            trav_tree(sis.get_children()[0])
#
#
#
#
#
# #
# #
# def aff_seq(n,gene,t):
#    global taxidmap_file
#    ## if not remolded case should be added
#    #print n.name
#
#    for c in n.get_children():
#        n.arr[gene]['seq']+=(aff_seq(c,gene,t) +" ")
#    #print n.arr[gene]['seq']
#    return n.arr[gene]['seq']
#
#    for c in n.get_children():
#        n.score *=aff_seq(c,gene,t)
#    return n.score

##### OLD Abdul and Marwa
#    if not n.is_leaf() :
#        n.arr[gene]['seq']= aff_seq(n.get_children()[0],gene)
#    result=n.arr[gene]['seq']
#
#    if not n.is_root():
#        sisters= n.get_sisters()
#        for sis in sisters:
#            if not sis.is_leaf():
#                sis.arr[gene]['seq'] = aff_seq(sis.get_children()[0],gene)
#            result = result+"    "+gene+"   "+sis.arr[gene]['seq']
#            print n.name, sis.name
#
#    return result

# def affect_score0(n):
#    if (n.score)==0:
#        n.score=affect_score(n.get_children()[0])
#    result=n.score
#    if not n.is_root():
#        sis=n.get_sisters()[0]
#    else:
#        sis=n
#    if sis.score==0:
#        sis.score=affect_score(sis.get_children()[0])
#    if result<sis.score:
#        gene1_seq=get_sequence_trna(accession1, gene1, data)
#        gene2_seq=get_sequence_trna(accession2, gene2, data)
#        result=sis.score
#    return result
#
# def affect_score(tr,outdir,g):
#    #global tree_file
#    #tr= Tree(tree_file,format =1)
#    for nd in tr.traverse('postorder'):
#        if nd.get_children():
#            nd.arr[g]['model']= internal_node_model_build(t,nd,outdir,g)
#            #print nd.name
# def internal_node_model_build(t,n,outdir,g):
#
#    node = n.get_children()[0]
#    sis = n.get_children()[1]
#    result=align_trna(t,outdir,node,sis,g)
#
#
#    return result

# def affect_score(n,outdir,g):
#    global tree_file
#
#    for c in n.get_children():
#        n.arr[g]['model']= affect_score(c,outdir,g)
#    if not n.is_root():
#        sis=n.get_sisters()[0]
#        #for cc in sis.get_children():
#        #    sis.arr[g]['model']= affect_score(cc,outdir,g)
#    n.arr[g]['model']= align_trna(outdir,n,sis,g)
#    print "testestestes",n.name, sis.name, n.arr[g]['model']
#
#    return n.arr[g]['model']
# def affect_score_old_2(n,outdir,g):
#    print n
#    global work_dir
#    if n.score==0:
#        n.score=affect_score_old_2(n.get_children()[0],outdir,g)
#    #result=n.model
#    result = n.arr[g]['model']
#    if not n.is_root():
#        sis=n.get_sisters()[0]
#        if sis.score==0 and not sis.is_leaf():
#            #sis.model=affect_score(sis.get_children()[0],outdir,g1,g2)    #old
#            sis.arr[g]['model']=affect_score_old_2(sis.get_children()[0],outdir,g)
#
#        #result= align_trna(outdir,n,sis,n.seq,sis.seq)  ###old
#        result= align_trna(outdir,n,sis,g)
#
#    return result
#

# def affect_score_old(n,outdir,g1,g2):
#    if n.score==0:
#        n.score=affect_score(n.get_children()[0],outdir,g1,g2)
#    result=n.score
#
#    if not n.is_root():
#        sis=n.get_sisters()[0]
#        if sis.score==0 and not sis.is_leaf():
#            sis.score=affect_score(sis.get_children()[0],outdir,g1,g2)
#        n.score=align_trna(outdir,n.name,sis.name,n.seq,sis.seq,"/homes/brauerei2/marwa/workspace/TaxaModels/004/tRNA-CM/CM-refseq56/NC_000857/trnD.cm")
#        sis.score= align_trna(outdir,n.name,sis.name,n.seq,sis.seq,"/homes/brauerei2/marwa/workspace/TaxaModels/004/tRNA-CM/CM-refseq56/NC_000857/trnF.cm")
#        if n.score < sis.score:
#            result=sis.score
#
#
#    return result

# def travTree(Tr, gene):
#    travNode(Tr.get_tree_root())



# def computeModels(nd, gene):
#     if nd.is_leaf():
#         mod = nd.arr[gene]['model']
#         return mod
#
#     if not nd.is_leaf():
#         mod1, mod2 = computeModels(nd.get_children()[0], gene), computeModels(nd.get_children()[1], gene)
#
#         if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
#             # # alignment based on first child model
#             print "1"
#             print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '
#             #print 'cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth '
#             os.system('cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
#             os.system('cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#         else:  # has grand children >> use mapali
#             print "2"
#             print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' with mapali'
#             print nd.get_children()[0].name, "alignment with best score", findSTH(nd.get_children()[0].name)
#             os.system('cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
#             os.system('cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#         if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
#             # # alignment based on second child model
#             print "3"
#             print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
#             os.system('cmalign \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
#             os.system('cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#         else:  # has grand children >> use mapali
#             print "4"
#             print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
#             print findSTH(nd.get_children()[1].name)
#             os.system('cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
#             os.system('cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#         file = open(work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth', 'r')
#         score1 = 0
#         for line in file:
#             if not line.startswith("#"):
#                 temp = line.split()
#                 score1 += float(temp[6])
#         file.close()
#         #print score1
#
#         file = open(work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth', 'r')
#         score2 = 0
#         for line in file:
#             if not line.startswith("#"):
#                 temp = line.split()
#                 score2 += float(temp[6])
#         file.close()
#         #print score2
#
#         if score1 > score2:
#             print 'building cm at ' + nd.name + ' using ' + nd.get_children()[0].name
#             os.system('cmbuild -F \"'+work_dir+'result_CM_refseq56/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth\" ')
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth\n')
#         else:
#             print 'building cm at ' + nd.name + ' using ' + nd.get_children()[1].name
#             os.system('cmbuild -F \"'+work_dir+'result_CM_refseq56/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth\" ')
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name + ' '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth\n')
#         nd.arr[gene]['model'] = work_dir+'result_CM_refseq56/' + nd.name + '_' + gene + '.cm'
#
#         return nd.arr[gene]['model']
#




# def sub_tree_ratio(tree):
#     for n in tree.traverse():
#         if not n.is_root():
#             if not n.is_leaf():
#                 n_children=len(n.get_leaves())
#                 sis=n.get_sisters()[0]
#                 if not sis.is_leaf():
#                     sis_children=len(sis.get_leaves())
#                 else:
#                     sis_children = 1
#             print n.name, sis.name, n_children, sis_children , "ratio1= "+str(float(n_children/sis_children)), "ration2= "+str(float(sis_children/n_children))
#
#
# def create_fasta_leafs(t,gene):
#     for l in t:
#         f=open(work_dir+"leaf_fasta/"+l.name+"_"+gene+".fas","w")
#         f.write("> "+l.name+"\n"+l.arr[gene]['seq'])
#         f.close()
#
# def models_evaluation(t,models_dir, gene):
#
#     models = [ f for f in listdir(models_dir) if f.endswith(".cm") ]
#
#     for n in t.traverse():
#         if not n.is_leaf():
#             leaves=n.get_leaf_names()
#             for m in models:
#                 if n.name in m and gene in m:
#                     model=os.path.join(models_dir,m)
#                     for l in leaves:
#                         os.system('cmalign --sfile '+work_dir+'models_evaluation/scores/' + l + '_' + gene + '_cm' + n.name + '.sth \"' + model + '\" \"'+work_dir+'leaf_fasta/' + l + '_' + gene + '.fas\" ')
#                 else:
#                     continue
#
#

# def computeModels(nd, gene):
#     if nd.is_leaf() and gene in nd.arr.keys():
#         mod = nd.arr[gene]['model']
#         return mod
#     #else:
#     #    return None
#     if not nd.is_leaf():
#
#         mod1, mod2 = computeModels(nd.get_children()[0], gene), computeModels(nd.get_children()[1], gene)
#         if not mod1 is None and not mod2 is None:   # both children have models for this gene
#             if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
#                 # # alignment based on first child model
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '
#
#                 os.system('/opt/bin/cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
#                 os.system('/opt/bin/cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' with mapali'
#
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#             if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
#                 # # alignment based on second child model
#                 print "3"
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
#                 os.system('/opt/bin/cmalign \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
#                 os.system('/opt/bin/cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
#
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#
#             the_model = model_choice(work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth',work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth')
#
#             fn,ext = os.path.splitext(the_model)
#             out_chld = fn.split('_cm')[1]
#             #print 'building cm at ' + nd.name + ' using ' + nd.get_children()[0].name
#             os.system('/opt/bin/cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + the_model + '.sth\" ')
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + out_chld + '.sth\n')
#
#             nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#
#             return nd.arr[gene]['model']
#
#         elif not mod1 is None and mod2 is None: #only child1 have model for this gene
#
# #             if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
# #                 # # alignment based on first child model
# #                 print "1"
# #                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '
# #                 #print 'cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth '
# #                 os.system('/opt/bin/cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
# #                 os.system('/opt/bin/cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
# #
# #             else:  # has grand children >> use mapali
# #                 print "2"
# #                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' with mapali'
# #                 print nd.get_children()[0].name, "alignment with best score", findSTH(nd.get_children()[0].name)
# #                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
# #                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
# #
# #             os.system('/opt/bin/cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth\" ')
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth\n')
#
# #             nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#             nd.arr[gene]['model'] = mod1
#
#             return nd.arr[gene]['model']
#
#         elif mod1 is None and not mod2 is None: #only child2 have model for this gene
#
# #              if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
# #                  # # alignment based on second child model
# #                  print "3"
# #                  print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
# #                  os.system('/opt/bin/cmalign \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
# #                  os.system('/opt/bin/cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
# #
# #              else:  # has grand children >> use mapali
# #                  print "4"
# #                  print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
# #                  print findSTH(nd.get_children()[1].name)
# #                  os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
# #                  os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
# #
# #
# #             os.system('/opt/bin/cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth\" ')
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth\n')
#
# #             nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#             nd.arr[gene]['model'] = mod2
#
#             return nd.arr[gene]['model']
#         else:   # both children have no model for this gene
#             print "Oh shit!"
#

# def remolding_in_tree(t):
#
#     tmp = []
#     ################################################################# 13 March 2014 - include the case where a sister node is leaf ##################    #done
#     ################################################################# 14 March 2014 - include the case where remolding occurs between leafs  ################## done
#     ################################################################# 19 March 2014 - include the score of the best sequence that a model can give  ##################    #done
#     ################################################################# 19 March 2014 - include the score of the alignment with the root node  ##################    done
#
#     global taxidmap_file
#     for nd in t.traverse():
#         #if not nd.is_leaf() and not nd.is_root():
#         scrs_nd = {}
#         if not nd.is_root():
#
#             scrs_sis = {}
#             #print nd.get_sisters()
#             sis=nd.get_sisters()[0]
#             for g1 in nd.arr:
#
#                 for g2 in sis.arr:
#                     if g1 in ['trnL1','trnL2'] and g2 in ['trnL1','trnL2']:
#
#
#                         #if nd.name in tmp and sis.name in tmp:
#                         #    continue
# #                         cmcomp_res=os.popen('/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/CMCompare '+nd.arr[g1]['model']+' '+nd.arr[g1]['model']).read()
# #                         cmcomp_res=cmcomp_res.strip().split(' ')
# #                         cmcomp_res = filter(None, cmcomp_res)
# #
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+sis.name+"_"+g1+"_"+g2+'.fas'):
#
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+sis.name+"_"+g1+"_"+g2+'.fas',"w")
#                             #f.write("> "+nd.name+"_"+g1+"\n"+nd.arr[g1]['seq']+"\n")
#                             #f.write("> "+nd.name+"_"+g2+"\n"+nd.arr[g2]['seq']+"\n")
#                             #f.write(nd.arr[g1]['seq']+"\n")
#
#                             f.write(sis.arr[g2]['seq']+"\n")
#
# #                             f.write("> Golden_seq \n "+cmcomp_res[4])           ## include the golden sequence inside the plots
#                             f.close()
#
#                         # aligning with model of current node (g1)
#                         #print nd.name
#                         os.system('/opt/bin/cmalign \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+sis.name+"_"+g1+"_"+g2+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+sis.name+"_"+g1+"_"+g2+ '_cm_'+nd.name+"_"+g1 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+sis.name+'_'+g1+'_'+g2+ '_cm_'+nd.name+'_'+g1 + '.sth \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+sis.name+'_'+g1+'_'+g2 + '.fas\" ')
#
#
#                         #max_score_model = float(cmcomp_res[2])
#
#                         ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                         file = open(work_dir+'remolding/score_files/' + nd.name+"_"+sis.name+"_"+g1+"_"+g2+'_cm_'+nd.name+"_"+g1 + '.sth', 'r')
#                         score1 = 0
#
#                         for line in file:
#                             if not line.startswith("#"):
#                                 temp = line.split()
#
#                                 # gene model key
#                                 if not nd.name+"_"+g1 in scrs_nd:
#                                     scrs_nd[nd.name+"_"+g1] = {}
#
#                                 # sister gene key            ### probably not needed
#                                 #if not sis.name+"_"+g2 in scrs_nd[nd.name+"_"+g1]:
#                                 #    scrs_nd[nd.name+"_"+g1][sis.name+"_"+g2] = {}
#
#                                 # leaf node key which is included in the alignment
#                                 #if not str(temp[1]) in scrs_nd[nd.name+"_"+g1][sis.name+"_"+g2]:
#                                 #    scrs_nd[nd.name+"_"+g1][sis.name+"_"+g2][temp[1]] = []
#
#                                 #scrs_nd[nd.name+"_"+g1][sis.name+"_"+g2][temp[1]].append(str(temp[6]))
#                                 #### end sister gene key test
#                                 if not str(temp[1]) in scrs_nd[nd.name+"_"+g1]:
#                                     scrs_nd[nd.name+"_"+g1][temp[1]] = str(temp[6])
#                                 #scrs_nd[nd.name+"_"+g1][temp[1]]=str(temp[6])
#
#
#                                 #score1 += float(temp[6])
#                         file.close()
#                         #nd.add_feature('scores_'+g1,scrs_nd)
#
#                  ####     in species comparison
#                 for g3 in nd.arr:
#                     if g3 in ['trnL1','trnL2'] and g1 in ['trnL1','trnL2']:
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+"_"+g3+'.fas'):
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+"_"+g3+'.fas',"w")
#
#                             f.write(nd.arr[g1]['seq']+"\n")
#                             f.write(nd.arr[g3]['seq']+"\n")
#                             f.close()
#                         #print nd.name, g1, g3,"\n", nd.arr[g1]['seq'], nd.arr[g3]
#                         os.system('/opt/bin/cmalign \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+"_"+g3+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+"_"+g3+ '_cm_'+nd.name+"_"+g1 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+'_'+g3+ '_cm_'+nd.name+'_'+g1 + '.sth \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1+'_'+g3 + '.fas\" ')
#
#
#                         file = open(work_dir+'remolding/score_files/' + nd.name+"_"+g1+"_"+g3+'_cm_'+nd.name+"_"+g1 + '.sth', 'r')
#                         score1 = 0
#
#                         for line in file:
#                             if not line.startswith("#"):
#                                 temp = line.split()
#
#                                 # gene model key
#                                 if not nd.name+"_"+g1 in scrs_nd:
#                                     scrs_nd[nd.name+"_"+g1] = {}
#
#                                 if not str(temp[1]) in scrs_nd[nd.name+"_"+g1]:
#                                     scrs_nd[nd.name+"_"+g1][temp[1]] = str(temp[6])
#                                 #s
#                         file.close()
#                 nd.add_feature('scores',scrs_nd)
#
#
#         ####        alignment with root node model
#         else:
#             print "root "+nd.name
#             for g4 in nd.arr:
#                 for g5 in nd.arr:
#                     if g4 in ['trnL1','trnL2'] and g5 in ['trnL1','trnL2']:
#
# #                         cmcomp_res=os.popen('/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/CMCompare '+nd.arr[g4]['model']+' '+nd.arr[g4]['model']).read()
# #                         cmcomp_res=cmcomp_res.strip().split(' ')
# #                         cmcomp_res = filter(None, cmcomp_res)
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g4+"_"+g5+'.fas'):
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+g4+"_"+g5+'.fas',"w")
#
#                             f.write(nd.arr[g4]['seq']+"\n")
#                             f.write(nd.arr[g5]['seq']+"\n")
#                             #f.write("> Golden_seq \n "+cmcomp_res[4])
#                             f.close()
#                     # aligning with model of sister node (g2)
#                     #print nd.name
#                         os.system('/opt/bin/cmalign \"' + nd.arr[g4]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + g4+'_'+g5 + '.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g4+"_"+g5+ '_cm_'+nd.name+"_"+g4 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+"_"+g4+"_"+g5+ '_cm_'+nd.name+"_"+g4 + '.sth \"' + nd.arr[g4]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + g4+'_'+g5 + '.fas\" ')
#                         file = open(work_dir+'remolding/score_files/' + nd.name+"_"+g4+"_"+g5+'_cm_'+nd.name+"_"+g4 + '.sth', 'r')
#                         score1 = 0
#
#                         for line in file:
#                             if not line.startswith("#"):
#                                 temp = line.split()
#
#                                 # gene model key
#                                 if not nd.name+"_"+g4 in scrs_nd:
#                                     scrs_nd[nd.name+"_"+g4] = {}
#
#                                 if not str(temp[1]) in scrs_nd[nd.name+"_"+g4]:
#                                     scrs_nd[nd.name+"_"+g4][temp[1]] = str(temp[6])
#                                 #s
#                         file.close()
#             nd.add_feature('scores',scrs_nd)
# #
# #
# #                     ##  add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g2)
# #                     file = open(work_dir+'remolding/score_files/' + nd.name+"_"+sis.name+"_"+g1+"_"+g2+'_cm_'+sis.name+"_"+g2 + '.sth', 'r')
# #                     score2 = 0
# #                     for line in file:
# #                         if not line.startswith("#"):
# #                             temp = line.split()
# #
# #                             if not sis.name+"_"+g2 in scrs_sis:
# #                                 scrs_sis[sis.name+"_"+g2] = {}
# #
# #                             if not nd.name+"_"+g1 in scrs_sis[sis.name+"_"+g2]:
# #                                 scrs_sis[sis.name+"_"+g2][nd.name+"_"+g1] = {}
# #
# #
# #                             if not str(temp[1])in scrs_sis[sis.name+"_"+g2][nd.name+"_"+g1]:
# #                                 scrs_sis[sis.name+"_"+g2][nd.name+"_"+g1][temp[1]] = []
# #
# #                             scrs_sis[sis.name+"_"+g2][nd.name+"_"+g1][temp[1]].append(str(temp[6]))
# #                             #score2 += float(temp[6])
# #                     file.close()
# #                     sis.add_feature('scores_'+g2,scrs_sis)
#
#
#                     #tmp.append(nd.name)
#                     #tmp.append(sis.name)
#
#                     #with open(work_dir+"remolding/bit_scores_internal.txt","a") as remf:
#
#                     #    remf.write(nd.name+ " "+"    "+sis.name+"    "+g1+" "+g2+"  "+str(score1)+"\n")
#     return t

#

    # return nd.arr[gene]['seq']








# def remolding_in_tree(t, rem_dict):
#
#     global taxidmap_file
#
#     for nd in t.traverse("postorder"):
#         scrs = {}
#         if not nd.is_root():
#
#             sis=nd.get_sisters()[0]
#
#             if nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, nd.name) in rem_dict and not get_NC(taxidmap_file, sis.name) in rem_dict:     ### both are leafs but only nd have remolding candidate
#                 print "1"
#                 for g1 in nd.arr:
#
#                     if g1 in rem_dict[get_NC(taxidmap_file, nd.name)]:        ### if tested gene is a remolding candidate
#
#                         for g2 in sis.arr:
#
#
#                             if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas'):
#
#                                 f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas',"w")
#
#                                 f.write(nd.arr[g1]['seq']+"\n")
#
#                                 f.close()
#
#                             # aligning with model of current node (g1)
#
#                             os.system('/opt/bin/cmalign \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+ '_cm_'+sis.name+"_"+g2 + '.sth ')
#                             os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+ '_cm_'+sis.name+'_'+g2 + '.sth \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1 + '.fas\" ')
#
#                             ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                             node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + nd.name+"_"+g1+'_cm_'+sis.name+"_"+g2 + '.sth')
#                             #            gene model score
#
#                             if not node_gene in scrs:
#                                 scrs[node_gene] = {}
#
#                             if not nd.name+"_"+g1 in scrs[node_gene]:
#                                 scrs[node_gene][nd.name+"_"+g1] = scr
#
#                             #print "1",max(d[nd.name+"_"+g1], key=lambda x: d[nd.name+"_"+g1][x])    ### will give me the tRNA of the nd that have the highest score based on the alignment with the sister model.
#
#                             #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ case1: ", scrs
#                             ## missing is to compute the aff_seq for the remolded tRNAs
#                             ## missing is to compute the model for the common ancestor of these two nodes
#                     scrs.clear()
#             elif nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, sis.name) in rem_dict and not get_NC(taxidmap_file, nd.name) in rem_dict:     ### both leafs but only sis have remolding candidate
#                 print "2"
#                 for g1 in nd.arr:
#
#                     for g2 in sis.arr:
#                         if g2 in rem_dict[get_NC(taxidmap_file, sis.name)]:        ### if tested gene is a remolding candidate
#
#
#                             if not os.path.isfile(work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas'):
#
#                                 f=open(work_dir+'fasta_files/' +sis.name+"_"+g2+'.fas',"w")
#
#                                 f.write(sis.arr[g2]['seq']+"\n")
#
#                                 f.close()
#
#                             # aligning with model of current node (g1)
#
#                             os.system('/opt/bin/cmalign \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas\" > '+work_dir+'stockholm_files/' +sis.name+"_"+g2+ '_cm_'+nd.name+"_"+g1 + '.sth ')
#                             os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+g2+ '_cm_'+nd.name+'_'+g1 + '.sth \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' +sis.name+'_'+g2 + '.fas\" ')
#
#                             ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                             node_gene,scr = if_remolded(work_dir+'remolding/score_files/' +sis.name+"_"+g2+'_cm_'+nd.name+"_"+g1 + '.sth')
#                             #            gene model score
#
#                             if not node_gene in scrs:
#                                 scrs[node_gene] = {}
#
#                             if not sis.name+"_"+g2 in scrs[node_gene]:
#                                 scrs[node_gene][sis.name+"_"+g2] = scr
#                             # the output
#                             #print "2",max(d[sis.name+"_"+g2], key=lambda x: d[sis.name+"_"+g2][x])    ### will give me the tRNA of the nd that have the highest score based on the alignment with the sister model.
#
#                             ## missing is to compute the aff_seq for the remolded tRNAs
#                             ## missing is to compute the model for the common ancestor of these two nodes
#                 scrs.clear()
#             elif nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, nd.name) in rem_dict and get_NC(taxidmap_file, sis.name) in rem_dict:        ### both leafs and both have remolding candidate
#
#                 for g1 in nd.arr:
#
#                     #if g1 in rem_dict[get_NC(taxidmap_file, nd.name)]:
#                         #print "3",nd.name, sis.name
#
#                     for g2 in sis.arr:
#                         #if g2 in rem_dict[get_NC(taxidmap_file, sis.name)]:        ### if tested gene is a remolding candidate
#                             #print "3",nd.name, sis.name
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas'):
#
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas',"w")
#
#                             f.write(nd.arr[g1]['seq']+"\n")
#
#                             f.close()
#
#                         # aligning with model of current node (g1)
#
#                         os.system('/opt/bin/cmalign \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+ '_cm_'+sis.name+"_"+g2 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+ '_cm_'+sis.name+'_'+g2 + '.sth \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1+ '.fas\" ')
#
#                         ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + nd.name+"_"+g1+'_cm_'+sis.name+"_"+g2 + '.sth')
#                         #            gene model score
#     #### the correct one and its working
#
#                         if not node_gene in scrs:
#                             scrs[node_gene] = {}
#
#                         if not sis.name+"_"+g2 in scrs[node_gene]:
#                             scrs[node_gene][sis.name+"_"+g2] = scr
#     ## scrs contains the score of each gene based on each model of the sister node (e.g : {"Gene_X":{"Model_Y'":50,"Model_X'":60}})
#
#                     print "case 3: ", scrs
#                     for aligned_gene in scrs:
#                         #print md.split("_")[1], max(scrs[md], key=lambda x: scrs[md][x]).split("_")[1]
#                         if aligned_gene.split("_")[1] == max(scrs[aligned_gene], key=lambda x: scrs[aligned_gene][x]).split("_")[1]:           ### both are remolded, no difference in score
#                             gn = aligned_gene.split("_")[1]
#                             ancestor = t.get_common_ancestor(nd,sis)
#                             ancestor.arr[gn]['seq'] = aff_seq(nd,sis,gn)
#                             ffile = open(work_dir+"fasta_files/"+ancestor.name+"_"+gn+".fas","w")
#                             ffile.write(ancestor.arr[gn]['seq'])
#                             ffile.close()
#                             ancestor.arr[gn]['model'] = computeModels(ancestor, gn)
#
#
#                     scrs.clear()
# #
#
#             #elif not nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, sis.name) in rem_dict:     ### only sis is leaf and has remolding candidate
#                 ## do something
#
#             #elif nd.is_leaf() and not sis.is_leaf() and get_NC(taxidmap_file, nd.name) in rem_dict:     ### only nd is leaf and has remolding candidate
#                 ## do something
#
#             #elif not nd.is_leaf() and sis.is_leaf() and not get_NC(taxidmap_file, sis.name) in rem_dict:     ### only sis is leaf and doesnt have remolding candidate
#                 ## do something
#
#             #elif nd.is_leaf() and not sis.is_leaf() and not get_NC(taxidmap_file, nd.name) in rem_dict:     ### only nd is leaf and doesnt have remolding candidate
#                 ## do something
#
#             elif not nd.is_leaf() and not sis.is_leaf() and nd.arr and sis.arr:                                                           #### both are not leafs
#                 #print "case 4", nd.arr, sis.arr
#                 for g1 in nd.arr:
#
#                     for g2 in sis.arr:
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas'):
#
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas',"w")
#
#                             f.write(nd.arr[g1]['seq']+"\n")
#
#                             f.close()
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas'):
#
#                             f=open(work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas',"w")
#
#                             f.write(sis.arr[g2]['seq']+"\n")
#
#                             f.close()
#                         # aligning with model of current node (g1)
#
#                         os.system('/opt/bin/cmalign \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+ '_cm_'+sis.name+"_"+g2 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+ '_cm_'+sis.name+'_'+g2 + '.sth \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1+ '.fas\" ')
#
#
#
#                         os.system('/opt/bin/cmalign \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas\" > '+work_dir+'stockholm_files/' + sis.name+"_"+g2+ '_cm_'+nd.name+"_"+g1 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+g2+ '_cm_'+nd.name+'_'+g1 + '.sth \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+'_'+g2+ '.fas\" ')
#
#
#                         ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#                         scr_nd = alignment_score_internals(work_dir+'remolding/score_files/' + sis.name+"_"+g2+'_cm_'+nd.name+"_"+g1 + '.sth')
#
#                         scr_sis = alignment_score_internals(work_dir+'remolding/score_files/' + nd.name+"_"+g1+'_cm_'+sis.name+"_"+g2 + '.sth')
#
#
#                         if not sis.name+"_"+g2 in scrs:
#                             scrs[sis.name+"_"+g2] = {}
#
#                         if not nd.name+"_"+g1 in scrs[sis.name+"_"+g2]:
#                             scrs[sis.name+"_"+g2][nd.name+"_"+g1] = scr_nd
#
#
#                         if not nd.name+"_"+g1 in scrs:
#                             scrs[nd.name+"_"+g1] = {}
#
#                         if not sis.name+"_"+g2 in scrs[nd.name+"_"+g1]:
#                             scrs[nd.name+"_"+g1][sis.name+"_"+g2] = scr_sis
#
#                     for aligned_gene in scrs:
#                     ## scrs contains the score of each gene based on each model of the sister node (e.g : {"Gene_X":{"Model_Y'":50,"Model_X'":60}})
#                         if aligned_gene.split("_")[1] == max(scrs[aligned_gene], key=lambda x: scrs[aligned_gene][x]).split("_")[1]:           ### both are remolded, no difference in score
#                             gn = aligned_gene.split("_")[1]
#                             ancestor = t.get_common_ancestor(nd,sis)
#                             ancestor.arr[gn]['seq'] = aff_seq(nd,sis,gn)
#                             ffile = open(work_dir+"fasta_files/"+ancestor.name+"_"+gn+".fas","w")
#                             ffile.write(ancestor.arr[gn]['seq'])
#                             ffile.close()
#                             ancestor.arr[gn]['model'] = computeModels(ancestor, gn)
#                         else:
#                             print aligned_gene.split("_"), "is remolded from", max(scrs[aligned_gene], key=lambda x: scrs[aligned_gene][x]).split("_")
#                     print "INT",scrs
#                     #scrs.clear()
# #                 for md in scrs:
# #                     print md, max(scrs[md], key=lambda x: scrs[md][x])
# #
#             else:
#                 continue
#                 print "Daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaamnn!!!"
#
#
#     #return t


# def computeModels(nd, gene):
#     if nd.is_leaf() and gene in nd.arr.keys():
#         mod = nd.arr[gene]['model']
#         return mod
#     #else:
#     #    return None
#     if not nd.is_leaf():
#         print "112",nd.name, nd.get_children()[0].name,nd.get_children()[1].name
#         mod1, mod2 = computeModels(nd.get_children()[0], gene), computeModels(nd.get_children()[1], gene)
#         if not mod1 is None and not mod2 is None:   # both children have models for this gene
#             if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
#                 # # alignment based on first child model
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name+"_"+gene + ' without mapali '
#
#                 os.system('/opt/bin/cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
#                 os.system('/opt/bin/cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name+"_"+gene + ' with mapali'
#
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth ')
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[0].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#             if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
#                 # # alignment based on second child model
#                 print "3"
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name+"_"+gene + ' without mapali'
#                 os.system('/opt/bin/cmalign \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
#                 os.system('/opt/bin/cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name+"_"+gene + ' with mapali'
#
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" > '+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth ')
#                 os.system('/opt/bin/cmalign --mapali \"' + findSTH(nd.get_children()[1].name) + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '' + gene + '.fas\" ')
#
#
#             the_model = model_choice(work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth',work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth')
#
#             fn,ext = os.path.splitext(the_model)
#             out_chld = fn.split('_cm')[1]
#             #print 'building cm at ' + nd.name + ' using ' + nd.get_children()[0].name
#             os.system('/opt/bin/cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + the_model + '.sth\" ')
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + out_chld + '.sth\n')
#
#             nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#
#             return nd.arr[gene]['model']
#
#         elif not mod1 is None and mod2 is None: #only child1 have model for this gene
#
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[0].name + '.sth\n')
#
#
#             nd.arr[gene]['model'] = mod1
#
#             return nd.arr[gene]['model']
#
#         elif mod1 is None and not mod2 is None: #only child2 have model for this gene
#
#             with open('ndal.tmp', 'a') as file:
#                 file.write(nd.name +' '+ work_dir+'stockholm_files/testing/' + nd.name + '_' + gene + '_cm' + nd.get_children()[1].name + '.sth\n')
#
#             nd.arr[gene]['model'] = mod2
#
#             return nd.arr[gene]['model']
#
#         else:   # both children have no model for this gene
#             print "Oh shit!"
#

# def remolding_in_tree(t, rem_dict):
#
#     global taxidmap_file
#
#     for nd in t.traverse(strategy= "postorder"):
#         scrs = {}
#         if not nd.is_root():
#
#             sis=nd.get_sisters()[0]
#
#             if nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, nd.name) in rem_dict and not get_NC(taxidmap_file, sis.name) in rem_dict:     ### both are leafs but only nd have remolding candidate
#                 print "1"
#                 for g1 in nd.arr:
#
#                     if g1 in rem_dict[get_NC(taxidmap_file, nd.name)]:        ### if tested gene is a remolding candidate
#
#                         for g2 in sis.arr:
#
#
#                             if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas'):
#
#                                 f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas',"w")
#
#                                 f.write(nd.arr[g1]['seq']+"\n")
#
#                                 f.close()
#
#                             # aligning with model of current node (g1)
#
#                             os.system('/opt/bin/cmalign \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+ '_cm_'+sis.name+"_"+g2 + '.sth ')
#                             os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+ '_cm_'+sis.name+'_'+g2 + '.sth \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1 + '.fas\" ')
#
#                             ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                             node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + nd.name+"_"+g1+'_cm_'+sis.name+"_"+g2 + '.sth')
#                             #            gene model score
#
#                             if not node_gene in scrs:
#                                 scrs[node_gene] = {}
#
#                             if not nd.name+"_"+g1 in scrs[node_gene]:
#                                 scrs[node_gene][nd.name+"_"+g1] = scr
#
#                             #print "1",max(d[nd.name+"_"+g1], key=lambda x: d[nd.name+"_"+g1][x])    ### will give me the tRNA of the nd that have the highest score based on the alignment with the sister model.
#
#                             #print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ case1: ", scrs
#                             ## missing is to compute the aff_seq for the remolded tRNAs
#                             ## missing is to compute the model for the common ancestor of these two nodes
#                     scrs.clear()
#             elif nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, sis.name) in rem_dict and not get_NC(taxidmap_file, nd.name) in rem_dict:     ### both leafs but only sis have remolding candidate
#                 print "2"
#                 for g1 in nd.arr:
#
#                     for g2 in sis.arr:
#                         if g2 in rem_dict[get_NC(taxidmap_file, sis.name)]:        ### if tested gene is a remolding candidate
#
#
#                             if not os.path.isfile(work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas'):
#
#                                 f=open(work_dir+'fasta_files/' +sis.name+"_"+g2+'.fas',"w")
#
#                                 f.write(sis.arr[g2]['seq']+"\n")
#
#                                 f.close()
#
#                             # aligning with model of current node (g1)
#
#                             os.system('/opt/bin/cmalign \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+g2+'.fas\" > '+work_dir+'stockholm_files/' +sis.name+"_"+g2+ '_cm_'+nd.name+"_"+g1 + '.sth ')
#                             os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+g2+ '_cm_'+nd.name+'_'+g1 + '.sth \"' + nd.arr[g1]['model'] + '\" \"'+work_dir+'fasta_files/' +sis.name+'_'+g2 + '.fas\" ')
#
#                             ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                             node_gene,scr = if_remolded(work_dir+'remolding/score_files/' +sis.name+"_"+g2+'_cm_'+nd.name+"_"+g1 + '.sth')
#                             #            gene model score
#
#                             if not node_gene in scrs:
#                                 scrs[node_gene] = {}
#
#                             if not sis.name+"_"+g2 in scrs[node_gene]:
#                                 scrs[node_gene][sis.name+"_"+g2] = scr
#                             # the output
#                             #print "2",max(d[sis.name+"_"+g2], key=lambda x: d[sis.name+"_"+g2][x])    ### will give me the tRNA of the nd that have the highest score based on the alignment with the sister model.
#
#                             ## missing is to compute the aff_seq for the remolded tRNAs
#                             ## missing is to compute the model for the common ancestor of these two nodes
#                 scrs.clear()
#             elif nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, nd.name) in rem_dict and get_NC(taxidmap_file, sis.name) in rem_dict:        ### both leafs and both have remolding candidate
#
#                 for g1 in nd.arr:
#
#                     #if g1 in rem_dict[get_NC(taxidmap_file, nd.name)]:
#                         #print "3",nd.name, sis.name
#
#                     for g2 in sis.arr:
#                         #if g2 in rem_dict[get_NC(taxidmap_file, sis.name)]:        ### if tested gene is a remolding candidate
#                             #print "3",nd.name, sis.name
#
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas'):
#
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas',"w")
#
#                             f.write(nd.arr[g1]['seq']+"\n")
#
#                             f.close()
#
#                         # aligning with model of current node (g1)
#
#                         os.system('/opt/bin/cmalign \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+ '_cm_'+sis.name+"_"+g2 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+ '_cm_'+sis.name+'_'+g2 + '.sth \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1+ '.fas\" ')
#
#                         ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + nd.name+"_"+g1+'_cm_'+sis.name+"_"+g2 + '.sth')
#                         #            gene model score
#     #### the correct one and its working
#
#                         if not node_gene in scrs:
#                             scrs[node_gene] = {}
#
#                         if not sis.name+"_"+g2 in scrs[node_gene]:
#                             scrs[node_gene][sis.name+"_"+g2] = scr
#     ## scrs contains the score of each gene based on each model of the sister node (e.g : {"Gene_X":{"Model_Y'":50,"Model_X'":60}})
#
#                     print "case 3: ", scrs
#                     for aligned_gene in scrs:
#                         #print md.split("_")[1], max(scrs[md], key=lambda x: scrs[md][x]).split("_")[1]
#                         if aligned_gene.split("_")[1] == max(scrs[aligned_gene], key=lambda x: scrs[aligned_gene][x]).split("_")[1]:           ### both are remolded, no difference in score
#                             gn = aligned_gene.split("_")[1]
#                             ancestor = t.get_common_ancestor(nd,sis)
#                             ancestor.arr[gn]['seq'] = aff_seq(nd,sis,gn)
#
#                             ancestor.arr[gn]['model'] = computeModels(ancestor, gn)
#                             #print "$$$$------------", ancestor.arr[gn]['model'],ancestor.arr[gn]['seq']
#
#                     scrs.clear()
# #                             ancestor.arr[g1]['seq'],ancestor.arr[g2]['seq'] = aff_seq(nd,sis,g1),aff_seq(nd,sis,g1)
# #                             ancestor.arr[g1]['model'],ancestor.arr[g2]['model'] = computeModels(nd, g1),computeModels(sis, g2)
# #                             print "111",ancestor.name, ancestor.arr[g1]['seq'], ancestor.arr[g1]['model']
#
#             #elif not nd.is_leaf() and sis.is_leaf() and get_NC(taxidmap_file, sis.name) in rem_dict:     ### only sis is leaf and has remolding candidate
#                 ## do something
#
#             #elif nd.is_leaf() and not sis.is_leaf() and get_NC(taxidmap_file, nd.name) in rem_dict:     ### only nd is leaf and has remolding candidate
#                 ## do something
#
#             #elif not nd.is_leaf() and sis.is_leaf() and not get_NC(taxidmap_file, sis.name) in rem_dict:     ### only sis is leaf and doesnt have remolding candidate
#                 ## do something
#
#             #elif nd.is_leaf() and not sis.is_leaf() and not get_NC(taxidmap_file, nd.name) in rem_dict:     ### only nd is leaf and doesnt have remolding candidate
#                 ## do something
#
#             elif not nd.is_leaf() and not sis.is_leaf():                                                           #### both are not leafs
#
#                 for g1 in nd.arr:
#
#
#                     #if g1 in rem_dict[get_NC(taxidmap_file, nd.name)]:
#                         #print "3",nd.name, sis.name
#
#                     for g2 in sis.arr:
#                         #if g2 in rem_dict[get_NC(taxidmap_file, sis.name)]:        ### if tested gene is a remolding candidate
#
#
#                         #print "WWWWWWWW",   nd.name, sis.name, nd.arr['trnL2']['model'],sis.arr['trnL2']['model']
#                         if not os.path.isfile(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas'):
#
#                             f=open(work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas',"w")
#
#                             f.write(nd.arr[g1]['seq']+"\n")
#
#                             f.close()
#
#                         # aligning with model of current node (g1)
#                         #print "asdasdadasd",nd.arr[g1]['seq'], sis.arr[g2]['model']
#                         os.system('/opt/bin/cmalign \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+"_"+g1+'.fas\" > '+work_dir+'stockholm_files/' + nd.name+"_"+g1+ '_cm_'+sis.name+"_"+g2 + '.sth ')
#                         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + nd.name+'_'+g1+ '_cm_'+sis.name+'_'+g2 + '.sth \"' + sis.arr[g2]['model'] + '\" \"'+work_dir+'fasta_files/' + nd.name+'_'+g1+ '.fas\" ')
#
#                         ## add score to the node (of all children of the current and sister nodes) where the model came from as a feature (in this case from model of g1)
#
#                         scr = alignment_score_internals(work_dir+'remolding/score_files/' + nd.name+"_"+g1+'_cm_'+sis.name+"_"+g2 + '.sth')
#
#                         #            gene model score
# #### the correct one and its working
#                         #print "/////",nd.name, sis.name, scr
#                         if not nd.name+"_"+g1 in scrs:
#                             scrs[nd.name+"_"+g1] = {}
#
#                         if not sis.name+"_"+g2 in scrs[nd.name+"_"+g1]:
#                             scrs[nd.name+"_"+g1][sis.name+"_"+g2] = scr
#                     print "INT",scrs
#                     scrs.clear()
# #                 for md in scrs:
# #                     print md, max(scrs[md], key=lambda x: scrs[md][x])
# #
#             else:
#                 print "Daaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaamnn!!!"
#
#
#     #return t
#
# def do_alignments(nd,arr1,arr2,rem_dict):
#
#     '''
#     For each child of nd (if its a leaf and is a remolding candidate) we have rows inside the rem_dict dict.
#     e.g:
#         chld_g1 chld_g2
#         sis_g1 sis_g2
#
#     for each of them, i should perform the 4 following alignments:
#         B with mB_sis, B with mA_sis, A with mB_sis and A with mA_sis
#
#     '''
#     trna_log = open(work_dir+"result_log_file.txt","a")
#
#     chld = nd.get_children()[0]
#     sis = nd.get_children()[1]
#     scrs = {}
#
#     chld_g1 = arr1[0]
#     chld_g2 = arr1[1]
#     sis_g1 = arr2[0]
#     sis_g2 = arr2[1]
#
#
#
#     if not os.path.isfile(work_dir+'fasta_files/' + chld.name+"_"+chld_g1+'.fas'):
#
#        f=open(work_dir+'fasta_files/' + chld.name+"_"+chld_g1+'.fas',"w")
#        f.write(chld.arr[chld_g1]['seq']+"\n")
#        f.close()
#
#     ### chld_g1 with model of chld_g1 of the sister
#
#     if chld_g1 in sis.arr:
#         scr=0                        ### test if the sister have g1, if yes align g1 with g1 of the sister (e.g B with mB_sis)
#         os.system('/opt/bin/cmalign \"' + sis.arr[chld_g1]['model'] + '\" \"'+work_dir+'fasta_files/' + chld.name+"_"+chld_g1+'.fas\" > '+work_dir+'stockholm_files/' +chld.name+"_"+chld_g1+ '_cm_'+sis.name+"_"+chld_g1 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + chld.name+'_'+chld_g1+ '_cm_'+sis.name+'_'+chld_g1 + '.sth \"' + sis.arr[chld_g1]['model'] + '\" \"'+work_dir+'fasta_files/' +chld.name+'_'+chld_g1 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + chld.name+'_'+chld_g1+ '_cm_'+sis.name+'_'+chld_g1 + '.sth')
#
#
#         if not chld.name+"_"+chld_g1 in scrs:
#             scrs[chld.name+"_"+chld_g1] = {}
#         if not sis.name+'_'+chld_g1 in scrs[chld.name+"_"+chld_g1]:
#             scrs[chld.name+"_"+chld_g1][sis.name+"_"+chld_g1] = scr
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, sis.name)+" "+chld_g1+"\n")
#         print "Sister node "+ get_NC(taxidmap_file, sis.name) +" is missing tRNA "+ chld_g1
#
#     ### chld_g1 with model of chld_g2 of the sister
#     if chld_g2 in sis.arr:
#         scr=0
#         os.system('/opt/bin/cmalign \"' + sis.arr[chld_g2]['model'] + '\" \"'+work_dir+'fasta_files/' + chld.name+"_"+chld_g1+'.fas\" > '+work_dir+'stockholm_files/' +chld.name+"_"+chld_g1+ '_cm_'+sis.name+"_"+chld_g2 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + chld.name+'_'+chld_g1+ '_cm_'+sis.name+'_'+chld_g2 + '.sth \"' + sis.arr[chld_g2]['model'] + '\" \"'+work_dir+'fasta_files/' +chld.name+'_'+chld_g1 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + chld.name+'_'+chld_g1+ '_cm_'+sis.name+'_'+chld_g2 + '.sth')
#
#
#         if not chld.name+"_"+chld_g1 in scrs:
#             scrs[chld.name+"_"+chld_g1] = {}
#         if not sis.name+"_"+chld_g2 in scrs[chld.name+"_"+chld_g1]:
#             scrs[chld.name+"_"+chld_g1][sis.name+"_"+chld_g2] = scr
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, sis.name)+" "+chld_g2+"\n")
#         print "Sister node "+ get_NC(taxidmap_file, sis.name) +" is missing tRNA "+ chld_g2
#
#
#     ##### same procedure, but with the switched remolding candidates. IMPORTANT ################################ IMPORTANT
#
#     if not os.path.isfile(work_dir+'fasta_files/' + chld.name+"_"+chld_g2+'.fas'):
#
#        f=open(work_dir+'fasta_files/' + chld.name+"_"+chld_g2+'.fas',"w")
#        f.write(chld.arr[chld_g2]['seq']+"\n")
#        f.close()
#
#
#     ### chld_g2 with model of chld_g2 of the sister
#
#
#     if chld_g2 in sis.arr:
#         scr=0                       ### test if the sister have g2
#         os.system('/opt/bin/cmalign \"' + sis.arr[chld_g2]['model'] + '\" \"'+work_dir+'fasta_files/' + chld.name+"_"+chld_g2+'.fas\" > '+work_dir+'stockholm_files/' +chld.name+"_"+chld_g2+ '_cm_'+sis.name+"_"+chld_g2 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + chld.name+'_'+chld_g2+ '_cm_'+sis.name+'_'+chld_g2 + '.sth \"' + sis.arr[chld_g2]['model'] + '\" \"'+work_dir+'fasta_files/' +chld.name+'_'+chld_g2 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + chld.name+'_'+chld_g2+ '_cm_'+sis.name+'_'+chld_g2 + '.sth')  ## scr of g1 with g1 of the sister
#
#
#         if not chld.name+"_"+chld_g2 in scrs:
#             scrs[chld.name+"_"+chld_g2] = {}
#         if not sis.name+'_'+chld_g2 in scrs[chld.name+"_"+chld_g2]:
#             scrs[chld.name+"_"+chld_g2][sis.name+"_"+chld_g2] = scr
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, sis.name)+" "+chld_g2+"\n")
#         print "Sister node "+ get_NC(taxidmap_file, sis.name) +" is missing tRNA "+ chld_g2
#
#
#     ### chld_g2 with model of chld_g1 of the sister
#
#     if chld_g1 in sis.arr:
#         scr=0
#         os.system('/opt/bin/cmalign \"' + sis.arr[chld_g1]['model'] + '\" \"'+work_dir+'fasta_files/' + chld.name+"_"+chld_g2+'.fas\" > '+work_dir+'stockholm_files/' +chld.name+"_"+chld_g2+ '_cm_'+sis.name+"_"+chld_g1 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + chld.name+'_'+chld_g2+ '_cm_'+sis.name+'_'+chld_g1 + '.sth \"' + sis.arr[chld_g1]['model'] + '\" \"'+work_dir+'fasta_files/' +chld.name+'_'+chld_g2 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + chld.name+'_'+chld_g2+ '_cm_'+sis.name+'_'+chld_g1 + '.sth')  ## scr of g1 with remdict[g1] (i.e candidate of remolding) from the sister
#
#
#         if not chld.name+"_"+chld_g2 in scrs:
#             scrs[chld.name+"_"+chld_g2] = {}
#         if not sis.name+"_"+chld_g1 in scrs[chld.name+"_"+chld_g2]:
#             scrs[chld.name+"_"+chld_g2][sis.name+"_"+chld_g1] = scr
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, sis.name)+" "+chld_g1+"\n")
#         print "Sister node "+ get_NC(taxidmap_file, sis.name) +" is missing tRNA "+ chld_g1
#
#
#
#     ############################################### direction of remolding in sis_g1     ##############################################################
#
#     if not os.path.isfile(work_dir+'fasta_files/' + sis.name+"_"+sis_g1+'.fas'):
#
#        f=open(work_dir+'fasta_files/' + sis.name+"_"+sis_g1+'.fas',"w")
#        f.write(sis.arr[sis_g1]['seq']+"\n")
#        f.close()
#
#
#
#     ### sis_g1 with model of sis_g1 of the chld
#     if sis_g1 in chld.arr:
#         scr=0
#         os.system('/opt/bin/cmalign \"' + chld.arr[sis_g1]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+sis_g1+'.fas\" > '+work_dir+'stockholm_files/' +sis.name+"_"+sis_g1+ '_cm_'+chld.name+"_"+sis_g1 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+sis_g1+ '_cm_'+chld.name+'_'+sis_g1 + '.sth \"' + chld.arr[sis_g1]['model'] + '\" \"'+work_dir+'fasta_files/' +sis.name+'_'+sis_g1 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + sis.name+'_'+sis_g1+ '_cm_'+chld.name+'_'+sis_g1 + '.sth')  ##
#
#
#         if not sis.name+"_"+sis_g1 in scrs:
#             scrs[sis.name+"_"+sis_g1] = {}
#         if not chld.name+"_"+sis_g1 in scrs[sis.name+"_"+sis_g1]:
#             scrs[sis.name+"_"+sis_g1][chld.name+"_"+sis_g1] = scr
#
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, chld.name)+" "+sis_g1+"\n")
#         print "Chld node "+ get_NC(taxidmap_file, chld.name) +" is missing tRNA "+ sis_g1
#
#
#     ### sis_g1 with model of sis_g2 of the chld
#     if sis_g2 in chld.arr:
#         scr=0
#         os.system('/opt/bin/cmalign \"' + chld.arr[sis_g2]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+sis_g1+'.fas\" > '+work_dir+'stockholm_files/' +sis.name+"_"+sis_g1+ '_cm_'+chld.name+"_"+sis_g2 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+sis_g1+ '_cm_'+chld.name+'_'+sis_g2 + '.sth \"' + chld.arr[sis_g2]['model'] + '\" \"'+work_dir+'fasta_files/' +sis.name+'_'+sis_g1 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + sis.name+'_'+sis_g1+ '_cm_'+chld.name+'_'+sis_g2 + '.sth')  ##
#
#         if not sis.name+"_"+sis_g1 in scrs:
#             scrs[sis.name+"_"+sis_g1] = {}
#         if not chld.name+"_"+sis_g2 in scrs[sis.name+"_"+sis_g1]:
#             scrs[sis.name+"_"+sis_g1][chld.name+"_"+sis_g2] = scr
#
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, chld.name)+" "+sis_g2+"\n")
#         print "Chld node "+ get_NC(taxidmap_file, chld.name) +" is missing tRNA "+ sis_g2
#
#
#
#
#     ##### same procedure, but with the switched remolding candidates. IMPORTANT ################################ IMPORTANT
#
#     if not os.path.isfile(work_dir+'fasta_files/' + sis.name+"_"+sis_g2+'.fas'):
#
#        f=open(work_dir+'fasta_files/' + sis.name+"_"+sis_g2+'.fas',"w")
#        f.write(sis.arr[sis_g2]['seq']+"\n")
#        f.close()
#
#     ### sis_g2 with model of sis_g2 of the chld
#     if sis_g2 in chld.arr:
#         scr=0
#         os.system('/opt/bin/cmalign \"' + chld.arr[sis_g2]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+sis_g2+'.fas\" > '+work_dir+'stockholm_files/' +sis.name+"_"+sis_g2+ '_cm_'+chld.name+"_"+sis_g2 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+sis_g2+ '_cm_'+chld.name+'_'+sis_g2 + '.sth \"' + chld.arr[sis_g2]['model'] + '\" \"'+work_dir+'fasta_files/' +sis.name+'_'+sis_g2 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + sis.name+'_'+sis_g2+ '_cm_'+chld.name+'_'+sis_g2 + '.sth')  ## scr of g1 with g1 of the sister
#
#         if not sis.name+"_"+sis_g2 in scrs:
#             scrs[sis.name+"_"+sis_g2] = {}
#         if not chld.name+"_"+sis_g2 in scrs[sis.name+"_"+sis_g2]:
#             scrs[sis.name+"_"+sis_g2][chld.name+"_"+sis_g2] = scr
#
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, chld.name)+" "+sis_g2+"\n")
#         print "Sister node "+ get_NC(taxidmap_file, chld.name) +" is missing tRNA "+ sis_g2
#
#    ### sis_g2 with model of sis_g1 of the chld
#     if sis_g1 in chld.arr:
#         scr=0
#         os.system('/opt/bin/cmalign \"' + chld.arr[sis_g1]['model'] + '\" \"'+work_dir+'fasta_files/' + sis.name+"_"+sis_g2+'.fas\" > '+work_dir+'stockholm_files/' +sis.name+"_"+sis_g2+ '_cm_'+chld.name+"_"+sis_g1 + '.sth ')
#         os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + sis.name+'_'+sis_g2+ '_cm_'+chld.name+'_'+sis_g1 + '.sth \"' + chld.arr[sis_g1]['model'] + '\" \"'+work_dir+'fasta_files/' +sis.name+'_'+sis_g2 + '.fas\" ')
#
#         node_gene,scr = if_remolded(work_dir+'remolding/score_files/' + sis.name+'_'+sis_g2+ '_cm_'+chld.name+'_'+sis_g1 + '.sth')  ## scr of g1 with remdict[g1] (i.e candidate of remolding) from the sister
#
#
#         if not sis.name+"_"+sis_g2 in scrs:
#             scrs[sis.name+"_"+sis_g2] = {}
#         if chld.name+"_"+sis_g1 in not scrs[sis.name+"_"+sis_g2]:
#             scrs[sis.name+"_"+sis_g2][chld.name+"_"+sis_g1] = scr
#
#
#     else:
#         trna_log.write(get_NC(taxidmap_file, chld.name)+" "+sis_g1+"\n")
#         print "Sister node "+ get_NC(taxidmap_file, chld.name) +" is missing tRNA "+ sis_g1
#
#
#
#
#     return scrs



#
# def remolding_in_tree(t, rem_dict):
#     global taxidmap_file
#
#     #print rem_dict
#
#     remolding_output = open(work_dir+"all_remoldings.txt","w")
#     for nd in t.traverse("postorder"):
#         #scrs = {}
# #         if nd.is_root():
# #             continue
#
#         if not nd.is_leaf():
#             scrs = {}
#             chld = nd.get_children()[0]
#             sis = nd.get_children()[1]
#
#             res = {}
# #             print get_NC(taxidmap_file, chld.name), get_NC(taxidmap_file, sis.name)
#             if not get_NC(taxidmap_file, chld.name) in rem_dict and not get_NC(taxidmap_file, sis.name) in rem_dict:     ### both don't have remolding events
# #                 if not chld.is_leaf() and not sis.is_leaf():
# #                     if chld.remolding and sis.remolding:
# #
# #                         for tup1 in chld.remolding:
# #                             if not chld in res:
# #                                 res[chld] = []
# #                             res[chld].append(do_alignments(chld,tup1))
# #
# #
# #                         for tup2 in sis.remolding:
# #                             if not sis in res:
# #                                 res[sis] = []
# #                             res[sis].append(do_alignments(sis,tup2))
# #
# #                         remolding_direction = []
# #                         for kid in res:     # loop over all kids of nd
# #                             for d in res[kid]:   # loop over all dicts of kid
# #                                 for k in d:
# #                                     if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
# #                                         if not k.split("_")[1] == max(d[k], key=lambda x: d[k][x]).split("_")[1]:
# #
# #                                             remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" "+ get_NC(taxidmap_file, k.split("_")[0])+"\n")
# #                                                                         #node, remolded gene, donor gene
# #                                             remolding_direction.append((kid,k.split("_")[1],max(d[k], key=lambda x: d[k][x]).split("_")[1]))
# #
# #
# #
# #
# #
# #                     print "internals", remolding_direction
#                 continue
#
#             elif get_NC(taxidmap_file, chld.name) in rem_dict and get_NC(taxidmap_file, sis.name) in rem_dict:     ### both have remolding events
#                 remolding_direction = []
#                 same_rem = []
#                 same_rem = list(set(rem_dict[get_NC(taxidmap_file, chld.name)]) & set(rem_dict[get_NC(taxidmap_file, sis.name)])) ## test if they have the same remolding candidates using list intersctions (no intersection -> no same remolding candidates)
#
#                 for l in rem_dict[get_NC(taxidmap_file, chld.name)]:            ### test if the remolding candidates are the same but are swtiched
#                     for ll in rem_dict[get_NC(taxidmap_file, sis.name)]:
#                         if l == tuple(reversed(ll)):
#                             if l not in same_rem and reversed(l) not in same_rem:
#                                 same_rem.append(l)
#
#                 if same_rem:
#                     nd.add_feature('same',same_rem)
#
#                 res={}
#
#                 for arr1 in rem_dict[get_NC(taxidmap_file, chld.name)]:         #### array containing the 2 candidate genes from chld
#                     if arr1 not in same_rem:
#                         if not chld in res:
#                             res[chld] = []
#                         res[chld].append(do_alignments(chld,arr1))
#
#
#                 for arr2 in rem_dict[get_NC(taxidmap_file, sis.name)]:      #### array containing the 2 candidate genes from sis
#                     if arr2 not in same_rem:
#                         if not sis in res:
#                             res[sis] = []
#                         res[sis].append(do_alignments(sis,arr2))
#
#
#                 remolding_direction = []
#                 ## loop through the result array, and get the remolding direction
#                 for kid in res:     # loop over all kids of nd
#                     for d in res[kid]:   # loop over all dicts of kid
#                         for k in d:
#                             if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                                 if not k.split("_")[1] == max(d[k], key=lambda x: d[k][x]).split("_")[1]:
#
#                                     remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" "+ get_NC(taxidmap_file, k.split("_")[0])+"\n")
#
#                                     print k,d[k]
#                                     print kid.name,k.split("_")[1],max(d[k], key=lambda x: d[k][x]).split("_")[1]
#                                     #trnN is remolded from  trnK  in accession NC_007438
#                                     #Assuming N is remolded from K, this means that the sequence of N needs to be appended with K in the ancestor. The append can be done at the chld level.
#
#
#
#                                                                 #node, remolded gene, donor gene
#                                     remolding_direction.append((kid,k.split("_")[1],max(d[k], key=lambda x: d[k][x]).split("_")[1]))
#
#                 #print remolding_direction
#                 #rem_internals = []
#                 if remolding_direction:     ## the case where we couldnt detect the direction of the remolding | ASK Matthias what should we do when we can't detect it.
#
#                     for i in range(len(remolding_direction)):
#
#                         node = remolding_direction[i][0]
#                         remolded_gene = remolding_direction[i][1]
#                         donor_gene = remolding_direction[i][2]
#
#                         node.arr[donor_gene]['seq'] += node.arr[remolded_gene]['seq']
#                         node.arr[donor_gene]['structure'] += node.arr[remolded_gene]['structure']
#
#                         node.arr[remolded_gene]['seq'] = ''
#                         node.arr[remolded_gene]['structure'] = ''
#
#                         nd.arr[donor_gene]['seq'] = aff_seq(chld,sis,donor_gene,donor_gene)
#                         nd.arr[remolded_gene]['seq'] = aff_seq(chld,sis,remolded_gene,remolded_gene)
#
#                         nd.arr[donor_gene]['model'] = computeModels(nd, donor_gene)
#                         nd.arr[remolded_gene]['model'] = computeModels(nd, remolded_gene)
#
#                         #rem_internals.append((nd.name,remolded_gene,donor_gene))
#
#                     #nd.add_feature('remolding',rem_internals)
#
#
#
#
#
#
#             if get_NC(taxidmap_file, chld.name) in rem_dict and not get_NC(taxidmap_file, sis.name) in rem_dict:     ### only chld have remolding candidate
#                 res = []
#                 remolding_direction = []
#                 for arr1 in rem_dict[get_NC(taxidmap_file, chld.name)]:
#                     res.append(do_alignments(chld,arr1))
#
#                 for d in res:
#                     for k in d:
#                         if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                             if not k.split("_")[1]== max(d[k], key=lambda x: d[k][x]).split("_")[1]:
#                                 remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + get_NC(taxidmap_file, k.split("_")[0])+"\n")
#
#                                 remolding_direction.append((chld,k.split("_")[1],max(d[k], key=lambda x: d[k][x]).split("_")[1]))
#
#                 rem_internals = []
#                 if remolding_direction:     ## the case where we couldnt detect the direction of the remolding | ASK Matthias what should we do when we can't detect it.
#
#                     for i in range(len(remolding_direction)):
#
#                         node = remolding_direction[i][0]
#                         remolded_gene = remolding_direction[i][1]
#                         donor_gene = remolding_direction[i][2]
#
#                         node.arr[donor_gene]['seq'] += node.arr[remolded_gene]['seq']
#                         node.arr[donor_gene]['structure'] += node.arr[remolded_gene]['structure']
#
#                         node.arr[remolded_gene]['seq'] = ''
#                         node.arr[remolded_gene]['structure'] = ''
#
#                         nd.arr[donor_gene]['seq'] = aff_seq(chld,sis,donor_gene,donor_gene)
#                         nd.arr[remolded_gene]['seq'] = aff_seq(chld,sis,remolded_gene,remolded_gene)
#
#                         nd.arr[donor_gene]['model'] = computeModels(nd, donor_gene)
#                         nd.arr[remolded_gene]['model'] = computeModels(nd, remolded_gene)
#
#
#                         #rem_internals.append((nd.name,remolded_gene,donor_gene))
#
#                     nd.add_feature('remolding',rem_internals)
#
#             if not get_NC(taxidmap_file, chld.name) in rem_dict and get_NC(taxidmap_file, sis.name) in rem_dict:     ### only sis have remolding candidate
#                 remolding_direction = []
#                 res = []
#                 for arr2 in rem_dict[get_NC(taxidmap_file, sis.name)]:
#                     res.append(do_alignments(chld,arr2))
#
#                 for d in res:
#                     for k in d:
#                         if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                             if not k.split("_")[1]== max(d[k], key=lambda x: d[k][x]).split("_")[1]:
#                                 remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + get_NC(taxidmap_file, k.split("_")[0])+"\n")
#
#                                 remolding_direction.append((sis,k.split("_")[1],max(d[k], key=lambda x: d[k][x]).split("_")[1]))
#
#                 rem_internals = []
#                 if remolding_direction:     ## the case where we couldnt detect the direction of the remolding | ASK Matthias what should we do when we can't detect it.
#
#                     for i in range(len(remolding_direction)):
#
#                         node = remolding_direction[i][0]
#                         remolded_gene = remolding_direction[i][1]
#                         donor_gene = remolding_direction[i][2]
#
#                         node.arr[donor_gene]['seq'] += node.arr[remolded_gene]['seq']
#                         node.arr[donor_gene]['structure'] += node.arr[remolded_gene]['structure']
#
#                         node.arr[remolded_gene]['seq'] = ''
#                         node.arr[remolded_gene]['structure'] = ''
#
#                         nd.arr[donor_gene]['seq'] = aff_seq(chld,sis,donor_gene,donor_gene)
#                         nd.arr[remolded_gene]['seq'] = aff_seq(chld,sis,remolded_gene,remolded_gene)
#
#                         nd.arr[donor_gene]['model'] = computeModels(nd, donor_gene)
#                         nd.arr[remolded_gene]['model'] = computeModels(nd, remolded_gene)
#
#                         #rem_internals.append((nd.name,remolded_gene,donor_gene))
#
#                     #nd.add_feature('remolding',rem_internals)
#
#     remolding_output.close()
#
# def aff_seq_all(nd,gene):
#     global taxidmap_file
#     file=taxidmap_file
#     if gene in nd.arr.keys():
#         if nd.is_leaf():
#             fasta="> "+nd.name+"_"+gene+"\n"+nd.arr[gene]['seq']+"\n"
#             nd.arr[gene]['seq'] = fasta
#             return fasta
#
#         if not nd.is_leaf():
#             fasta=""
#             for chld in nd.get_children():
#                 #print chld.name
#                 if gene in chld.arr.keys():
#                     fasta+=aff_seq_all(chld, gene)
#                     nd.arr[gene]['seq'] = fasta
#                 else:
#                     with open(work_dir+"missing_trna.txt","a") as missing_trna:
#                         missing_trna.write(get_NC(file,chld.name) +" ("+chld.name+") is missing "+gene+"\n")
#                     continue
#
#         seq = open(work_dir+'fasta_files/' + nd.name +'_' +gene + '.fas', 'w')
#         seq.write(fasta)
#         seq.close()
#         return fasta
#     else:
#         #return ","
#         sys.stderr.write( "skipping (no "+gene+") in "+get_NC(file,nd.name)+" " )
#
#





# Rosewater
#-----------
# taxidmap_file = "/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/RNAremold/tRNA-phylo/004/tRNA-CM/RefSeq/new_taxidtoacc-refseq63.txt"
# tree_file = "/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Higgs2003_Paper_test/Demospongiae.nw"
# work_dir = "/scratch/abdullah/data/Higgs2003_Paper_test/"
# outp_dir = "/scratch/abdullah/data/Higgs2003_Paper_test/remolding/"
# outp_dir = "/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Higgs2003_Paper_test/remolding/"
# main_dir = "/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/RNAremold/tRNA-phylo/004/tRNA-CM/"
# fasta_files_dir = "/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/RNAremold/tRNA-phylo/004/tRNA-CM/RefSeq/refseq63-fasta"

# internal_models_dir = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Metazoa/result_CM_refseq56/"
# MAC
#--------
taxidmap_file = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/RefSeq/new_taxidtoacc-refseq63.txt"
tree_file = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Metazoa/Final_Metazoa_bifurcated_tree_internals.nw"
work_dir = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Higgs/"
# outp_dir = "/scratch/abdullah/data/Higgs2003_Paper_test/remolding/"
# outp_dir = "Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Higgs/remolding/"
main_dir = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/RefSeq/"
# tree_file = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/Acariformes/Acariformes_bifurcated_tree.nw"
# work_dir = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Higgs/"
# fasta_files_dir = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/test/refseq58-fasta"
# internal_models_dir = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/Acariformes/result_CM_refseq56/"


def load_data( dirs ):
    """
    """
    data_trna = {}
    data_gene = {}
    # extract all tRNAs from the MITOS results that have an annotated anticodon (and discard the others) + replace nonstandard bases with random bases(ACGTU)
    for dr in dirs:
        # if not os.listdir(dr) == []:
            # continue

        if not os.path.isdir( dr ):
            sys.stderr.write( "skipping non dir %s\n" % dr )
            continue

        try:
            gb = mitofile.mitofromfile( dr + "/result" )
        except IOError:
            sys.stderr.write( "skipping (no result) %s\n" % dr )
            continue

        try:
            f = open( dr + "/result.pkl" )
            features = cPickle.load( f )
            f.close()
        except IOErrgene == row[i].name:
            sys.stderr.write( "skipping (no features) %s\n" % dr )
            continue

        tmp = [ x for x in features if ( x.type == "tRNA" and x.anticodon == None )]
        for t in tmp:
            logging.warning( "remove degenerated tRNA: %s %s" % ( gb.accession, t.name ) )

        # data_trna[ gb.accession ] = [ x for x in features if ( x.type == "tRNA" and x.anticodon != None )]   #if we want only the ones with anticodon
        data_trna[ gb.accession ] = [ x for x in features if ( x.type == "tRNA" )]
        data_gene[ gb.accession ] = [ x for x in features if ( x.type == "gene" )]


        for i in range( len( data_trna[ gb.accession ] ) ):
            while 1:
                r = random.choice( ['A', 'U', 'C', 'G'] )
                ( data_trna[ gb.accession ][i].sequence, cnt ) = re.subn( "[^ACGTU]", r, data_trna[ gb.accession ][i].sequence, count = 1 )
                if cnt == 0:
                    break
                else:
                    logging.warning( "replaced nonstandard base by random: %s" % r )
    return data_trna, data_gene


def convert_dict( dicti ):
    d = {}
    for acc in dicti:
        if not acc in d:
            d[acc] = {}
        for g in range( len( dicti[acc] ) ):
            # if dicti[acc][g].name in ["trnL1","trnL2"]:

            if not dicti[acc][g].name in d[acc]:
                d[acc][dicti[acc][g].name] = {}
                # anti_codon=str(dicti[acc][g].anticodon).replace('T','U')
            # d[acc][dicti[acc][g].name]['seq']=dicti[acc][g].sequence+anti_codon
            d[acc][dicti[acc][g].name]['seq'] = dicti[acc][g].sequence
            d[acc][dicti[acc][g].name]['structure'] = dicti[acc][g].structure
            d[acc][dicti[acc][g].name]['model'] = main_dir + "CM-refseq63/" + acc + "/" + dicti[acc][g].name + ".cm"


    return d


def load_remolding_candidates( rem_cand_file ):
    '''
    read the remolding candidates that we found using the in-species analysis and only make the testing based on these events in the tree
    the file is as follows:
    accession    candidate_g1    candidate_g2
    '''
    rem_dict = {}
    inv_rem_dict = {}
    with open( rem_cand_file, 'r' ) as inF:
        for line in inF:
            if line.startswith( "acc" ):
                continue
            line = line.split()
            #    line[0] : acc
            #    line[1] : g1
            #    line[2] : g2
#             if not line[0] in rem_dict:
#                 rem_dict[line[0]] = {}
#             if not line[2] in rem_dict[line[0]]:
#                 rem_dict[line[0]][line[2]] =line[1]

            if not get_id( taxidmap_file, line[0] ) in rem_dict:
                rem_dict[get_id( taxidmap_file, line[0] )] = []

            rem_dict[get_id( taxidmap_file, line[0] )].append( ( line[1], line[2] ) )


    return rem_dict


def get_sequence_trna( id, gene, data ):
    row = []
    accession = get_NC( taxidmap_file, id )
    gene_seq = ""
    if accession in data:
        row = data[accession]
    else:
        sys.stderr.write( "accession not found in the data table " + accession + "\n" )

    for i in range( len( row ) ):

        if gene == row[i].name:
            gene_seq = row[i].sequence
    return gene_seq


def get_sequence_PCgenes( id, gene, fasta_files_dir, data ):
    row = []
    accession = get_NC( taxidmap_file, id )

    gene_seq = ""
    if accession in data:
        row = data[accession]
        for i in range( len( row ) ):
            if gene == row[i].name:
                gene_start = row[i].start
                gene_end = row[i].stop

                record = SeqIO.read( fasta_files_dir + "/" + accession + ".fas", 'fasta' )
                gene_seq = record.seq[gene_start:gene_end]

        return gene_seq

    else:
        sys.stderr.write( "accession not found in the data table " + accession + "\n" )
        return


# def find_Nc(NC,folder):
#
#     os.chdir(folder)
#     found = False
#     for file in glob.glob("*"):
#         if file==NC:
#             found= True
#     return found

def find_id( tax_file, id ):
    with open( tax_file, 'r' ) as inF:
        for line in inF:
            line = line.split()
            if id == line[0]:
                found = True
            else:
                found = False
    return found

def get_NC( tax_file, id ):
    acc = ""
    with open( tax_file, 'r' ) as inF:
        for line in inF:
            line = line.split()
            if id == line[0]:
                acc = line[1]
                break
    return acc




def get_id( tax_file, acc ):
    id = ""
    with open( tax_file, 'r' ) as inF:
        for line in inF:
            line = line.split()
            if acc == line[1]:
                id = line[0]
                break
    return id



def cmbuild_call( outdir, acc, gname ):
    os.system( "/opt/bin/cmbuild -F " + outdir + "CM-refseq63/" + acc + "/" + gname + ".cm " + outdir + "/stockholm_files/" + acc + "/" + gname + ".sto" )

def model_build_trna( pool, data, odirectory ):  # # takes the old dict before i convert it
    if not os.path.exists( odirectory ):
        os.makedirs( odirectory )

    if not os.path.exists( odirectory + "/stockholm_files/" ):
        os.makedirs( odirectory + "/stockholm_files" )

    if not os.path.exists( odirectory + "/CM-refseq63" ):
        os.makedirs( odirectory + "/CM-refseq63" )

    for acc in data:
        if not os.path.exists( odirectory + "/stockholm_files/" + acc ):
            os.makedirs( odirectory + "/stockholm_files/" + acc )

        if not os.path.exists( odirectory + "/CM-refseq63/" + acc ):
            os.makedirs( odirectory + "/CM-refseq63/" + acc )
        # print odirectory+acc
        for i in range( len( data[acc] ) ):
            fout = open( odirectory + "/stockholm_files/" + acc + "/" + data[acc][i].name + ".sto", "w" )
            input = "# STOCKHOLM 1.0 \n"
            input += acc + "\t" + data[acc][i].sequence + "\n" + "#=GC SS_cons \t" + data[acc][i].structure
            input += "\n//"
            fout.write( input )
            fout.close()
            pool.apply_async( cmbuild_call, args = ( odirectory, acc, data[acc][i].name ) )
            # os.system("/opt/bin/cmbuild -F "+odirectory+"/CM-refseq63/"+acc+"/"+data[acc][i].name+".cm "+ odirectory+"/stockholm_files/"+acc+"/"+data[acc][i].name+".sto")
            # print "cmbuild "+odirectory+"CM/"+acc+"/"+data[acc][i].name+".cm "+ odirectory+"stockholm-files/"+acc+"/"+data[acc][i].name+".sto"




def model_build_PCgenes( data_genes, odirectory ):
    global taxidmap_file
    global fasta_files_dir
    if not os.path.exists( odirectory ):
        os.makedirs( odirectory )

    if not os.path.exists( odirectory + "/stockholm-files/PCgenes" ):

        os.makedirs( odirectory + "/stockholm-files/PCgenes" )

    if not os.path.exists( odirectory + "/Hmm-refseq56/PCgenes" ):
        os.makedirs( odirectory + "/Hmm-refseq56/PCgenes" )

    for acc in data_genes:
        if not os.path.exists( odirectory + "/stockholm-files/PCgenes/" + acc ):
            os.makedirs( odirectory + "/stockholm-files/PCgenes/" + acc )

        if not os.path.exists( odirectory + "/Hmm-refseq56/PCgenes/" + acc ):
            os.makedirs( odirectory + "/Hmm-refseq56/PCgenes/" + acc )
        id = get_taxid( taxidmap_file, acc )

        for i in range( len( data_genes[acc] ) ):
                # print data_genes[acc][i].name
                if get_sequence_PCgenes( id, data_genes[acc][i].name, fasta_files_dir, data_genes ) is not None:
                    fout = open( odirectory + "/stockholm-files/PCgenes/" + acc + "/" + data_genes[acc][i].name + ".sto", "w" )
                    input = "# STOCKHOLM 1.0 \n"
                    input += acc + "_" + data_genes[acc][i].name + "\t" + get_sequence_PCgenes( id, data_genes[acc][i].name, fasta_files_dir, data_genes )
                    input += "\n//"
                    fout.write( str( input ) )
                    fout.close()
                    os.system( "hmmbuild " + odirectory + "/Hmm-refseq56/PCgenes/" + acc + "/" + data_genes[acc][i].name + ".cm " + odirectory + "/stockholm-files/PCgenes/" + acc + "/" + data_genes[acc][i].name + ".sto" )
                else:
                    sys.stderr.write( "skipping (no gene " + data_genes[acc][i].name + ") in " + acc )
            # print "cmbuild "+odirectory+"CM/"+acc+"/"+data[acc][i].name+".cm "+ odirectory+"stockholm-files/"+acc+"/"+data[acc][i].name+".sto"




def model_choice( sth1, sth2 ):
    '''
    param[in] : two stockholm alignments (score files) which the output model will be built from.
    i count the number of sequences inside each alignment, and we build the model from the sequence with the larger number of sequenes.
    if the number of sequences is the same, we choose a random one.
    '''

    f1 = open( sth1, 'r' )
    f2 = open( sth2, 'r' )
    i = 0
    j = 0
    for l1 in f1:
        if not l1.startswith( "#" ):
            i += 1
    f1.close()

    for l2 in f2:
        if not l2.startswith( "#" ):
            j += 1
    f2.close()

    if i > j:
        return sth1
    elif j > i:
        return sth2
    else:
        return random.choice( [sth1, sth2] )






def if_remolded( score_file ):
    '''
    it reads the score file generated from the alignment of 2 tRNA from 2 sister nodes and output the score for the infernal alignment of this model with the gene sequence(s)
    the idea is to look at the sister species and check the score, if S(X),m_Y' > S(X),m_X' => X is remolded from Y' | X' and Y' are the same tRNAs from the sister species
    
    for now, it just returns the score
    '''
    print score_file
    sfile = open( score_file, "r" )
    i = 0
    score = 0
    for line in sfile:
        if not line.startswith( "#" ):
            i += 1
            temp = line.split()
            aligned_gene = temp[1]
            score += float( temp[6] )

    sfile.close()
    return aligned_gene, score / i

def alignment_score_internals( score_file ):
    '''
    it reads the score file generated from the alignment of 2 tRNA from 2 sister nodes and output the score for the infernal alignment of this model with the gene sequence(s)
    the idea is to look at the sister species and check the score, if S(X),m_Y' > S(X),m_X' => X is remolded from Y' | X' and Y' are the same tRNAs from the sister species
    '''
    print score_file
    sfile = open( score_file, "r" )
    score = 0
    i = 0
    for line in sfile:
        if not line.startswith( "#" ):
            i += 1
            temp = line.split()

            score += float( temp[6] )

    sfile.close()
    return score / i

def uniq( inlist ):
    uniques = []
    for item in inlist:
        if item not in uniques:
            uniques.append( item )
    return uniques

def uniq_col_list( list, col ):
    un = []
    for val in range( len( list ) ):
        un.append( list[val][col] )
    return uniq( un )

def computeModels( nd, gene ):
    if nd.is_leaf() and gene in nd.arr.keys():
        # print nd.name
        mod = nd.arr[gene]['model']
        return mod

    if not nd.is_leaf():

        mod1, mod2 = computeModels( nd.get_children()[0], gene ), computeModels( nd.get_children()[1], gene )
        # print mod1, mod2
        if not mod1 is None and not mod2 is None:  # both children have models for this gene

            if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
                # # alignment based on first child model
                print "1", nd.name, gene, nd.get_children()[0].name
                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '

                print work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas', mod1
                os.system( 'cmalign \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ' )
                os.system( 'cmalign --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            else:  # has grand children >> use mapali
                print "2", nd.name, gene, nd.get_children()[0].name
                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' with mapali'
                print nd.get_children()[0].name, "alignment with best score", findSTH( nd.get_children()[0].name )
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[0].name ) + '\" \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ' )
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[0].name ) + '\" --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
                # # alignment based on second child model
                print "3", nd.name, gene, nd.get_children()[1].name, mod2
                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
                os.system( 'cmalign \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ' )
                os.system( 'cmalign --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            else:  # has grand children >> use mapali
                print "4", nd.name, gene, nd.get_children()[1].name
                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
                # print nd.name, nd.arr[gene]['seq'],findSTH(nd.get_children()[1].name)
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[1].name ) + '\" \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ' )
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[1].name ) + '\" --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            file = open( work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth', 'r' )
            score1 = 0
            i = 0
            for line in file:
                if not line.startswith( "#" ):
                    temp = line.split()
                    i += 1
                    score1 += float( temp[6] )
            file.close()
            # print score1

            file = open( work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth', 'r' )
            score2 = 0
            j = 0
            for line in file:
                if not line.startswith( "#" ):
                    temp = line.split()
                    j += 1
                    score2 += float( temp[6] )
            file.close()
            # print score2

            if score1 / i > score2 / j:
                print 'building cm at ' + nd.name + ' using ' + nd.get_children()[0].name

                os.system( 'cmbuild -F \"' + work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\" ' )

                with open( 'ndal.tmp', 'a' ) as file:
                    file.write( nd.name + ' ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\n' )
            else:
                print 'building cm at ' + nd.name + ' using ' + nd.get_children()[1].name

                os.system( 'cmbuild -F \"' + work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\" ' )

                with open( 'ndal.tmp', 'a' ) as file:
                    file.write( nd.name + ' ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\n' )

            if os.path.isfile( work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm' ):
                nd.arr[gene]['model'] = work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'

            return nd.arr[gene]['model']

        elif not mod1 is None and mod2 is None:  # only child1 have model for this gene, align only based on child1
            if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali

                print "11", nd.name, gene, nd.get_children()[0].name

                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '

                os.system( 'cmalign \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ' )
                os.system( 'cmalign --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            else:  # has grand children >> use mapali
                print "22", nd.name, gene, nd.get_children()[0].name
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[0].name ) + '\" \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ' )
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[0].name ) + '\" --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            os.system( 'cmbuild -F \"' + work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\" ' )
            with open( 'ndal.tmp', 'a' ) as file:
                file.write( nd.name + ' ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\n' )
                # file.write(nd.name +' '+ mod1+'\n')

            if os.path.isfile( work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm' ):
                nd.arr[gene]['model'] = work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'

            # print "FUCK",nd.arr[gene]['model']

            return nd.arr[gene]['model']


        elif mod1 is None and not mod2 is None:  # only child2 have model for this gene, align only based on child2

            if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
            # # alignment based on second child model
                print "33"
                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
                os.system( 'cmalign \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ' )
                os.system( 'cmalign --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            else:  # has grand children >> use mapali
                print "44"
                print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
                # print nd.name, nd.arr[gene]['seq'],findSTH(nd.get_children()[1].name)
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[1].name ) + '\" \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ' )
                os.system( 'cmalign --mapali \"' + findSTH( nd.get_children()[1].name ) + '\" --sfile ' + work_dir + 'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas\" ' )

            os.system( 'cmbuild -F \"' + work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\" ' )
            with open( 'ndal.tmp', 'a' ) as file:
                file.write( nd.name + ' ' + work_dir + 'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\n' )
                # file.write(nd.name +' '+ mod2+'\n')

            if os.path.isfile( work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm' ):
                nd.arr[gene]['model'] = work_dir + 'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'

            return nd.arr[gene]['model']

        else:  # both children have no model for this gene
            print "Oh shit!"

#
# def computeModels(nd, gene):
#     if nd.is_leaf() and gene in nd.arr.keys():
#         #print nd.name
#         mod = nd.arr[gene]['model']
#         return mod
#
#     if not nd.is_leaf():
#
#         mod1, mod2 = computeModels(nd.get_children()[0], gene), computeModels(nd.get_children()[1], gene)
#         #print mod1, mod2
#         if not mod1 is None and not mod2 is None:   # both children have models for this gene
#
#             if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
#                 # # alignment based on first child model
#                 print "1",nd.name, gene,nd.get_children()[0].name
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '
#
#                 print work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas', mod1
#                 os.system('cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ')
#                 os.system('cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#                 print "2",nd.name, gene,nd.get_children()[0].name
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' with mapali'
#
#                 print nd.get_children()[0].name, "alignment with best score", nd.get_children()[0].arr[gene]['best_alignemnt']
#                 os.system('cmalign --mapali \"' + nd.get_children()[0].arr[gene]['best_alignemnt'] + '\" \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ')
#                 os.system('cmalign --mapali \"' + nd.get_children()[0].arr[gene]['best_alignemnt'] + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
#                 # # alignment based on second child model
#                 print "3",nd.name, gene,nd.get_children()[1].name, mod2
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
#                 os.system('cmalign \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ')
#                 os.system('cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#                 print "4",nd.name, gene,nd.get_children()[1].name
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
#                 #print nd.name, nd.arr[gene]['seq'],findSTH(nd.get_children()[1].name)
#                 os.system('cmalign --mapali \"' +  nd.get_children()[1].arr[gene]['best_alignemnt']  + '\" \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ')
#                 os.system('cmalign --mapali \"' +  nd.get_children()[1].arr[gene]['best_alignemnt']  + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             file = open(work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth', 'r')
#             score1 = 0
#             i=0
#             for line in file:
#                 if not line.startswith("#"):
#                     temp = line.split()
#                     i+=1
#                     score1 += float(temp[6])
#             file.close()
#             #print score1
#
#             file = open(work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth', 'r')
#             score2 = 0
#             j=0
#             for line in file:
#                 if not line.startswith("#"):
#                     temp = line.split()
#                     j+=1
#                     score2 += float(temp[6])
#             file.close()
#             #print score2
#
#             if score1/i > score2/j:
#                 print 'building cm at ' + nd.name + ' using ' + nd.get_children()[0].name
#
#                 os.system('cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\" ')
#
# #                 with open('ndal.tmp', 'a') as file:
# #                     file.write(nd.name +' '+ work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\n')
#                 nd.arr[gene]['best_alignemnt'] = work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth'
#             else:
#                 print 'building cm at ' + nd.name + ' using ' + nd.get_children()[1].name
#
#                 os.system('cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\" ')
# #
# #                 with open('ndal.tmp', 'a') as file:
# #                     file.write(nd.name + ' '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\n')
#                 nd.arr[gene]['best_alignemnt'] = work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth'
#
#             if os.path.isfile(work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'):
#                 nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#
#             return nd.arr[gene]['model']
#
#         elif not mod1 is None and mod2 is None: #only child1 have model for this gene, align only based on child1
#             if not nd.get_children()[0].get_children():  # first child does not have childrens // directly above leafs // no use for --mapali
#
#                 print "11", nd.name, gene,nd.get_children()[0].name
#
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[0].name + ' without mapali '
#
#                 os.system('cmalign \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ')
#                 os.system('cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#                 print "22",nd.name, gene,nd.get_children()[0].name
#                 os.system('cmalign --mapali \"' +  nd.get_children()[0].arr[gene]['best_alignemnt']  + '\" \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth ')
#                 os.system('cmalign --mapali \"' +  nd.get_children()[0].arr[gene]['best_alignemnt']  + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth \"' + mod1 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             os.system('cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\" ')
# #             with open('ndal.tmp', 'a') as file:
# #                 file.write(nd.name +' '+ work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth\n')
# #                 #file.write(nd.name +' '+ mod1+'\n')
#             nd.arr[gene]['best_alignemnt'] = work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[0].name + '.sth'
#
#             if os.path.isfile(work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'):
#                 nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#
#             #print "FUCK",nd.arr[gene]['model']
#
#             return nd.arr[gene]['model']
#
#
#         elif mod1 is None and not mod2 is None: #only child2 have model for this gene, align only based on child2
#
#             if not nd.get_children()[1].get_children():  # second child does not have childrens // directly above leafs // no use for --mapali
#             # # alignment based on second child model
#                 print "33"
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' without mapali'
#                 os.system('cmalign \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ')
#                 os.system('cmalign --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             else:  # has grand children >> use mapali
#                 print "44"
#                 print 'aligning at ' + nd.name + ' based on ' + nd.get_children()[1].name + ' with mapali'
#                 #print nd.name, nd.arr[gene]['seq'],findSTH(nd.get_children()[1].name)
#                 os.system('cmalign --mapali \"' +  nd.get_children()[1].arr[gene]['best_alignemnt'] + '\" \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" > '+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth ')
#                 os.system('cmalign --mapali \"' +  nd.get_children()[1].arr[gene]['best_alignemnt']  + '\" --sfile '+work_dir+'CM_score_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth \"' + mod2 + '\" \"'+work_dir+'fasta_files/' + nd.name + '_' + gene + '.fas\" ')
#
#             os.system('cmbuild -F \"'+work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm\" \"'+work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\" ')
# #             with open('ndal.tmp', 'a') as file:
# #                 file.write(nd.name +' '+ work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth\n')
# #                 #file.write(nd.name +' '+ mod2+'\n')
#             nd.arr[gene]['best_alignemnt'] = work_dir+'stockholm_files/' + nd.name + '_' + gene + '_cm_' + nd.get_children()[1].name + '.sth'
#
#             if os.path.isfile(work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'):
#                 nd.arr[gene]['model'] = work_dir+'result_CM_refseq63/' + nd.name + '_' + gene + '.cm'
#
#             return nd.arr[gene]['model']
#
#         else:   # both children have no model for this gene
#             print "Oh shit!"

def do_alignments( nd, rarr, sis ):

    '''
    For each child of nd (if its a leaf and is a remolding candidate) we have rows inside the rem_dict dict.
    e.g:
        chld_g1 chld_g2
        sis_g1 sis_g2
        
    for each of them, i should perform the 4 following alignments:
        B with mB_sis, B with mA_sis, A with mB_sis and A with mA_sis
        
    '''

    trna_log = open( work_dir + "result_log_file.txt", "a" )

    chld = nd
    # sis = nd.get_sisters()[0]
    scrs = {}

    chld_g1 = rarr[0]
    chld_g2 = rarr[1]

    # print nd.name,nd.arr[chld_g1],nd.arr[chld_g2], sis.arr[chld_g1], rarr
    # sis_g1 = arr2[0]
    # sis_g2 = arr2[1]


    # print "0",chld.name, sis.name, rarr
    if not os.path.isfile( work_dir + 'fasta_files/' + chld.name + "_" + chld_g1 + '.fas' ):

       f = open( work_dir + 'fasta_files/' + chld.name + "_" + chld_g1 + '.fas', "w" )
       f.write( chld.arr[chld_g1]['seq'] + "\n" )
       f.close()

    # ## chld_g1 with model of chld_g1 of the sister

    if chld_g1 in sis.arr and sis.arr[chld_g1]['model']:
        print "1", work_dir + 'fasta_files/' + chld.name + "_" + chld_g1 + '.fas', sis.arr[chld_g1]['model']
        scr = 0  # ## test if the sister have g1, if yes align g1 with g1 of the sister (e.g B with mB_sis)
        os.system( 'cmalign \"' + sis.arr[chld_g1]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + "_" + chld_g1 + '.fas\" > ' + work_dir + 'stockholm_files/' + chld.name + "_" + chld_g1 + '_cm_' + sis.name + "_" + chld_g1 + '.sth ' )
        os.system( 'cmalign --sfile ' + work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g1 + '_cm_' + sis.name + '_' + chld_g1 + '.sth \"' + sis.arr[chld_g1]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + '_' + chld_g1 + '.fas\" ' )


        node_gene, scr = if_remolded( work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g1 + '_cm_' + sis.name + '_' + chld_g1 + '.sth' )


        if not chld.name + "_" + chld_g1 in scrs:
            scrs[chld.name + "_" + chld_g1] = {}
        if not sis.name + '_' + chld_g1 in scrs[chld.name + "_" + chld_g1]:
            scrs[chld.name + "_" + chld_g1][sis.name + "_" + chld_g1] = scr


    else:
        trna_log.write( get_NC( taxidmap_file, sis.name ) + " " + chld_g1 + "\n" )
        print "Sister node " + sis.name + " is missing tRNA " + chld_g1

    # ## chld_g1 with model of chld_g2 of the sister
    if chld_g2 in sis.arr and sis.arr[chld_g2]['model']:
        print "2" , chld.name, sis.name
        scr = 0
        os.system( 'cmalign \"' + sis.arr[chld_g2]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + "_" + chld_g1 + '.fas\" > ' + work_dir + 'stockholm_files/' + chld.name + "_" + chld_g1 + '_cm_' + sis.name + "_" + chld_g2 + '.sth ' )
        os.system( 'cmalign --sfile ' + work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g1 + '_cm_' + sis.name + '_' + chld_g2 + '.sth \"' + sis.arr[chld_g2]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + '_' + chld_g1 + '.fas\" ' )

        node_gene, scr = if_remolded( work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g1 + '_cm_' + sis.name + '_' + chld_g2 + '.sth' )


        if not chld.name + "_" + chld_g1 in scrs:
            scrs[chld.name + "_" + chld_g1] = {}
        if not sis.name + "_" + chld_g2 in scrs[chld.name + "_" + chld_g1]:
            scrs[chld.name + "_" + chld_g1][sis.name + "_" + chld_g2] = scr


    else:
        trna_log.write( get_NC( taxidmap_file, sis.name ) + " " + chld_g2 + "\n" )
        print "Sister node " + sis.name + " is missing tRNA " + chld_g2


    ##### same procedure, but with the switched remolding candidates. IMPORTANT ################################ IMPORTANT

    if not os.path.isfile( work_dir + 'fasta_files/' + chld.name + "_" + chld_g2 + '.fas' ):

       f = open( work_dir + 'fasta_files/' + chld.name + "_" + chld_g2 + '.fas', "w" )
       f.write( chld.arr[chld_g2]['seq'] + "\n" )
       f.close()


    # ## chld_g2 with model of chld_g2 of the sister


    if chld_g2 in sis.arr and sis.arr[chld_g2]['model']:
        print "3", chld.name, sis.name
        scr = 0  # ## test if the sister have g2
        os.system( 'cmalign \"' + sis.arr[chld_g2]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + "_" + chld_g2 + '.fas\" > ' + work_dir + 'stockholm_files/' + chld.name + "_" + chld_g2 + '_cm_' + sis.name + "_" + chld_g2 + '.sth ' )
        os.system( 'cmalign --sfile ' + work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g2 + '_cm_' + sis.name + '_' + chld_g2 + '.sth \"' + sis.arr[chld_g2]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + '_' + chld_g2 + '.fas\" ' )

        node_gene, scr = if_remolded( work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g2 + '_cm_' + sis.name + '_' + chld_g2 + '.sth' )  # # scr of g1 with g1 of the sister


        if not chld.name + "_" + chld_g2 in scrs:
            scrs[chld.name + "_" + chld_g2] = {}
        if not sis.name + '_' + chld_g2 in scrs[chld.name + "_" + chld_g2]:
            scrs[chld.name + "_" + chld_g2][sis.name + "_" + chld_g2] = scr


    else:
        trna_log.write( get_NC( taxidmap_file, sis.name ) + " " + chld_g2 + "\n" )
        print "Sister node " + sis.name + " is missing tRNA " + chld_g2


    # ## chld_g2 with model of chld_g1 of the sister

    if chld_g1 in sis.arr and sis.arr[chld_g1]['model']:
        print "4" , chld.name, sis.name
        scr = 0
        os.system( 'cmalign \"' + sis.arr[chld_g1]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + "_" + chld_g2 + '.fas\" > ' + work_dir + 'stockholm_files/' + chld.name + "_" + chld_g2 + '_cm_' + sis.name + "_" + chld_g1 + '.sth ' )
        os.system( 'cmalign --sfile ' + work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g2 + '_cm_' + sis.name + '_' + chld_g1 + '.sth \"' + sis.arr[chld_g1]['model'] + '\" \"' + work_dir + 'fasta_files/' + chld.name + '_' + chld_g2 + '.fas\" ' )

        node_gene, scr = if_remolded( work_dir + 'remolding/score_files/' + chld.name + '_' + chld_g2 + '_cm_' + sis.name + '_' + chld_g1 + '.sth' )  # # scr of g1 with remdict[g1] (i.e candidate of remolding) from the sister


        if not chld.name + "_" + chld_g2 in scrs:
            scrs[chld.name + "_" + chld_g2] = {}
        if not sis.name + "_" + chld_g1 in scrs[chld.name + "_" + chld_g2]:
            scrs[chld.name + "_" + chld_g2][sis.name + "_" + chld_g1] = scr


    else:
        trna_log.write( get_NC( taxidmap_file, sis.name ) + " " + chld_g1 + "\n" )
        print "Sister node " + sis.name + " is missing tRNA " + chld_g1



    trna_log.write( str( scrs ) + "\n" )
    # print scrs
    return scrs




def fix_node_model( nd, donor_gene ):

    f = open( work_dir + 'fasta_files/' + nd.name + "_" + donor_gene + '.fas', "w" )
    f.write( nd.arr[donor_gene]['seq'] + "\n" )
    f.close()


    clustalw_cline = ClustalwCommandline( "clustalw2", infile = work_dir + 'fasta_files/' + nd.name + "_" + donor_gene + '.fas', outfile = work_dir + "clustal_alignments/" + nd.name + "_" + donor_gene + ".aln" )
    clustalw_cline()
    AlignIO.convert( work_dir + "clustal_alignments/" + nd.name + "_" + donor_gene + ".aln", "clustal", work_dir + "stockholm_files/" + nd.name + "_" + donor_gene + ".sth", "stockholm" )  # convert alignment file to stockholm in order to use it with quick tree

    os.system( 'cmbuild --noss -F \"' + work_dir + 'result_CM_refseq63/' + nd.name + '_' + donor_gene + '.cm\" \"' + work_dir + 'stockholm_files/' + nd.name + '_' + donor_gene + '.sth\" ' )

    nd.arr[donor_gene]['model'] = work_dir + 'result_CM_refseq63/' + nd.name + '_' + donor_gene + '.cm'


    return nd.arr[donor_gene]['model']

def fix_remolding_bags( parent_nd, node, remolded_gene, donor_gene ):



    chld = parent_nd.get_children()[0]
    sis = parent_nd.get_children()[1]

    # node.arr[donor_gene]['seq'] += node.arr[remolded_gene]['seq']
    # node.arr[donor_gene]['structure'] += node.arr[remolded_gene]['structure']
    # node.arr[donor_gene]['model'] = fix_node_model(node,donor_gene)


    node.arr[remolded_gene]['seq'] = ''
    node.arr[remolded_gene]['structure'] = ''
    node.arr[remolded_gene]['model'] = ''  # ## this has the effect that if the parent node chose this model as the best one, in the next iteration up this will throw an error

    parent_nd.arr[donor_gene]['seq'] = aff_seq( chld, sis, donor_gene, donor_gene )
    parent_nd.arr[remolded_gene]['seq'] = aff_seq( chld, sis, remolded_gene, remolded_gene )

    parent_nd.arr[donor_gene]['model'] = computeModels( parent_nd, donor_gene )
    print "------------------------------------------------------------------------------------------------------------"
    parent_nd.arr[remolded_gene]['model'] = computeModels( parent_nd, remolded_gene )


def test_fix_remolding_bags( node, remolded_gene, donor_gene ):


    node.arr[donor_gene]['seq'] += node.arr[remolded_gene]['seq']
    node.arr[donor_gene]['structure'] += node.arr[remolded_gene]['structure']


    node.arr[remolded_gene]['seq'] = ''
    node.arr[remolded_gene]['structure'] = ''
    node.arr[remolded_gene]['model'] = ''

# def up_sis(g1,g2,node,rem_dict):        ### needs to be changed to return only the first node that does not have the tested gene(s) as remolding candidates
#     l = []
#     ll = []
#
#     for arr in rem_dict[node.name]:
#         ll.append(arr[0])
#         ll.append(arr[1])
#     while not node.is_root():
#
#         node = node.up
#         if not node.is_root():
#             if not sis.name in rem_dict:
#                 if node.get_sisters()[0].is_leaf():
#                     l.append(node.get_sisters()[0])
#
#             elif not g1 in ll and not g2 in ll:
#                 if node.get_sisters()[0].is_leaf():
#                     l.append(node.get_sisters()[0])
#
#     return l


def up_sis( g1, g2, node, rem_dict ):  # ## needs to be changed to return only the first node that does not have the tested gene(s) as remolding candidates
    l = []
    ll = []

    for arr in rem_dict[node.name]:
        ll.append( arr[0] )
        ll.append( arr[1] )
    while not node.is_root():

        node = node.up
        if not node.is_root():
            if not sis.name  in rem_dict:
                if node.get_sisters()[0].is_leaf():
                    l.append( node.get_sisters()[0] )

            elif not g1 in ll and not g2 in ll:
                if node.get_sisters()[0].is_leaf():
                    l.append( node.get_sisters()[0] )

    return l

# ## should be fixed is : the candidate or outlier should not have any pair which contain one of the candidates to be compared.
# #i.e if the pair is (R,T) i should not use (R,Y) neither (Y,R).



#     global taxidmap_file
#
#     #print rem_dict
#
#     remolding_output = open(work_dir+"all_remoldings.txt","w")
#     for nd in t.traverse("postorder"):
#         #scrs = {}
# #         if nd.is_root():
# #             continue
#
#         if not nd.is_leaf():
#             scrs = {}
#             chld = nd.get_children()[0]
#             sis = nd.get_children()[1]
#             res = {}
# #             print get_NC(taxidmap_file, chld.name), get_NC(taxidmap_file, sis.name)
#             if not chld.name in rem_dict and not sis.name in rem_dict:     ### both don't have remolding events
#
#                 continue
#
#             elif chld.name in rem_dict and sis.name in rem_dict:     ### both have remolding events
#                 #print chld.name, sis.name,"22"
#                 remolding_direction = []
#                 direction_not_detected = []
#                 same_rem = []
#
#                 same_rem = list(set(rem_dict[chld.name]) & set(rem_dict[sis.name])) ## test if they have the same remolding candidates using list intersctions (no intersection -> no same remolding candidates)
#
#                 for l in rem_dict[chld.name]:            ### test if the remolding candidates are the same but are swtiched
#                     for ll in rem_dict[sis.name]:
#                         if l == tuple(reversed(ll)):
#                             if l not in same_rem and reversed(l) not in same_rem:
#                                 same_rem.append(l)
# #
# #                 if same_rem:
# #                     nd.add_feature('same',same_rem)
#
#                 res={}
#
#                 for arr1 in rem_dict[chld.name]:         #### array containing the 2 candidate genes from chld
#                     #print arr1,"4"
#                     if arr1 not in same_rem:
#                         if not chld in res:
#                             res[chld] = []
#                         res[chld].append(do_alignments(chld,arr1,chld.get_sisters()[0]))
#
#
#                 for arr2 in rem_dict[sis.name]:      #### array containing the 2 candidate genes from sis
#                     #print arr2,"3"
#                     if arr2 not in same_rem:
#                         if not sis in res:
#                             res[sis] = []
#                         #print arr2
#                         res[sis].append(do_alignments(sis,arr2,sis.get_sisters()[0]))
#
#
#                 unique_unknown_direction = []
#                 ## loop through the result array, and get the remolding direction
#                 for kid in res:     # loop over all kids of nd
#                     for d in res[kid]:   # loop over all dicts of kid
#                         for k in d:
#                             if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                                 if not k.split("_")[1] == max(d[k], key=lambda x: d[k][x]).split("_")[1]:
#
#                                     #remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" "+ get_NC(taxidmap_file, k.split("_")[0])+"\n")
#                                     remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" "+ k.split("_")[0]+"\n")
#
#
#                                     #trnN is remolded from  trnK  in accession NC_007438
#                                     #Assuming N is remolded from K, this means that the sequence of N needs to be appended with K in the ancestor. The append can be done at the chld level.
#
#                                                                 #node, donor gene,remolded gene
#                                     remolding_direction.append((kid,max(d[k], key=lambda x: d[k][x]).split("_")[1],k.split("_")[1]))
#                                 else:
#                                     needed_genes = tuple([i.split("_")[1] for i in d[k].keys()])
#                                     if not (kid,needed_genes[0],needed_genes[1]) in direction_not_detected:
#                                         direction_not_detected.append((kid,needed_genes[0],needed_genes[1]))
#
#
#
#                 if remolding_direction:     ## the case where we couldnt detect the direction of the remolding | ASK Matthias what should we do when we can't detect it.
#
#                     for i in range(len(remolding_direction)):
#
#                         node = remolding_direction[i][0]
#                         donor_gene = remolding_direction[i][1]
#                         remolded_gene = remolding_direction[i][2]
#
#                         fix_remolding_bags(nd,node,remolded_gene,donor_gene)
#
#
#                 test = {}
#                 if direction_not_detected:
#                     for i in range(len(direction_not_detected)):
#                         nod = direction_not_detected[i][0]
#                         g1 = direction_not_detected[i][1]
#                         g2 = direction_not_detected[i][2]
#
#
#
#                         #print nd.name
#
#                         no_remolding_cand = up_sis(g1,g2,nod,rem_dict)     ## this function return the list of nodes which does not have remolding candidates similar as nod
#
#
#                         for i in range(len(no_remolding_cand)):
#                             test=do_alignments(nod,(g1,g2),no_remolding_cand[i])
#
#                             for k in test:
#
#                                 if len(test[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                                     if not k.split("_")[1] == max(test[k], key=lambda x: test[k][x]).split("_")[1]:
#
#                                         remolded_gene = k.split("_")[1]
#                                         donor_gene = max(test[k], key=lambda x: test[k][x]).split("_")[1]
#
#                                         fix_remolding_bags(nd,nod,remolded_gene,donor_gene)
#
#                                         remolding_output.write(max(test[k], key=lambda x: test[k][x]).split("_")[1]+" "+k.split("_")[1]+" "+ k.split("_")[0]+"\n")
#
#                                         #print "detected", max(test[k], key=lambda x: test[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + k.split("_")[0]
#
#
#                                     else:
#                                         if not nd.name in rem_dict:
#                                             rem_dict[nd.name] =[]
#
#                                         if not tuple(reversed((g1,g2))) in rem_dict[nd.name] and not (g1,g2) in rem_dict[nd.name]:
#                                             rem_dict[nd.name].append((g1,g2))
#
#
#             if chld.name in rem_dict and not sis.name in rem_dict:     ### only chld have remolding candidate
#                 res = []
#                 remolding_direction = []
#                 direction_not_detected = []
#                 for arr1 in rem_dict[chld.name]:
#                     res.append(do_alignments(chld,arr1,chld.get_sisters()[0]))
#
#                 for d in res:
#                     for k in d:
#                         if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                             if not k.split("_")[1]== max(d[k], key=lambda x: d[k][x]).split("_")[1]:
#                                 #remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + get_NC(taxidmap_file, k.split("_")[0])+"\n")
#                                 remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + k.split("_")[0]+"\n")
#
#
#                                 remolding_direction.append((chld,max(d[k], key=lambda x: d[k][x]).split("_")[1],k.split("_")[1]))
#                             else:
#                                 needed_genes = tuple([i.split("_")[1] for i in d[k].keys()])
#                                 if not (chld,needed_genes[0],needed_genes[1]) in direction_not_detected:
#                                     direction_not_detected.append((chld,needed_genes[0],needed_genes[1]))
#
#                 rem_internals = []
#                 if remolding_direction:     ## the case where we couldnt detect the direction of the remolding | ASK Matthias what should we do when we can't detect it.
#
#                     for i in range(len(remolding_direction)):
#
#                         node = remolding_direction[i][0]
#                         donor_gene = remolding_direction[i][1]
#                         remolded_gene = remolding_direction[i][2]
#
# #                         node.arr[donor_gene]['seq'] += node.arr[remolded_gene]['seq']
# #                         node.arr[donor_gene]['structure'] += node.arr[remolded_gene]['structure']
# #
# #                         node.arr[remolded_gene]['seq'] = ''
# #                         node.arr[remolded_gene]['structure'] = ''
# #
# #                         nd.arr[donor_gene]['seq'] = aff_seq(chld,sis,donor_gene,donor_gene)
# #                         nd.arr[remolded_gene]['seq'] = aff_seq(chld,sis,remolded_gene,remolded_gene)
# #
# #                         nd.arr[donor_gene]['model'] = computeModels(nd, donor_gene)
# #                         nd.arr[remolded_gene]['model'] = computeModels(nd, remolded_gene)
#
#
#                         fix_remolding_bags(nd,node,remolded_gene,donor_gene)
#
#                 if direction_not_detected:
#                     for i in range(len(direction_not_detected)):
#                         nod = direction_not_detected[i][0]
#                         g1 = direction_not_detected[i][1]
#                         g2 = direction_not_detected[i][2]
#
#                         if not nd.name in rem_dict:
#                             rem_dict[nd.name] =[]
#
#                         if not tuple(reversed((g1,g2))) in rem_dict[nd.name] and not (g1,g2) in rem_dict[nd.name]:
#                             rem_dict[nd.name].append((g1,g2))
#
#             if not chld.name in rem_dict and sis.name in rem_dict:     ### only sis have remolding candidate
#                 remolding_direction = []
#                 direction_not_detected = []
#                 res = []
#                 for arr2 in rem_dict[sis.name]:
#                     res.append(do_alignments(sis,arr2,sis.get_sisters()[0]))
#
#                 for d in res:
#                     for k in d:
#                         if len(d[k].keys()) > 1:    ## this is the sister tRNA is missing.
#                             if not k.split("_")[1]== max(d[k], key=lambda x: d[k][x]).split("_")[1]:
#                                 #remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + get_NC(taxidmap_file, k.split("_")[0])+"\n")
#                                 remolding_output.write(max(d[k], key=lambda x: d[k][x]).split("_")[1]+" "+k.split("_")[1]+" " + k.split("_")[0]+"\n")
#
#                                 remolding_direction.append((sis,max(d[k], key=lambda x: d[k][x]).split("_")[1],k.split("_")[1]))
#                             else:
#                                 needed_genes = tuple([i.split("_")[1] for i in d[k].keys()])
#                                 #(sis,)+tuple(reversed((needed_genes[0],needed_genes[1]))) in direction_not_detected check if the reversed tuple is in the list
#                                 if not (sis,needed_genes[0],needed_genes[1]) in direction_not_detected:
#                                     direction_not_detected.append((sis,needed_genes[0],needed_genes[1]))
#
#
#                 if remolding_direction:     ## the case where we couldnt detect the direction of the remolding | ASK Matthias what should we do when we can't detect it.
#
#                     for i in range(len(remolding_direction)):
#
#                         node = remolding_direction[i][0]
#                         donor_gene = remolding_direction[i][1]
#                         remolded_gene = remolding_direction[i][2]
#
#                         fix_remolding_bags(nd,node,remolded_gene,donor_gene)
#
#
#                 if direction_not_detected:
#                     for i in range(len(direction_not_detected)):
#                         nod = direction_not_detected[i][0]
#                         g1 = direction_not_detected[i][1]
#                         g2 = direction_not_detected[i][2]
#
#                         if not nd.name in rem_dict:
#                             rem_dict[nd.name] =[]
#
#                         if not tuple(reversed((g1,g2))) in rem_dict[nd.name] and not (g1,g2) in rem_dict[nd.name]:
#                             rem_dict[nd.name].append((g1,g2))
#
#
#     remolding_output.close()
#


def up_sis_one_side( gene, t, node_up, node, rem_dict ):
    '''
    return the closest species to 'node' that does not have 'gene' as a remolding candidate
    '''

    # all_leaves= t.iter_leaves()
    out_dict = {}


    # node_up = node      ## in order to keep track of the node im testing
    node_up = node_up.up
    leaves = node_up.get_leaves()
    # print node, leaves


    for l in leaves:  # # maybe i should replace this loop and only loop on the closest leafs (20 or 50 nodes far as a max )
        if not l.name == node.name:

            if not l.name in rem_dict:

                if not l in out_dict:
                    out_dict[l] = 0
                out_dict[l] = t.get_distance( l, node, topology_only = True )

            else:

                all_cand = []
                for arr2 in rem_dict[l.name]:
                    all_cand.append( arr2[0] )
                    all_cand.append( arr2[1] )

                if gene not in all_cand:
                    if not l in out_dict:
                        out_dict[l] = 0
                    out_dict[l] = t.get_distance( l, node, topology_only = True )

    # print out_dict
    if not out_dict:
        return up_sis_one_side( gene, t, node_up, node, rem_dict )
    else:
        # print "5 ",min(out_dict, key=lambda x: out_dict[x]).name, type(min(out_dict, key=lambda x: out_dict[x]))
        return min( out_dict, key = lambda x: out_dict[x] )



def read_background_distributions_in_species():
    '''
    this distribution is read from file where i have the bit scores for the all x all alignments within each species.
    the alignment of T with T is being neglected (i.e only alignmnets of X != Y is being imported here)
    '''
    distributions_dict = {}
    background_distributions = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/background_distributions_same_species"
    for fn in os.listdir( background_distributions ):
        full_file_path = os.path.join( background_distributions, fn )
        if os.path.isfile( full_file_path ):
            ff = open( full_file_path ).read()
            ff = ff.translate( None, '\n' )
            basefn, ext = os.path.splitext( fn )
            if not basefn in distributions_dict:
                distributions_dict[basefn] = ff

    return distributions_dict

def read_background_distributions_between_species():
    '''
    this distribution is read from file where i have the bit scores for the alignments of trnX with trnX in different species.
    the alignment of T with X is being neglected (i.e only alignmnets of X = X' (from different species) is being imported here)
    '''
    distributions_dict = {}
    background_distributions = "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/background_distributions_same_trna_different_species/"
    for fn in os.listdir( background_distributions ):
        full_file_path = os.path.join( background_distributions, fn )
        if os.path.isfile( full_file_path ):
            ff = open( full_file_path ).read()
            ff = ff.translate( None, '\n' )
            basefn, ext = os.path.splitext( fn )
            if not basefn in distributions_dict:
                distributions_dict[basefn] = ff

    return distributions_dict


def create_distribution_between_species( t, rem_dict ):
    '''
    This distribution is created from the alignments of trnX with the closely related trnX that is not a remolding candidate. 
    For each leaf, for each tRNA family i do the same and i get a distribution of scores for each tRNA family.
     
    I creates a file containing the bit score of the alignment of each tRNA with the same tRNA from a different species that does not have the same
    remolding candidate and is the closest in term of topology distance
     
    '''

    between_species_dist = open( work_dir + "between_species_distributions.txt", "w" )
    nb_leaves = len( t.get_leaves() )
    i = 0
    for l in t.get_leaves():
        i += 1

        sis = l.get_sisters()[0]


        for gene in l.arr:
            print "\n", i, "/", nb_leaves, "\n"
            if not sis.name in rem_dict:

                if sis.is_leaf():
                                            # # alignged   used_to_align    score
                    between_species_dist.write( l.name + " " + sis.name + " " + gene + " " + str( do_alignments_one_side( l, sis, gene ) ) + "\n" )
                    # print "1 "+l.name + " "+ gene+ " alignment with sis "+sis.name
                else:

                    closet_leaf_no_cand = up_sis_one_side( gene, t, l, l, rem_dict )


                    if not closet_leaf_no_cand is None:
                        between_species_dist.write( l.name + " " + closet_leaf_no_cand.name + " " + gene + " " + str( do_alignments_one_side( l, closet_leaf_no_cand, gene ) ) + "\n" )


            else:

                all_cand = []
                for arr2 in rem_dict[sis.name]:
                    all_cand.append( arr2[0] )
                    all_cand.append( arr2[1] )

                if gene not in all_cand:
                    between_species_dist.write( l.name + " " + sis.name + " " + gene + " " + str( do_alignments_one_side( l, sis, gene ) ) + "\n" )
                    # print "2 "+l.name+" "+ gene+" alignment with sis "+sis.name

                else:

                    closet_leaf_no_cand = up_sis_one_side( gene, t, l, l, rem_dict )

                    if not closet_leaf_no_cand is None:
                        between_species_dist.write( l.name + " " + closet_leaf_no_cand.name + " " + gene + " " + str( do_alignments_one_side( l, closet_leaf_no_cand, gene ) ) + "\n" )


    between_species_dist.close()


def do_alignments_one_side( nd1, nd2, gene ):

    '''
    This function creates the alignments to generated the distributions for each tRNA familty between species.
        
    '''

    if not os.path.isfile( work_dir + 'fasta_files/' + nd1.name + "_" + gene + '.fas' ):

       f = open( work_dir + 'fasta_files/' + nd1.name + "_" + gene + '.fas', "w" )
       f.write( nd1.arr[gene]['seq'] + "\n" )
       f.close()

    # ## nd1 with nd2

    if gene in nd2.arr and nd2.arr[gene]['model']:
        # print "1", work_dir+'fasta_files/' + nd1.name+"_"+gene+'.fas', nd2.arr[gene]['model']

        scr = 0  # ## test if the sister have g1, if yes align g1 with g1 of the sister (e.g B with mB_sis)
        # os.system('cmalign \"' + nd2.arr[gene]['model'] + '\" \"'+work_dir+'fasta_files/' + nd1.name+"_"+gene+'.fas\" > '+work_dir+'stockholm_files/' +nd1.name+"_"+gene+ '_cm_'+nd2.name+"_"+gene + '.sth ')
        os.system( 'cmalign --sfile ' + work_dir + 'remolding/score_files/test/' + nd1.name + '_' + gene + '_cm_' + nd2.name + '_' + gene + '.sth \"' + nd2.arr[gene]['model'] + '\" \"' + work_dir + 'fasta_files/' + nd1.name + '_' + gene + '.fas\" ' )


        node_gene, scr = if_remolded( work_dir + 'remolding/score_files/test/' + nd1.name + '_' + gene + '_cm_' + nd2.name + '_' + gene + '.sth' )


    else:
        print "node " + nd2.name + " is missing tRNA " + gene
        scr = 0


    return scr


def significance_test( alignments_score_dict, in_species_distributions_dict, between_species_distributions_dict, pval_threshold ):
    global taxidmap_file
    '''
    alignments_score_dict is as follows:
    
        {Gene_X:{Model_1:'',Model_2,''}
        
        The significance test should be done based on the distribution of the model used for the alignment
    
        in_species_distributions_dict : distribution of score of the alignment for each tRNA against all the tRNAs of the same species (ignoring the same tRNA)
        between_species_distributions_dict: distribution of scores for each tRNA aligned with the same tRNA from a closely related species.
        
    for a score of gene x with model y to be considered as a remolding, it should be signigicantly larger than the distribution of model y inside the 'in_species_distributions'
    and it should be within or larger than the distribution of model y inside 'between_species_distributions'.
        
    '''
    stat_file = open( work_dir + "stats_file.txt", "a" )
    remolded_gene = None
    donor_gene = None
    for g in alignments_score_dict:
        for m in alignments_score_dict[g]:
            if m.split( "_" )[1] == g.split( "_" )[1]:
                continue
            print "\n", m.split( "_" )[1], "---------\n"
            ro.r( m.split( "_" )[1] + '_dist_in_sp=' + in_species_distributions_dict[m.split( "_" )[1]] )  # # adding distribution from dict as R variable to R session
            ro.r( m.split( "_" )[1] + '_dist_btw_sp=' + between_species_distributions_dict[m.split( "_" )[1]] )  # # adding distribution from dict as R variable to R session
            if len( alignments_score_dict[g].keys() ) < 2:
                remolded_gene = None
                donor_gene = None
                continue
            if len( alignments_score_dict[g].keys() ) > 1:  # # this if the sister tRNA is missing.
                ro.r( 'bit_score =' + str( alignments_score_dict[g][m] ) )
                # k.split("_")[1] == max(test[k], key=lambda x: test[k][x]).split("_")[1]
                # ## this if statement tests multiple things:
                #    1- if the max score of the gene g based on model m is not the same gene
                #    2- if the score of gene g with model m is larger than the distribution of all scores of model m within the same species (distribution of the model used to align)
                #    3- if the score of gene g with model m is inside the distribution of all scores of gene g aligned with all occurances of model m between closely related species (distribution of the model used to align)
                if ( not g.split( "_" )[1] == max( alignments_score_dict[g], key = lambda x: alignments_score_dict[g][x] ).split( "_" )[1] and ro.r( 'wilcox.test(bit_score,' + m.split( "_" )[1] + '_dist_in_sp,alternative=c(\'greater\'))$p.value' )[0] <= pval_threshold ) and ( ro.r( 'wilcox.test(bit_score,' + m.split( "_" )[1] + '_dist_btw_sp,alternative=c(\'greater\'))$p.value' )[0] <= pval_threshold or ro.r( 'wilcox.test(bit_score,' + m.split( "_" )[1] + '_dist_btw_sp,alternative=c(\'less\'))$p.value' )[0] > pval_threshold ):


                    # print "\n\n34343",g.split("_")[1], max(alignments_score_dict[g], key=lambda x: alignments_score_dict[g][x]).split("_")[1],"\n\n"

                    remolded_gene = g.split( "_" )[1]
                    donor_gene = m.split( "_" )[1]
                if not ro.r( 'wilcox.test(bit_score,' + m.split( "_" )[1] + '_dist_in_sp,alternative=c(\'greater\'))$p.value' )[0] <= pval_threshold:
                    #                 node_aligned        gene_aligned        node_used            gene_used
                    stat_file.write( get_NC( taxidmap_file, g.split( "_" )[0] ) + " " + g.split( "_" )[1] + " " + m.split( "_" )[0] + " " + m.split( "_" )[1] + " in_species_distribution\n" )

                if ro.r( 'wilcox.test(bit_score,' + m.split( "_" )[1] + '_dist_btw_sp,alternative=c(\'greater\'))$p.value' )[0] > pval_threshold or ro.r( 'wilcox.test(bit_score,' + m.split( "_" )[1] + '_dist_btw_sp,alternative=c(\'less\'))$p.value' )[0] <= pval_threshold:
                    stat_file.write( get_NC( taxidmap_file, g.split( "_" )[0] ) + " " + g.split( "_" )[1] + " " + m.split( "_" )[0] + " " + m.split( "_" )[1] + " between_species_distribution\n" )

                if g.split( "_" )[1] == max( alignments_score_dict[g], key = lambda x: alignments_score_dict[g][x] ).split( "_" )[1]:
                    stat_file.write( get_NC( taxidmap_file, g.split( "_" )[0] ) + " " + g.split( "_" )[1] + " " + m.split( "_" )[0] + " " + m.split( "_" )[1] + " larger_score\n" )

                    # print "score is not significantly larger than the distribution of "+ m.split("_")[1]
    print alignments_score_dict
    return remolded_gene, donor_gene

def fill_remolding_directions( t, remolding_result_file ):
    global taxidmap_file
    arr = {}
    fin = open( remolding_result_file, "r" )
    for line in fin:
        line = line.strip()
        line = line.split( " " )
        #        accesson,donor,remolded
        if not line[2] in arr:
            arr[line[2]] = []
        arr[line[2]].append( "d_" + line[0] + " | r_" + line[1] )
        # arr.append((line[2],line[0],line[1]))

    for node in t.traverse():
        if get_NC( taxidmap_file, node.name ) in arr:

            node.add_feature( 'remolding', arr[get_NC( taxidmap_file, node.name )] )
        else:
            node.add_feature( 'remolding', '' )
    return t

def my_layout( node ):
    global node2leaves
    global taxidmap_file
    global t
    fin = open( "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Final_Remolding_Results_Metazoa_new.txt", "r" )
    test = []
    for line in fin:
        line = line.strip()
        line = line.split( " " )
        test.append( t.search_nodes( name = line[2] )[0] )

    # print node.name
    if set( node2leaves[node] ).intersection( set( test ) ):
        node.img_style["draw_descendants"] = True

#     if node.remolding=='':
#         node.img_style["draw_descendants"] = True
#
#     else:
#         node.img_style["draw_descendants"] = False
#
#

def up_sis_both_sides( g1, g2, t, node_up, node, rem_dict, to_ignore_dict ):
    '''
    return the closest species to 'node' that does not have 'gene' as a remolding candidate
    '''

    # all_leaves= t.iter_leaves()
    out_dict = {}


    # node_up = node      ## in order to keep track of the node im testing
    node_up = node_up.up
    leaves = node_up.get_leaves()
    # print node, leaves

    for l in leaves:
        if l.name == node.name:
            continue

        if g1 in l.arr and g2 in l.arr:

            # print "asdadasdasdasdasd",l.arr[g1],l.arr[g2]
            if not l.name in to_ignore_dict:

                if not l in out_dict:
                    out_dict[l] = 0
                out_dict[l] = t.get_distance( l, node, topology_only = True )

            else:

                all_cand = []
                for arr2 in to_ignore_dict[l.name]:
                    all_cand.append( arr2[0] )
                    all_cand.append( arr2[1] )

                if g1 not in all_cand and g2 not in all_cand:
                    if not l in out_dict:
                        out_dict[l] = 0
                    out_dict[l] = t.get_distance( l, node, topology_only = True )

    # print out_dict
    if not out_dict:

        return up_sis_both_sides( g1, g2, t, node_up, node, rem_dict, to_ignore_dict )
    else:

        return min( out_dict, key = lambda x: out_dict[x] ), t.get_distance( l, min( out_dict, key = lambda x: out_dict[x] ), topology_only = True )


def remolding_in_tree( t, to_ignore_dict, rem_dict, in_species_distributions_dict, between_species_distributions_dict ):
    global taxidmap_file

    # print rem_dict

    remolding_output = open( work_dir + "all_remoldings-new-0.05.txt", "w" )
    for nd in t:
        test = {}

        sis = nd.get_sisters()[0]

        if not nd.name in rem_dict:
            continue

        elif nd.name in rem_dict:
            for arr1 in rem_dict[nd.name]:
                g1 = arr1[0]
                g2 = arr1[1]
                print g1, g2
                if not sis.name  in rem_dict:  # sis does not have any remolding candidates
                    if sis.is_leaf() and g1 in sis.arr and g2 in sis.arr:  # sis is leaf
                        test = do_alignments( nd, ( g1, g2 ), sis )
                        remolded_gene, donor_gene = significance_test( test, in_species_distributions_dict, between_species_distributions_dict, 0.05 )
                        remolding_output.write( str( donor_gene ) + " " + str( remolded_gene ) + " " + nd.name + " " + get_NC( taxidmap_file, nd.name ) + " " + "sis " + sis.name + "\n" )
                        print "11111111111111111"

                    else:  # if not leaf and does not have any remolding candidates, it means its internal node, so we need to search more
                        print "22222222222222222"
                        le, dist = up_sis_both_sides( g1, g2, t, nd, nd, rem_dict, to_ignore_dict )
                        test = do_alignments( nd, ( g1, g2 ), le )
                        remolded_gene, donor_gene = significance_test( test, in_species_distributions_dict, between_species_distributions_dict, 0.05 )
                        remolding_output.write( str( donor_gene ) + " " + str( remolded_gene ) + " " + nd.name + " " + get_NC( taxidmap_file, nd.name ) + " " + str( dist ) + " " + le.name + "\n" )
                        print "\n\n3", donor_gene, remolded_gene, "\n\n"


                elif sis.name  in rem_dict and g1 in sis.arr and g2 in sis.arr:  # # sister node has remolding candidates, they need to be checked if they have the same one for the rested candidate of nd

                    all_cand = []
                    for arr2 in rem_dict[sis.name]:
                        all_cand.append( arr2[0] )
                        all_cand.append( arr2[1] )
                    if g1 not in all_cand and g2 not in all_cand:
                        print "33333333333333333"
                        test = do_alignments( nd, ( g1, g2 ), sis )
                        remolded_gene, donor_gene = significance_test( test, in_species_distributions_dict, between_species_distributions_dict, 0.05 )
                        remolding_output.write( str( donor_gene ) + " " + str( remolded_gene ) + " " + nd.name + " " + get_NC( taxidmap_file, nd.name ) + " " + "sis " + sis.name + "\n" )
                        print "\n\n 2", donor_gene, remolded_gene, "\n\n"

                    else:  # # sister has remolding candidates similar to the ones being tested, we should look for other candidates going up in the tree
                        print "44444444444444444"
                        le, dist = up_sis_both_sides( g1, g2, t, nd, nd, rem_dict, to_ignore_dict )

                        test = do_alignments( nd, ( g1, g2 ), le )
                        remolded_gene, donor_gene = significance_test( test, in_species_distributions_dict, between_species_distributions_dict, 0.05 )
                        remolding_output.write( str( donor_gene ) + " " + str( remolded_gene ) + " " + nd.name + " " + get_NC( taxidmap_file, nd.name ) + " " + str( dist ) + " " + le.name + "\n" )
                        print "\n\n3", donor_gene, remolded_gene, "\n\n"


                else:
                    print "555555555"
                    le, dist = up_sis_both_sides( g1, g2, t, nd, nd, rem_dict, to_ignore_dict )

                    test = do_alignments( nd, ( g1, g2 ), le )
                    remolded_gene, donor_gene = significance_test( test, in_species_distributions_dict, between_species_distributions_dict, 0.05 )
                    remolding_output.write( str( donor_gene ) + " " + str( remolded_gene ) + " " + nd.name + " " + get_NC( taxidmap_file, nd.name ) + " " + str( dist ) + " " + le.name + "\n" )
                    print "\n\n5", donor_gene, remolded_gene, "\n\n"


    remolding_output.close()


def aff_seq_all( nd, gene ):
    global taxidmap_file
    if gene in nd.arr.keys():
        if nd.is_leaf():

            fasta = "> " + nd.name + "_" + gene + "\n" + nd.arr[gene]['seq'] + "\n"
            nd.arr[gene]['seq'] = fasta

            seq = open( work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas', 'w' )
            seq.write( fasta )
            seq.close()
            return fasta

        if not nd.is_leaf():
            fasta = ""
            for chld in nd.get_children():

                if gene in chld.arr.keys():
                    fasta += aff_seq_all( chld, gene )
                    nd.arr[gene]['seq'] = fasta
                else:
                    with open( work_dir + "missing_trna.txt", "a" ) as missing_trna:
                        missing_trna.write( get_NC( taxidmap_file, chld.name ) + " (" + chld.name + ") is missing " + gene + "\n" )
                    continue
        # print nd.name
        seq = open( work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas', 'w' )
        seq.write( fasta )
        seq.close()
        return fasta
    else:
        # return ","
        sys.stderr.write( "skipping (no " + gene + ") in " + get_NC( taxidmap_file, nd.name ) + " " )




def init_leafs_seq( t, gene ):
    for nd in t:
        if gene in nd.arr.keys():

            if nd.is_leaf():
                fasta = "> " + nd.name + "_" + gene + "\n" + nd.arr[gene]['seq'] + "\n"
                nd.arr[gene]['seq'] = fasta

                seq = open( work_dir + 'fasta_files/' + nd.name + '_' + gene + '.fas', 'w' )
                seq.write( fasta )
                seq.close()

    return t


def aff_seq( chld, sis, g1, g2 ):

    if g1 in chld.arr and g2 in sis.arr:
        return chld.arr[g1]['seq'] + sis.arr[g2]['seq']
    elif g1 in chld.arr and not g2 in sis.arr:
        return chld.arr[g1]['seq']
    elif not g1 in chld.arr and g2 in sis.arr:
        return sis.arr[g1]['seq']
    elif not g1 in chld.arr and not g2 in sis.arr:
        return ''
    else:
        print "shit,WTF"

def findSTH( id ):
    file = open( 'ndal.tmp', 'r' )  # ndal.tmp > temporary file to store the correct alignment models
    for line in file:
        line = line.split()
        if line[0] == id:
            best = line[1]
    file.close()
    return best


def intialize_non_leaves( t ):
    """
    go through all the nodes of tree and add an empty dictionary to all the internal nodes.
    @param[in] tree

    return a tree which contains nodes containing the needed features.
    """
    global taxidmap_file
    file = taxidmap_file

    for n in t.traverse( strategy = 'postorder' ):
        if not n.is_leaf():
            genes_arr = ["trnX", "trnS1", "trnF", "trnD", "trnY", "trnS2", "trnL1", "trnL2", "trnH", "trnI", "trnM", "trnN", "trnC", "trnE", "trnP", "trnQ", "trnR", "trnT", "trnW", "trnK", "trnA", "trnG", "trnV"]
            # genes_arr = ["trnL1","trnL2"]
            data = {k: {'model':'', 'seq':'', 'structure':'', 'best_alignemnt':''} for k in genes_arr}
            n.add_feature( 'arr', data )
    return t



def initialize_leaves( t, data_array, outdir ):

    """
    go through all the nodes of tree and fill up the data from data_array as a feature for the node
    @param[in] tree
    @param[in] dictionary of data read from MITOS pkl files.
    @param[in] output directory
    
    return a tree which contains nodes containing the needed features.
    """
    global taxidmap_file

    for n in t.traverse( strategy = 'postorder' ):

        if get_NC( taxidmap_file, n.name ) in data_array:
            n.add_feature( "arr", data_array[get_NC( taxidmap_file, n.name )] )


        n.add_feature( 'acc', get_NC( taxidmap_file, n.name ) )

    return t


def remolding_in_species_tree( t ):  # ## this version includes the tree
    #     remove identity sequences from the alignments. only align one sequence to one model

    # i can do it without going through the whole tree, i can just go through the dictionary where the data is .. the tree is only needed when im working with the in tree remolding
    # # it is only needed in the case where i need to compare with the sister specie

    global taxidmap_file
    for nd in t:
        for g1 in nd.arr:  # to get the gene seq
            for g2 in nd.arr:  # to get the model
                if not os.path.isfile( work_dir + "fasta_files/" + nd.name + "_" + g1 + ".fas" ):
                    f = open( work_dir + "fasta_files/" + nd.name + "_" + g1 + ".fas", "w" )
                    # f.write("> "+nd.name+"_"+g1+"\n"+nd.arr[g1]['seq']+"\n")
                    # f.write("> "+nd.name+"_"+g2+"\n"+nd.arr[g2]['seq']+"\n")
                    f.write( nd.arr[g1]['seq'] + "\n" )
                    # f.write(nd.arr[g2]['seq']+"\n")
                    f.close()
                # aligning with model of gene2


                os.system( 'cmalign \"' + nd.arr[g2]['model'] + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + g1 + '.fas\" > ' + work_dir + 'stockholm_files/' + nd.name + '_' + g1 + 'cm_' + g2 + '.sth ' )
                os.system( 'cmalign --sfile ' + work_dir + 'remolding/score_files/' + nd.name + '_' + g1 + '_cm_' + g2 + '.sth \"' + nd.arr[g2]['model'] + '\" \"' + work_dir + 'fasta_files/' + nd.name + '_' + g1 + '.fas\" ' )

                file = open( work_dir + 'remolding/score_files/' + nd.name + '_' + g1 + '_cm_' + g2 + '.sth', 'r' )
                score1 = 0
                for line in file:
                    if not line.startswith( "#" ):

                        temp = line.split()
                        score1 = float( temp[6] )
                file.close()

                with open( work_dir + "remolding/bit_scores.txt", "a" ) as remf:
                    #            accession                        taxid    gene_sequence    model    score
                    remf.write( get_NC( taxidmap_file, nd.name ) + " " + nd.name + " " + g1 + " " + g2 + "  " + str( score1 ) + "\n" )



def cm_call( model, fasta_file, sth_file ):
    # print '/opt/bin/cmalign ' + model+ ' '+fasta_file+' > '+sth_file
    # print '/opt/bin/cmalign --sfile '+sth_file +' '+ model + ' '+fasta_file

    # os.system('/opt/bin/cmalign ' + model+ ' '+fasta_file+' > '+sth_file)
    if not os.path.isfile( sth_file ):
        os.system( 'cmalign --sfile ' + sth_file + ' ' + model + ' ' + fasta_file )



def species_no_trna():
    import ast
    outfile = open( "species_zero_trna.txt", "w" )
    ofile = open( "remolding/missing_trnas.txt", "r" )
    for line in ofile:
        line = line.split( "set" )
        lst = ast.literal_eval( line[1] )
        acc = line[0].split( " " )[0]
        outfile.write( acc + "    " + str( len( lst ) ) + "\n" )
    ofile.close()
    outfile.close()

def remolding_in_species( pool, dat_trna ):  # ## this version DOES NOT includes the tree
    #     remove identity sequences from the alignments. only align one sequence to one model
    genes_arr = ["trnS1", "trnF", "trnD", "trnY", "trnS2", "trnL1", "trnL2", "trnH", "trnI", "trnM", "trnN", "trnC", "trnE", "trnP", "trnQ", "trnR", "trnT", "trnW", "trnK", "trnA", "trnG", "trnV"]
    global taxidmap_file
    for acc in dat_trna:
        if len( dat_trna[acc] ) != len( genes_arr ):
            with open( work_dir + "remolding/missing_trnas.txt", "a" ) as missing_trnas:
                missing_trnas.write( acc + " is missing " + str( set( genes_arr ) - set( dat_trna[acc].keys() ) ) + "\n" )

        for g1 in dat_trna[acc]:
            for g2 in dat_trna[acc]:
                if not os.path.isfile( work_dir + "fasta_files/" + acc + "_" + g1 + ".fas" ):
                    f = open( work_dir + "fasta_files/" + acc + "_" + g1 + ".fas", "w" )

                    f.write( "> " + acc + "_" + g1 + "\n" + dat_trna[acc][g1]['seq'] + "\n" )

                    f.close()
                # aligning with model of gene2
                # os.system('/opt/bin/cmalign \"' + dat_trna[acc][g2]['model'] + '\" \"'+work_dir+'fasta_files/' + acc + '_' + g1 + '.fas\" > '+work_dir+'stockholm_files/' + acc + '_' + g1+ 'cm_'+g2 + '.sth ')
                # os.system('/opt/bin/cmalign --sfile '+work_dir+'remolding/score_files/' + acc + '_' + g1+ '_cm_'+g2+ '.sth \"' + dat_trna[acc][g2]['model'] + '\" \"'+work_dir+'fasta_files/' + acc + '_' + g1+ '.fas\" '

                pool.apply_async( cm_call, args = ( dat_trna[acc][g2]['model'], work_dir + 'fasta_files/' + acc + '_' + g1 + '.fas', work_dir + 'remolding/score_files/' + acc + '_' + g1 + '_cm_' + g2 + '.sth' ) )

def get_scores_in_species( dat_trna ):
    """
    accumulates the sequences in fasta format for all tRNAs from the leafs (if tRNA is not missing) to all the nodes of the tree
    if tRNA is missing from a leaf, its ignored from the recursion
    @param[in] tree
    return a tree with all nodes containing sequences (in fasta format) inside the .arr feature
    
    """
    global taxidmap_file
    for acc in dat_trna:
        for g1 in dat_trna[acc]:
            for g2 in dat_trna[acc]:
                print acc, g1, g2
                try:
                    file = open( work_dir + 'remolding/score_files/' + acc + '_' + g1 + '_cm_' + g2 + '.sth', 'r' )
                except:
                    print "Scheisse !!!"
                    continue
                score1 = 0
                for line in file:
                    if not line.startswith( "#" ):

                        temp = line.split()
                        score1 = float( temp[6] )
                file.close()

                with open( outp_dir + "bit_scores.txt", "a" ) as remf:
                    #      accession  gene_sequence  model    score
                    remf.write( acc + " " + g1 + " " + g2 + "  " + str( score1 ) + "\n" )





# ## important : species NC_023272 was missing from in species remolding, it needs to be re calcuated -- 18 MARCH 2014

if __name__ == '__main__':
    usage = "usage: %prog dirs"
    parser = argparse.ArgumentParser( description = usage )
    # parser.add_argument( 'dirs', metavar = 'DIRS', nargs = '+', help = 'directories' )
    parser.add_argument( 'dirs', help = 'dirs' )
    parser.add_argument( 'outdir', help = 'outputdir' )
    args = parser.parse_args()

    alldirs = []
    # print args.dirs
    # MAC
    # for root, dirs, files in os.walk(args.dirs[0]):

     #   for d in dirs:

    #        alldirs.append(os.path.join(root, d))

    random.seed( 42 )
    numpy.seterr( invalid = 'raise' )

    print "Reading tree ..."
    t = Tree( tree_file, format = 8 )
    sys.stderr.write( "load data\n" )
    all_directory = [os.path.join( args.dirs, f ) for f in os.listdir( args.dirs )]  # getting all directories
    data_trna, data_gene = load_data( all_directory )
#     #model_build_trna(data_trna, main_dir)
#     #print t.get_ascii(show_internal=True)


    print "Loading remolding candidates ..."
    remolding_cand = load_remolding_candidates( "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/grubbs_one_direction_remolding_0.05.txt" )
    to_ignore = load_remolding_candidates( "/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/grubbs_one_direction_remolding_all_cand.txt" )
    print "Converting dictionary data ..."
    dict_data = convert_dict( data_trna )




# #     #print dict_data['NC_008142']
# #     #pool = mp.Pool(12)
# #     #remolding_in_species(pool,dict_data)
# #     #model_build_trna(pool,data_trna, main_dir)
# #     #pool.close()
# #     #pool.join()
# #
#     #get_scores_in_species(dict_data)
# #





    print "Initializing non leaves ..."
    t = intialize_non_leaves( t )
    print "Initializing leaves ..."

    t = initialize_leaves( t, dict_data, args.outdir )

    genes_array = ["trnX", "trnS1", "trnF", "trnD", "trnY", "trnS2", "trnL1", "trnL2", "trnH", "trnI", "trnM", "trnN", "trnC", "trnE", "trnP", "trnQ", "trnR", "trnT", "trnW", "trnK", "trnA", "trnG", "trnV"]
#     between_species_dist = open(work_dir+"between_species_distributions.txt","w")
#     print t.get_ascii(show_internal=True)
#     pool = mp.Pool(4)
#     test(pool,t,remolding_cand)
#     pool.close()
#     pool.join()
#     between_species_dist.close()
    # create_distribution_between_species(t,remolding_cand)

            # ## need to be runned one to create the distributions

    # tgenes = ["trnY","trnR","trnT"]
    n = t.get_tree_root()



#     print "Filling up the sequence bags"
#     for g in genes_array:
#         init_leafs_seq(t, g)
#
# # # #     remolding_in_species(t)
# #     for gene in genes_array:
# #         open('ndal.tmp', 'w').close()
# #         computeModels(n, gene)
#
# #     testfile=open('/homes/brauerei/abdullah/Desktop/PhD/python/mtdbnew/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Higgs2003_Paper_test/remolding/test.txt','w')
#     print "Remolding ..."
    remolding_in_tree( t, to_ignore, remolding_cand, read_background_distributions_in_species(), read_background_distributions_between_species() )
#
#     node2leaves = t.get_cached_content()
#     t=fill_remolding_directions(t,"/Users/Abdullah/Documents/PhD/work/Others/mtdb/src/RNAremold/tRNA-phylo/004/tRNA-CM/data/Final_Remolding_Results_Metazoa_new.txt")
#     t.show(my_layout)
