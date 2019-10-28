"""This module contains wrapper functions for the detection of orthologs."""
import sys
import os
import time
import subprocess
import itertools
from collections import deque
import shutil
import multiprocessing as mp
import numpy as np
import pickle
from scipy.sparse import dok_matrix, csr_matrix, triu, save_npz, load_npz
from typing import Dict, List, Deque, Any, Tuple, Set

# Internal modules
from sonicparanoid import sys_tools as systools
from sonicparanoid import seq_tools as seqtools
# import the module for orthology prediction
from sonicparanoid import inpyranoid
from sonicparanoid import workers
from sonicparanoid import hdr_mapping as idmapper
from sonicparanoid import graph_c as graph
from sonicparanoid import mcl_c as mcl
from sonicparanoid import orthogroups
from sonicparanoid import essentials_c as essentials


__module_name__ = "Ortholog detection"
__source__ = "ortholog_detection.py"
__author__ = "Salvatore Cosentino"
#__copyright__ = ""
__license__ = "GPL"
__version__ = "2.8"
__maintainer__ = "Cosentino Salvatore"
__email__ = "salvo981@gmail.com"



def info():
    """This module contains functions for the detection of orthologs."""
    print("MODULE NAME:\t%s"%__module_name__)
    print("SOURCE FILE NAME:\t%s"%__source__)
    print("MODULE VERSION:\t%s"%__version__)
    print("LICENSE:\t%s"%__license__)
    print("AUTHOR:\t%s"%__author__)
    print("EMAIL:\t%s"%__email__)



def extract_ortholog_pairs(rootDir=os.getcwd(), outDir=os.getcwd(), outName=None, pairsFile=None, coreOnly=False, singleDir=False, tblPrefix="table", splitMode=False, debug=False):
    """Create file containing all generated ortholog pairs."""
    if debug:
        print("extract_ortholog_pairs :: START")
        print("Root directory:\t%s"%rootDir)
        print("Output directory:\t%s"%outDir)
        print("Output file name:\t%s"%outName)
        print("Species pairs file:\t%s"%pairsFile)
        print("Core only:\t%s"%coreOnly)
        print("All tables in same directory:\t{:s}".format(str(singleDir)))
        print("Table file prefix:\t{:s}".format(tblPrefix))
        # keep only first part of the gene id after splitting on the "_" character (if any)
        print("Split mode:\t%s"%splitMode)
    #fetch result files tables
    tblList = fetch_inparanoid_tables(rootDir=rootDir, outDir=outDir, pairsFile=pairsFile, tblPrefix=tblPrefix, singleDir=singleDir, debug=debug)
    totRead = tblCnt = 0
    coreClstrMissCnt = 0
    #extract the project name from the root
    projName: str = ""
    # NOTE: rtemove this since it not required
    if rootDir[-1] == "/":
        projName = rootDir.rsplit("/", 2)[-2]
    else:
        projName = rootDir.rsplit("/", 2)[-1]
    if outName is None:
        if coreOnly:
            outName = "%s_core_relations.tsv"%projName
        else:
            outName = "%s_all_relations.tsv"%projName
    #create output directory if required
    systools.makedir(outDir)
    #output file
    outTbl = os.path.join(outDir, outName)
    # this dictionary is to avoid repetition among the non-core pairs
    repeatTrap = {}
    ortho1All: List[str] = []
    ortho2All: List[str] = []
    orthoScoresDict: Dict[str, float] = {}
    print("Creating file with homolog pairs...")
    #create output file
    ofd = open(outTbl, "w")
    for path in tblList:
        if os.path.isfile(path):
            if debug:
                print(path)
            if os.path.basename(path).startswith(tblPrefix) or singleDir:
                tblCnt += 1
                for clstr in open(path):
                    if clstr[0] == "O":
                        continue
                    totRead += 1
                    clusterID, score, orto1, orto2 = clstr.rstrip().split("\t")
                    #count the cases
                    ortho1All = orto1.rstrip().split(" ")
                    ortho2All = orto2.rstrip().split(" ")
                    #will associate scores to ortholog genes
                    orthoScoresDict.clear()
                    for i, gene in enumerate(ortho1All):
                        if i % 2 == 0:
                            if splitMode:
                                orthoScoresDict[gene.split("_", 1)[1]] = round(float(ortho1All[i + 1]), 2)
                            else:
                                orthoScoresDict[gene] = round(float(ortho1All[i + 1]), 2)
                    #now the second part of the cluster...
                    for i, gene in enumerate(ortho2All):
                        if i % 2 == 0:
                            if splitMode:
                                orthoScoresDict[gene.split("_", 1)[1]] = round(float(ortho2All[i + 1]), 2)
                            else:
                                orthoScoresDict[gene] = round(float(ortho2All[i + 1]), 2)
                    #make lists with gene ids
                    ortho1list: List[str] = []
                    #extract genes for ortho1
                    for i, gene in enumerate(ortho1All):
                        if i % 2 == 0:
                            if splitMode:
                                ortho1list.append(gene.split("_", 1)[1])
                            else:
                                ortho1list.append(gene)
                    #extract genes for ortho2
                    ortho2list: List[str] = []
                    #extract genes for ortho1
                    for i, gene in enumerate(ortho2All):
                        if i % 2 == 0:
                            if splitMode:
                                ortho2list.append(gene.split("_", 1)[1])
                            else:
                                ortho2list.append(gene)
                    #write the pairs in the output file
                    if coreOnly: #add only the ortholog relation with 1.0 as score
                        #check the the score is 1.0
                        pairFound = False
                        for orto1gene in ortho1list:
                            if orthoScoresDict[orto1gene] == 1.0:
                                for orto2gene in ortho2list:
                                    #count the core relations written
                                    if orthoScoresDict[orto2gene] == 1.0:
                                        ofd.write("%s\t%s\n"%(orto1gene, orto2gene))
                                    pairFound = True
                        if not pairFound:
                            if debug:
                                print("WARNING: the CORE pair was not found:\n%s"%clstr)
                            coreClstrMissCnt += 1
                    else: #write all the ortholog relations
                        for orto1gene in ortho1list:
                            for orto2gene in ortho2list:
                                tmpPair = "%s-%s"%(orto1gene, orto2gene)
                                if not tmpPair in repeatTrap:
                                    repeatTrap[tmpPair] = None
                                    ofd.write("%s\t%s\n"%(orto1gene, orto2gene))
    ofd.close()

    # remove not required data structures
    del ortho1All, ortho2All, ortho2list, ortho1list, orthoScoresDict
    # sort the output file alphabetically
    from sh import sort
    tmpSortPath = os.path.join(outDir, "tmp_sorted_orthologs.tsv")
    # sort using sh
    print("Sorting homolog pairs...")
    sort(outTbl, "-o", tmpSortPath)
    # remove the original ortholog pairs file
    os.remove(outTbl)
    # rename the sorted file to the original output name
    os.rename(tmpSortPath, outTbl)
    if debug:
        print("Total clusters read:\t%d"%totRead)
        print("Repeated pairs:\t{:d}".format(len(repeatTrap)))
        if coreOnly:
            print("Total CORE clusters read:\t%d"%(totRead - coreClstrMissCnt))
    # write the number of ortholog relations in created
    from io import StringIO
    from sh import wc
    buf = StringIO()
    wc("-l", outTbl, _out=buf)
    pairsCnt = buf.getvalue().strip().split(" ", 1)[0]
    print("Total orthologous relations\t{:s}".format(pairsCnt))



def fetch_inparanoid_tables(rootDir=os.getcwd(), outDir=os.getcwd(), pairsFile=None, tblPrefix="table", singleDir=False, debug=False) -> List[str]:
    """Find result inparanoid table files for each proteome pair."""
    import fnmatch
    if debug:
        print("fetch_inparanoid_tables :: START")
        print("Root directory:\t%s"%rootDir)
        print("Output directory:\t%s"%outDir)
        print("Species pairs file:\t%s"%pairsFile)
        print("Table prefix:\t%s"%tblPrefix)
        print("Pairwise table are stored all in the same directory:\t{:s}".format(str(singleDir)))
        # the output table prefix can be "table" for ortholog tables, or "Output" for tables with bitscores
    #check that the input directory is valid
    if not os.path.isdir(rootDir):
        sys.stderr.write("ERROR: the directory containing the table files\n%s\n does not exist.\n"%rootDir)
        sys.exit(-2)
    if not os.path.isfile(pairsFile):
        sys.stderr.write("ERROR: you must provide a valid file containing all the species pairs\n")
        sys.exit(-2)
    #create the output directory if does not exist yet
    if outDir[-1] != "/":
        outDir += "/"
    systools.makedir(outDir)
    #load the species names
    pairs: Set[str] = set()
    foundPairs: Set[str] = set()
    #enter the root directory
    prevDir = os.getcwd()
    os.chdir(rootDir)
    #find the inparanoid table files
    fileList: str = []
    pair: str = ""
    runPath: str = ""
    tblName: str = ""

    for pair in open(pairsFile):
        pair = pair[:-1]
        pairs.add(pair)
        #make the file paths
        if singleDir:
            runPath = rootDir
        else:
            runPath = os.path.join(rootDir, pair)
        # set the table name
        if len(tblPrefix) == 0:
            tblName = pair
        else:
            tblName = "{:s}.{:s}".format(tblPrefix, pair)
        if os.path.isdir(runPath):
            tblPath = os.path.join(runPath, tblName)
            if os.path.isfile(tblPath):
                fileList.append(tblPath)
                if debug:
                    print(tblPath)
                foundPairs.add(pair)
    #check that the found tables and the species-pairs count are same
    if len(foundPairs) != len(pairs):
        sys.stderr.write("ERROR: the number of ortholog tables found (%d) and the number of species pairs (%d) must be the same.\n"%(len(foundPairs), len(pairs)))
        print("\nMissing ortholog tables for pairs:")
        # check which pair is missing
        missingSet: Set[str] = set()
        # fill the set with the missing pairs
        [missingSet.add(p) for p in pairs if p not in foundPairs]
        print(" ".join(missingSet))
        sys.exit(-4)
    #reset the current directory to the previous one
    os.chdir(prevDir)
    if debug:
        print("Found tables:\t%d"%len(fileList))
    #return the final list
    return fileList



def identify_required_aln_and_tbls(protCntDict: Dict[str, int], spSizeDict: Dict[str, int], runDir: str, alignDir: str, tblDir: str, owTbls: bool = False, owAll: bool = False, debug: bool = False) -> Tuple[int, int, int]:
    from math import log2
    """Create matrixes with required (fast and slow) alignments and tables"""
    if debug:
        print("\nidentify_required_aln_and_tbls :: START")
        print("Input proteomes:\t{:d}".format(len(protCntDict)))
        print("Proteome sizes:\t{:d}".format(len(spSizeDict)))
        print("Run directory: {:s}".format(runDir))
        print("Directory with alignments: {:s}".format(alignDir))
        print("Directory with pairwise-orthologs: {:s}".format(tblDir))
        print("Overwrite ortholog tables:\t{:s}".format(str(owTbls)))
        print("Overwrite everything:\t{:s}".format(str(owAll)))

    # initialize some variables
    proteomes: int = len(protCntDict)
    spList: List[int] = [int(x) for x in list(protCntDict.keys())]
    spList.sort()
    alnCntCicle1: int = 0
    alnCntCicle2: int = 0
    orthoTblsCnt: int = 0

    # set the overwite table if required
    if owAll:
        owTbls = True

    # load matrix with fast combinations
    fastMtxPath: str = os.path.join(runDir, "fast_aln_mtx.npz")
    tmpM = load_npz(fastMtxPath)

    # initialize the matrixes with required alignments
    dueCicle1Mtx = dok_matrix(tmpM.shape, dtype=np.single)
    dueCicle2Mtx = dok_matrix(tmpM.shape, dtype=np.single)

    # get indexes with non-zero values
    lM, cM = tmpM.nonzero()

    # tmp indexes for the matrix
    l: int = -1
    c: int = -1
    tmpW: float = 0.
    tmpA: str = ""
    tmpB: str = ""
    tmpPath: str = ""
    tmpFilePath: str = ""

    # fill the matrixes with required alignments
    for tpl in zip(lM, cM):
        l = tpl[0]
        c = tpl[1]
        tmpA = str(l + 1)
        tmpB = str(c + 1)
        tmpPath = os.path.join(alignDir, "{:s}-{:s}".format(tmpA, tmpB))
        # compute weight as follows
        # log2(avg_size(A, B) * avg_count(A, B))
        tmpW = round(log2(((protCntDict[tmpA] + protCntDict[tmpB]) * (spSizeDict[tmpA] + spSizeDict[tmpB])) / 4.), 6)

        if owAll: # perform the alignments regardless
            # whipe the directory with alignments
            for f in os.listdir(alignDir):
                tmpFilePath = os.path.join(alignDir, f)
                try:
                    if os.path.isfile(tmpFilePath):
                        os.remove(tmpFilePath)
                    elif os.path.isdir(tmpFilePath):
                        shutil.rmtree(tmpFilePath)
                except Exception as e:
                    print(e)
            # add the elements to the 2 matrixes
            dueCicle1Mtx[l, c] = tmpW
            dueCicle2Mtx[c, l] = tmpW
        else: # perform only missing alignments
            # add element in matrix if the alignment does not exist (search also for the gz file)
            if os.path.isfile(tmpPath) or os.path.isfile("{:s}.gz".format(tmpPath)):
                # do nothing
                pass
            else:
                # add the element in the matrix
                dueCicle1Mtx[l, c] = tmpW

            # check if the other pair alignment exists
            tmpPath = os.path.join(alignDir, "{:s}-{:s}".format(tmpB, tmpA))
            if os.path.isfile(tmpPath) or os.path.isfile("{:s}.gz".format(tmpPath)):
                # do nothing
                pass
            else:
                # add the element in the matrix
                dueCicle2Mtx[c, l] = tmpW

    # add within alignements if required
    # Give 10% higher weights to within alignments
    for sp in spList:
        tmpPath = os.path.join(alignDir, "{:d}-{:d}".format(sp, sp))
        tmpA = str(sp)

        if owAll:  # perform the alignments regardless of their existance
            dueCicle1Mtx[sp-1, sp-1] = round(log2(protCntDict[tmpA] * spSizeDict[tmpA]) * 1.3, 6)
            # remove the alignment file if it exists
            try:
                if os.path.isfile(tmpFilePath):
                    os.remove(tmpFilePath)
                elif os.path.isdir(tmpFilePath):
                    shutil.rmtree(tmpFilePath)
            except Exception as e:
                    print(e)
        else:
            if os.path.isfile(tmpPath) or os.path.isfile("{:s}.gz".format(tmpPath)):
                # due nothing
                pass
            else:
                tmpA = str(sp)
                dueCicle1Mtx[sp-1, sp-1] = round(log2(protCntDict[tmpA] * spSizeDict[tmpA]) * 1.3, 6)

    # update the counters
    alnCntCicle1: int = dueCicle1Mtx.nnz
    alnCntCicle2: int = dueCicle2Mtx.nnz

    if debug:
        print("\nRequired alignments (Cicle1)")
        print(dueCicle1Mtx.todense())
        print("\nRequired alignments (Cicle2)")
        print(dueCicle2Mtx.todense())
        print("\nAll Fast alignments")
        print(tmpM.todense())

    # store the matrixes
    dueCicle1Mtx = dueCicle1Mtx.tocsr()
    save_npz(os.path.join(runDir, "due_aln_mtx1.npz"), dueCicle1Mtx, compressed=False)
    dueCicle2Mtx = dueCicle2Mtx.tocsr()
    save_npz(os.path.join(runDir, "due_aln_mtx2.npz"), dueCicle2Mtx, compressed=False)

    # remove the matrixes
    del tmpM
    del dueCicle1Mtx
    del dueCicle2Mtx

    # initialize the matrixes with required orthology inference
    dueOrthoMtx = dok_matrix((proteomes, proteomes), dtype=np.single)

    # For each combination fill the matrix depending if the ortholog table exists or not
    for tpl in list(itertools.combinations(spList, r=2)):
        l = tpl[0]
        c = tpl[1]
        tmpA = str(l)
        tmpB = str(c)
        tmpPath = os.path.join(tblDir, "{:s}-{:s}/table.{:s}-{:s}".format(tmpA, tmpB, tmpA, tmpB))

        if owTbls:
            tmpW = round(log2(((protCntDict[tmpA] + protCntDict[tmpB]) * (spSizeDict[tmpA] + spSizeDict[tmpB])) / 4.), 6)
            dueOrthoMtx[l-1, c-1] = tmpW
        # add element in matrix if the alignment does not exist (search also for the gz file)
        elif not os.path.isfile(tmpPath):
            # compute weight as follows
            # log2(avg_size(A, B) * avg_count(A, B))
            tmpW = round(log2(((protCntDict[tmpA] + protCntDict[tmpB]) * (spSizeDict[tmpA] + spSizeDict[tmpB])) / 4.), 6)
            dueOrthoMtx[l-1, c-1] = tmpW

    # store the matrixes
    dueOrthoMtx = dueOrthoMtx.tocsr()
    save_npz(os.path.join(runDir, "due_orthology_inference_mtx.npz"), dueOrthoMtx, compressed=False)

    orthoTblsCnt: int = dueOrthoMtx.nnz

    if debug:
        print("\nRequired ortholog tables:")
        print(dueOrthoMtx.todense())

    if debug:
        sys.stdout.write("Alignments required (cicle2):\t{:d}\n".format(alnCntCicle1))
        sys.stdout.write("\nAlignments required (cicle1):\t{:d}\n".format(alnCntCicle2))
        sys.stdout.write("Total required alignments:\t{:d}\n".format(alnCntCicle2 + alnCntCicle1))
        sys.stdout.write("\nOrtholog tables required:\t{:d}\n".format(orthoTblsCnt))

    del dueOrthoMtx

    # return the count of alignments and tables required
    return (alnCntCicle1, alnCntCicle2, orthoTblsCnt)



def prepare_aln_jobs(mtxPath: str, threads: int = 4, debug: bool = False) -> Dict[str, float]:
    """Load the alignments or values from a table, and sort based on scores."""
    if debug:
        print("\nprepare_aln_jobs :: START")
        print("Job-matrix path: {:s}".format(mtxPath))
        print("Threads: {:d}".format(threads))

    # accessory variables
    requiredSpSet: Set[int] = set()
    requiredJobsDict: Dict[str, float] = {}
    proteomes: int = -1
    tmpA: int = 0
    tmpB: int = 0
    tmpPair: str = ""
    tmpW: float = -1.
    jobsCnt: int = -1
    pairsCnt: int = -1

    # load the matrix with fast alignments
    tmpM = load_npz(mtxPath)
    proteomes = tmpM.shape[0]
    lM, cM = tmpM.nonzero()

    # add the entries in the dictionary with alignments
    if debug:
        print("Jobs to be performed:\t{:d}".format(len(lM)))
    for tpl in zip(lM, cM):
        tmpA = tpl[0] + 1
        tmpB = tpl[1] + 1
        tmpW = tmpM[tpl]
        tmpPair = "{:d}-{:d}".format(tmpA, tmpB)
        # fill the dictionary
        requiredJobsDict[tmpPair] = tmpW

        # fill the set with species
        if len(requiredSpSet) < proteomes:
            if not tmpA in requiredSpSet:
                requiredSpSet.add(tmpA)
            if not tmpB in requiredSpSet:
                requiredSpSet.add(tmpB)

    pairsCnt = len(requiredJobsDict)
    del tmpM

    # add the job in chunks using triangular numbers
    if len(requiredJobsDict) > 0:
        # sort the alignments so that the biggest ones are performed first
        s: List[Tuple[str, float]] = [(k, requiredJobsDict[k]) for k in sorted(requiredJobsDict, key=requiredJobsDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        requiredJobsDict.clear()
        requiredJobsDict = {key: value for (key, value) in s}
        del s

        # fill the deque
        dqAlign = deque(maxlen=pairsCnt)
        for p, w in requiredJobsDict.items():
            dqAlign.append((p, w))

        pairsCnt = len(requiredJobsDict)
        jobsCnt = 0
        n: int = 1
        triangularNum: int = 0
        chunkList: List[int] = []  # will contain the sizes of chunks that will fill the job queue
        # now create a list with the chunk sizes
        while jobsCnt < pairsCnt:
            n += 1
            triangularNum = int((n * (n + 1)) / 2.)
            jobsCnt += triangularNum
            chunkList.append(triangularNum)

        # sort the list of chunks in inverted order
        chunkList.sort(reverse=True)
        # remove the biggest chunk
        chunkList.pop(0)
        # invert the list with chunks
        chunkListInv: List[int] = []
        for el in chunkList:
            chunkListInv.append(el)
        chunkListInv.sort()

        # set the step to half of the cpus
        heavyChunkSize: int = int(threads / 2.)

        if heavyChunkSize == 0:
            heavyChunkSize = 1
        # update the alignments dictionary
        requiredJobsDict.clear()
        remainingJobs: int = pairsCnt

        while remainingJobs > 0:
            # add the chunk of jobs that require a lot of memory
            for i in range(0, heavyChunkSize):
                if len(dqAlign) > 0:
                    p, w = dqAlign.popleft()
                    requiredJobsDict[p] = w
                    remainingJobs -= 1  # decrement
                else:  # no more elements to be added
                    break

            # add a chunk of small jobs
            if len(chunkList) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkList.pop(0)
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, w = dqAlign.pop()
                            requiredJobsDict[p] = w
                            remainingJobs -= 1  # decrement
                        else:  # no more elements to be added
                            break
            # add chunks of growing size
            elif len(chunkListInv) > 0:
                if len(dqAlign) > 0:
                    cSize = chunkListInv.pop(0)
                    for i in range(0, cSize):
                        if len(dqAlign) > 0:
                            p, w = dqAlign.pop()
                            requiredJobsDict[p] = w
                            remainingJobs -= 1  # decrement
                        else:  # no more elements to be added
                            break
    if debug:
        print("Job to be performed:\t{:d}".format(len(requiredJobsDict)))
        print("Involved proteomes:\t{:s}".format(str(requiredSpSet)))

    return requiredJobsDict



def run_sonicparanoid2_multiproc_essentials(inPaths, outDir=os.getcwd(), tblDir=os.getcwd(), threads=4, alignDir=None, mmseqsDbDir=None, create_idx=True, sensitivity=4.0, cutoff=40, confCutoff=0.05, lenDiffThr=0.5, overwrite_all=False, overwrite_tbls=False, update_run=False, keepAlign=False, essentialMode=True, debug=False) -> Tuple[str, str, Dict[str, int]]:
    """Execute sonicparanoid, using MMseqs2 if required for all the proteomes in the input directory."""
    import copy
    from math import log2
    if debug:
        print("\nrun_sonicparanoid2_multiproc_essentials :: START")
        print("Input paths:\t{:d}".format(len(inPaths)))
        print("Run directory:{:s}".format(outDir))
        print("Pairwise-ortholog directory:{:s}".format(tblDir))
        print("CPUs:\t{:d}".format(threads))
        print("Directory with alignment: {:s}".format(alignDir))
        print("MMseqs2 database directory:{:s}".format(mmseqsDbDir))
        print("Index MMseqs2 databases:\t{:s}".format(str(create_idx)))
        print("MMseqs2 sensitivity (-s):\t{:s}".format(str(sensitivity)))
        print("Cutoff:\t{:d}".format(cutoff))
        print("Confidence cutoff for paralogs:\t{:s}".format(str(confCutoff)))
        print("Length difference filtering threshold:\t{:s}".format(str(lenDiffThr)))
        print("Overwrite existing ortholog tables:\t{:s}".format(str(overwrite_tbls)))
        print("Overwrite everything:\t{:s}".format(str(overwrite_all)))
        print("Update an existing run:\t{:s}".format(str(update_run)))
        print("Keep raw MMseqs2 alignments:\t{:s}".format(str(keepAlign)))
        print("Essential mode:\t{:s}".format(str(essentialMode)))

    # directory with the input files
    inDir: str = os.path.dirname(inPaths[0])
    #check cutoff and woed size
    if cutoff < 40:
        cutoff = 40

    # accessory variables
    reqAln1Cnt: int = 0
    reqAln2Cnt: int = 0
    reqOrthoTblsCnt: int = 0

    # check that file with info on input file exists
    spFile = os.path.join(outDir, "species.tsv")
    if not os.path.isfile(spFile):
        sys.stderr.write("\nERROR: the species file ({:s}) could not be found.".format(os.path.basename(spFile)))
        sys.stderr.write("\nMake sure the species file is created before proceeding.\n")
        sys.exit(-2)

    # load proteomes sizes and protein lengths
    spSizeDict: Dict[str, int] = {}
    with open(os.path.join(outDir, "proteome_sizes.pckl"), "rb") as fd:
        spSizeDict = pickle.load(fd)
    protCntDict: Dict[str, int] = {}
    with open(os.path.join(outDir, "protein_counts.pckl"), "rb") as fd:
        protCntDict = pickle.load(fd)

    # generate the combinations
    spList = list(spSizeDict.keys())
    spPairsFile = os.path.join(outDir, "species_pairs.tsv")
    spPairs: List[str] = list(itertools.combinations(spList, r=2))

    # create a matrix that contains the combinations
    # this will be used as a control to decide if the master matrix can be created
    spListInt: List[int] = [int(x) for x in spList]  # convert the strings to integers
    spListInt.sort()
    maxSp: int = max(spListInt)
    M = dok_matrix((maxSp, maxSp), dtype=np.int8)
    # generate the combinations
    tplsList: List[Tuple[int, int]] = list(itertools.combinations(spListInt, r=2))
    # Fill the matrix
    for tplInt in tplsList:
        M[tplInt[0]-1, tplInt[1]-1] = 1
    # store to a npz file
    M = M.tocsr()
    M = triu(M, k=0, format="csr")
    combMtxPath = os.path.join(outDir, "combination_mtx.npz")
    save_npz(combMtxPath, M, compressed=False)
    del M
    del spListInt

    #check that the file with genome pairs has not been created yet
    dashedPairs: List[str] = ["{:s}-{:s}".format(tpl[0], tpl[1]) for tpl in spPairs]
    if os.path.isfile(spPairsFile):
        sys.stderr.write("\nWARNING: the species file\n{:s}\nalready exists already you are probably overwriting a previous run...".format(spPairsFile))
    else:
        with open(spPairsFile, "w") as ofd:
            [ofd.write("{:s}\n".format(tmpPair)) for tmpPair in dashedPairs]

    # Predict the fastest pairs
    essentials.predict_fastest_pairs(outDir=outDir, pairs=dashedPairs, protCnts=protCntDict, protSizes=spSizeDict, debug=debug)

    #give some information about the combinations
    print("\nFor the {:d} input species {:d} combinations are possible.".format(len(spList), len(spPairs)))

    # pair for which the ortholog table is missing
    requiredPairsDict: Dict[str, int] = {}
    # will contain the required alignments
    requiredAlignDict: Dict[str, int] = {}

    # identify the alignments and ortholog inference runs that will be performed
    reqAln1Cnt, reqAln2Cnt, reqOrthoTblsCnt = identify_required_aln_and_tbls(protCntDict, spSizeDict, outDir, alignDir, tblDir, overwrite_tbls, overwrite_all, debug)
    # Perform required alignments
    if reqAln1Cnt > 0:
        requiredAlignDict = prepare_aln_jobs(os.path.join(outDir, "due_aln_mtx1.npz"), threads, debug)
        # perform the alignments
        workers.perform_mmseqs_multiproc_alignments(requiredAln=requiredAlignDict, inDir=inDir, outDir=alignDir, dbDir=mmseqsDbDir,  runDir=outDir, create_idx=create_idx, sensitivity=sensitivity, cutoff=cutoff, threads=threads, keepAlign=keepAlign, firstCicle=True, debug=debug)
    if reqAln2Cnt > 0:
        requiredAlignDict = prepare_aln_jobs(os.path.join(outDir, "due_aln_mtx2.npz"), threads, debug)
        # perform the alignments
        if essentialMode:
            workers.perform_parallel_essential_alignments(requiredAln=requiredAlignDict, protCntDict=protCntDict, runDir=outDir, alnDir=alignDir, create_idx=False, sensitivity=sensitivity, cutoff=cutoff, threads=threads, keepAln=keepAlign, debug=False)
        else:
            workers.perform_mmseqs_multiproc_alignments(requiredAln=requiredAlignDict, inDir=inDir, outDir=alignDir, dbDir=mmseqsDbDir,  runDir=outDir, create_idx=create_idx, sensitivity=sensitivity, cutoff=cutoff, threads=threads, keepAlign=keepAlign, firstCicle=False, debug=debug)

    # Infer required ortholog tables
    if reqOrthoTblsCnt > 0:
        requiredPairsDict = prepare_aln_jobs(os.path.join(outDir, "due_orthology_inference_mtx.npz"), threads, debug)
        tmpA: str = ""
        tmpB: str = ""
        tmpW: float = 0.
        withinAlignDict: Dict[str, List[int, Any, Any]] = {}
        # initialize the dictionary with within
        for pair, weight in requiredPairsDict.items():
            tmpA, tmpB = pair.split("-", 1)
            if not tmpA in withinAlignDict:
                tmpW = round(log2((protCntDict[tmpA] * spSizeDict[tmpA])), 6)
                withinAlignDict[tmpA] = [tmpW, None, None]
            if not tmpB in withinAlignDict:
                tmpW = round(log2((protCntDict[tmpB] * spSizeDict[tmpB])), 6)
                withinAlignDict[tmpB] = [tmpW, None, None]
            if len(withinAlignDict) == maxSp:
                break

        # refill the dictionary by sorting by value
        s = [(k, withinAlignDict[k]) for k in sorted(withinAlignDict, key=withinAlignDict.get, reverse=True)]
        # empty the dictionary and fill it again with the size-sorted one
        withinAlignDict.clear()
        withinAlignDict = {tpl[0]: tpl[1] for tpl in s}
        del s

        # set counters to 0
        for sp in withinAlignDict:
            withinAlignDict[sp] = [0, None, None]

        # fill the dict with required species
        for pair in requiredPairsDict:
            tmpA, tmpB = pair.split("-", 1)
            # increment the counters
            withinAlignDict[tmpA][0] += 1
            withinAlignDict[tmpB][0] += 1

        sys.stdout.write("\nPredicting {:d} ortholog tables...".format(len(requiredPairsDict)))
        # calculate cpu-time for orthology inference
        orthology_start = time.perf_counter()

        ##### USE PREPROCESSING ####
        #### ORIGINAL ####
        # segOverlapCutoff: float = 0.5
        ##################
        segOverlapCutoff: float = 0.25
        # The actual matching segments must cover this of this match of the matched sequence
        # For example for a matched sequence 70 bps long, segments 1-15 and 50-70 gives a total coverage of 35, which is 50% of total.
        segCoverageCutoff: float = 0.25
        # load the required within alignments in parallel
        inpyranoid.preprocess_within_alignments_parallel(withinAlignDict, alignDir=alignDir, threads=threads, covCoff=segCoverageCutoff, overlapCoff=segOverlapCutoff, debug=debug)
        workers.perform_parallel_orthology_inference_shared_dict(requiredPairsDict, inDir, outDir=tblDir, sharedDir=alignDir, sharedWithinDict=withinAlignDict, cutoff=cutoff, confCutoff=confCutoff, lenDiffThr=lenDiffThr, threads=threads, debug=debug)
        sys.stdout.write("\nOrtholog tables creation elapsed time (seconds):\t{:s}\n".format(str(round(time.perf_counter() - orthology_start, 3))))
    # return the paths for species and pairs files
    return (spFile, spPairsFile, requiredPairsDict)
