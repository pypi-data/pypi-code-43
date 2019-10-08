#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
The script intergrates three original scripts edit_margin_length.py and realgn_merge_tx.py.
BAM file will be input use pysam and each line in BAM file will be looped to find the possible missed small exons, with
    the threshold: small_exon_size <= 100 and abs(delta_ratio) <= 0.5. 
The realign region will only be aligned to the exons of the transcript, not compare with intron regions.
"""

import csv
import re
import sys
import time
import warnings

import numpy as np
import pandas as pd
import pysam
import parasail
import collections

from itertools import groupby
from .block_class import (Cigar, Cigar_fromlist, ReadBlock, CigarSliceError)
from .find_small_exon import find_missed_exons


def groupby_unsorted(seq, key_fun=lambda x: x):
    """
    Unsorted version of groupby in itertools
    """
    indexs_dict = collections.defaultdict(list)
    for i, elem in enumerate(seq):
        indexs_dict[key_fun(elem)].append(i)
    for key, idxs in indexs_dict.items():
        yield key, [seq[i] for i in idxs]


def parse_bed(bed_path):
    """
    The function parse an annotation BED file to a dataframe contain list.
    We used to use list of dict as the result.
    [{'tx_i':146, 'chrom':'chrIS', 'strand':'+', 'start':6955486, 'end':6962816, 'name':'R1_101_1', 'block_count':3, 'block_sizes':[243, 116, 360], 'block_starts':[0, 4897, 6970]},
     {...},
     ...
     {...}]
    Actually, the list of dict is easy to be transformed to dataframe by pd.DataFrame(list_dict) and vice versa df.to_dict('records')
    The result dataframe should be sorted by start and end sites.
    """
    bed_col = [
        "chrom", "chromStart", "chromEnd", "name", "score", "strand", 
        "thickStart", "thickEnd", "itemRgb", "blockCount", "blockSizes", "blockStarts"
    ]
    bed = pd.read_csv(bed_path, sep='\t', header=None, names=bed_col,
                      quoting=csv.QUOTE_NONE, dtype={"chrom": str, "blockSizes": str, "blockStarts": str})
    bed["tx_i"] = bed.index
    #
    def parse_row(row):
        row["blockSizes"] = [np.int64(x) for x in row["blockSizes"].split(',')]
        row["blockStarts"] = [np.int64(x)
                              for x in row["blockStarts"].split(',')]
        row["blockNum"] = len(row["blockSizes"])
        return row
    bed = bed.apply(parse_row, axis=1)
    bed_df = pd.DataFrame(bed[["tx_i", "chrom", "strand"]])
    bed_df["tx"] = bed["name"]
    bed_df["start"] = bed["chromStart"]
    bed_df["end"] = bed["chromEnd"]
    bed_df["exon_sizes"] = bed["blockSizes"]
    bed_df["exon_starts"] = bed["blockStarts"]
    bed_df["exon_num"] = bed["blockNum"]
    return bed_df


def extend_tx(tx):
    """
    The function extends the list at exon_sizes and exon_starts in the transcript dataframe into exons.
    One line stands for one exon in the extended result.
    """
    if not all(tx["start"] < tx["end"]):  # We require start < end in the bed_df
        raise Exception("Error: start ≥ end in bed file!")
    exon_starts = tx.apply(
        lambda r: r["start"] + pd.Series(r["exon_starts"]), axis=1)
    exon_ends = tx.apply(
        lambda r: r["start"] + pd.Series(r["exon_starts"]) + pd.Series(r["exon_sizes"]), axis=1)
    exon_starts = exon_starts.stack().reset_index(level=1)
    exon_ends = exon_ends.stack().reset_index(level=1)
    if (not all(exon_starts["level_1"] == exon_ends["level_1"])) or (not all(exon_starts.index == exon_ends.index)):
        raise Exception("Error: extend exon fall!")
    exons = pd.DataFrame(
        {"exon_i": exon_starts["level_1"], "exon_start": exon_starts.iloc[:, 1], "exon_end": exon_ends.iloc[:, 1]}, dtype="int")
    exons = tx.drop(["exon_sizes", "exon_starts"], axis=1).join(exons)
    exons.set_index(["tx_i", "exon_i"], inplace=True)
    return exons


def trace_realign_region(row, read_cigar, read_start):
    """
    The function is used to trace the rdp and ci at the border of realign region and return a dict
    """
    realn_start_t = read_cigar.trace_ci_rdp(start_ci=(0, 0), start_pos=read_start,
                                            end_pos=row["realign_start"], start_rdp=0)
    if not realn_start_t[2]:
        raise Exception("Error: cannot trace to the realign border", row)
    realn_end_t = read_cigar.trace_ci_rdp(start_ci=realn_start_t[0], start_pos=row["realign_start"],
                                          end_pos=row["realign_end"], start_rdp=realn_start_t[1])
    if not realn_end_t[2]:
        raise Exception("Error: cannot trace to the realign border", row)
    return {"realign_start_ci": realn_start_t[0], "realign_end_ci": realn_end_t[0],
            "realign_start_rdp": realn_start_t[1], "realign_end_rdp": realn_end_t[1]}


def edit_margin_len(row, read_cigar):
    """
    The function is used to edit the margin length in the original realign_ss. 
    Margin length is called margin_length in the old file.
    One insertion 'I' or 'D' will +1 or -1 in the margin length.
    """
    cigar_slice = read_cigar.cslice(start_ci=row["realign_start_ci"], end_ci=row["realign_end_ci"])
    new_margin_len = row["margin_len"]
    for n, c in cigar_slice:
        if c == 'D':
            new_margin_len -= n
        elif c == 'I':
            new_margin_len += n
    return new_margin_len


def extend_realign_region(row, read_cigar):
    """
    This part is separated from the original modify_realign_region.

    Because minimap use bonus strategy on the splice site, There might be a long deletion or insertion beside the
    splice site. In case to make sure that the realign start do not begin with a deletion or the realign end do not
    end with a insertion and deletion, we need to extend the boundary of the realign region when the case happen.

    Shown as follows:

    Deletion:
    Start:  ... End:
      # @         @ #
    ATGCA       GCTTC
    AT--A       GC--C
        @           @

    Insertion:
    Start:  ... End:
        @           @
    AT--A       GC--C
    ATGCA       GCTTC
      # @         @ #

    The symbol '@' means the original position of ref_start/end (above the sequence) and query_start/end (below the
    sequence); The symbol '#' means the position after modification.
    """
    try:
        left_slice_group = read_cigar.cslice(end_ci=row["realign_start_ci"])[-1]
        if left_slice_group[1] in {'D', 'I'}:
            if left_slice_group[1] == 'D':
                row["realign_start"] -= left_slice_group[0]
            else:
                row["realign_start_rdp"] -= left_slice_group[0]
            if row["realign_start_ci"][1] == 0:
                row["realign_start_ci"] = (row["realign_start_ci"][0]-1, 0)
            else:
                row["realign_start_ci"] = (row["realign_start_ci"][0], 0)
    except IndexError: # most case because realign_start_ci is (0, 0)
        pass
    try:
        right_slice_group = read_cigar.cslice(start_ci=row["realign_end_ci"])[0]
        if right_slice_group[1] in {'D', 'I'}:
            if right_slice_group[1] == 'D':
                row["realign_end"] += right_slice_group[0]
            else:
                row["realign_end_rdp"] += right_slice_group[0]
            row["realign_end_ci"] = (row["realign_end_ci"][0]+1, 0)
    except IndexError: # most case because realign_end_ci reach the cigar end. 
        pass
    return row


def exclude_soft_clip(row, read_cigar):
    """
    Separated from extend_realign_region, used to exclude the soft clip at the start or end of the query_sequence. 
    Because sometimes realign region might include the softclip region and the softclip region usually is really 
    long which can lead to a wrong realignment result.
    """
    # Exclude the 'S' at both ends of the realign region
    cigar_slice = read_cigar.cslice(start_ci=row["realign_start_ci"], end_ci=row["realign_end_ci"])
    if cigar_slice[0][1] == 'S':
        row["realign_start_rdp"] += cigar_slice[0][0]
        row["realign_start_ci"] = (row["realign_start_ci"][0]+1, 0)
    if cigar_slice[-1][1] == 'S':
        row["realign_end_rdp"] -= cigar_slice[0][0]
        row["realign_end_ci"] = (row["realign_end_ci"][0], 0)
    return row


def modify_realign_region(row, read_cigar, read_start, float_flank_len):
    """
    The function is used to modify the realignment region.
    It also combines the trace, edit margin length and extend realign region process.
    Return: modified realign_ss
    """
    # Tracing process
    trace_dict = trace_realign_region(row[["realign_start", "realign_end", "read_intron_start", 
                                           "read_intron_end"]], read_cigar, read_start)
    row = row.append(pd.Series(trace_dict))
    if float_flank_len:
        # Extend the boundary of realign region
        row = extend_realign_region(row, read_cigar)
    # Exclude soft clip
    row = exclude_soft_clip(row, read_cigar)
    # Editing margin length
    row["margin_len_mod"] = edit_margin_len(row, read_cigar)
    row["delta_ratio_mod"] = (row["margin_len_mod"] - row["sum_exon_size"]) / row["sum_exon_size"]
    return row


def trace_realign_result(row, realign_cigar):
    """
    The function is used to trace the cigar index of introns which are used to split the realign_cigar.
    Return a ci_list.
    realn_tx_pos means the position regardless of introns and relative to the realign_start. The position of
    bases on the tx_seq.
    """
    ci_list = []
    intron_start = row["tx_leftexon_end"]
    realn_tx_pos = row["tx_leftexon_end"]-row["realign_start"]
    realn_intron_pos = [realn_tx_pos]
    for exon_size in row["exon_sizes"]:
        realn_tx_pos += exon_size
        realn_intron_pos.append(realn_tx_pos)
    for realn_tx_pos in realn_intron_pos:
        trace = realign_cigar.trace_ci_rdp(start_ci=(0, 0), start_pos=0, end_pos=realn_tx_pos, start_rdp=0)
        if not trace[2]:
            raise Exception("Error:, cannot trace to the intron position in the realign cigar!") 
        ci_list.append(trace[0])
    return ci_list


def cal_alignment_score(cigar_list, read_seq, ref_seq, cm, mm, go, ge):
    """
    mm, go and ge usually are negative to give penalty.
    """
    score = 0
    pos = 0
    rdp = 0
    for n, c in cigar_list:
        if n < 1:
            raise Exception("Error: list in cigar is not standard!", cigar_list)
        if c == 'M':
            for _ in range(n):
                if read_seq[rdp] == ref_seq[pos]:
                    score += cm
                else:
                    score += mm
                pos += 1
                rdp += 1
        elif c == '=':
            score += cm*n
            pos += n
            rdp += n
        elif c == 'X':
            score += mm*n
            pos += n
            rdp += n
        elif c == 'I':
            score += go + ge*(n-1)
            rdp += n
        elif c == 'D':
            score += go + ge*(n-1)
            pos += n
        elif c == 'N':
            pos += n # we do not give penalty on introns
        else:
            raise Exception("Error: cigar character exceed assumption {'M', '=', 'X', 'I', 'D'}!", c)
    if rdp != len(read_seq) or pos != len(ref_seq):
        raise Exception("Error: input cigar not correspond to read_seq or ref_seq!", '\n',
                        cigar_list, '\n',
                        read_seq, '\n',
                        ref_seq)
    return score


def check_cigar_seq(cigar, read_seq, ref_seq):
    """
    The function is used to check whether the cigar is corresponded to read_seq and ref_seq
    """
    pos = 0
    rdp = 0
    for n, c in cigar.list:
        if c in {'M', 'X', '='}:
            pos += n
            rdp += n
        elif c in {'S', 'I'}:
            rdp += n
        elif c in {'D', 'N'}:
            pos += n
    if rdp != len(read_seq) or pos != len(ref_seq):
        raise Exception("Error: input cigar not correspond to read_seq or ref_seq!", '\n',
                        cigar.list, '\n',
                        read_seq, '\n',
                        ref_seq)
    return 0


def realign_read(read, read_cigar, realign_ss, ref_fa, score_matrix):
    """
    The function realign the region indicated in the realign_ss.
    Suffix rel means relative. pos_rel means the reference position relative to the realign start site.
    pos_rel = pos - realign_start.
    """
    check_cigar_seq(read_cigar, read.query_sequence, ref_fa.fetch(realign_ss["chrom"], start=read.reference_start, end=read.reference_end))
    realign_start = realign_ss["realign_start"]
    realign_end = realign_ss["realign_end"]
    # fetch half-open interval.
    ref_seq = ref_fa.fetch(realign_ss["chrom"], start=realign_start, end=realign_end)
    # tx_seq: part of ref_seq which does not contain intron sequences.
    # Also calculate transcript intron lengths
    intron_lens = []
    intron_start = realign_ss["tx_leftexon_end"]
    tx_seq = ref_seq[:realign_ss["tx_leftexon_end"]-realign_start]
    for s, e in zip(realign_ss["small_exon_starts"], realign_ss["small_exon_ends"]):
        tx_seq += ref_seq[s-realign_start:e-realign_start]
        intron_lens.append(s - intron_start)
        intron_start = e
    intron_lens.append(realign_ss["tx_rightexon_start"] - intron_start)
    tx_seq += ref_seq[realign_ss["tx_rightexon_start"]-realign_start:]
    read_seq = read.query_sequence[realign_ss["realign_start_rdp"]:realign_ss["realign_end_rdp"]]
    realign_result = parasail.nw_trace(read_seq, tx_seq, 1, 1, score_matrix)
    realign_score = realign_result.score
    realign_cigar_str = realign_result.cigar.decode.decode("utf-8")
    # We find the parasail might confuse the "X" with "=", so we convert all "X" and "=" to "M"
    realign_cigar_str = re.sub("[X=]", "M", realign_cigar_str)
    realign_cigar = Cigar(realign_cigar_str)
    realign_cigar.standardize()
    # check cal_alignment_score
    if realign_score != cal_alignment_score(realign_cigar.list, read_seq, tx_seq, 1, -1, -1, -1):
        raise Exception("Error: parasail alignment score different with the calculation!", realign_score,
                        cal_alignment_score(realign_cigar.list, read_seq, tx_seq, 1, -1, -1, -1))
    ori_realn_cigar_list = read_cigar.cslice(start_ci=realign_ss["realign_start_ci"], 
                                             end_ci=realign_ss["realign_end_ci"])
    ori_score = cal_alignment_score(ori_realn_cigar_list, read_seq, ref_seq, 1, -1, -1, -1)
    increase_score = realign_score - ori_score
    realn_intron_cis = trace_realign_result(realign_ss[["tx_leftexon_end", "realign_start", "exon_sizes"]], realign_cigar)
    # joint new cigar
    new_cigar_list = read_cigar.cslice(end_ci=realign_ss["realign_start_ci"])
    start_ci = (0, 0)
    for ci, n in zip(realn_intron_cis, intron_lens):
        new_cigar_list.extend(realign_cigar.cslice(start_ci=start_ci, end_ci=ci))
        new_cigar_list.extend([[n, 'N']])
        start_ci = ci
    new_cigar_list.extend(realign_cigar.cslice(start_ci=start_ci))
    new_cigar_list.extend(read_cigar.cslice(start_ci=realign_ss["realign_end_ci"]))
    new_cigar = Cigar_fromlist(new_cigar_list)
    # check new cigar:
    # check_cigar_seq(new_cigar, read.query_sequence, ref_fa.fetch(realign_ss["chrom"], start=read.reference_start, end=read.reference_end))
    return new_cigar, increase_score


def find_fix_small_exon(
    ori_bam_path, ref_fa_path, annot_bed_path, out_bam_path, out_realign_region_path,
    small_exon_size=100, flank_len=20, ignore_strand=True,
    delta_ratio_thd=0.5, simplify=True, float_flank_len=False, only_region=False
):
    score_matrix = parasail.matrix_create("ACGT", 1, -1)
    start_time = time.process_time()
    ori_bam = pysam.AlignmentFile(ori_bam_path, "rb")
    if not only_region:
        realign_bam = pysam.AlignmentFile(out_bam_path, "wb", template=ori_bam)
    ref_fa = pysam.FastaFile(ref_fa_path)

    annot_bed = parse_bed(annot_bed_path)
    annot_bed = annot_bed[annot_bed["exon_num"] != 1]  # Filter out singleten
    # In order to avoid repetitive computation, we extend the bed file in advance.
    annot_exon = extend_tx(annot_bed)

    filter_list = []
    read_i = 0  # 0 based
    total_intron = 0
    misaligned_read_num = 0
    misaligned_intron_num = 0
    fix_read_num = 0
    fix_intron_num = 0
    for read in ori_bam.fetch(until_eof=True):
        if read.cigarstring is None or read.query_sequence is None:
            if not only_region:
                realign_bam.write(read)
            read_i += 1
            continue
        read_miss_exon_flag = False
        read_fix_flag = False
        read_block = ReadBlock(read, read_i)
        realign_list = find_missed_exons(read_block, annot_bed, annot_exon, ignore_strand=ignore_strand, 
                                         flank_len=flank_len, small_exon_size=small_exon_size)
        if realign_list is not False:
            read_cigar = read_block.cigar
            read_start = read_block.starts[0]
            for ith_intron, realign_intron_group in groupby_unsorted(realign_list, lambda x: x["read_ith_intron"]):
                realn_scores_increase = []
                realn_cigars = []
                delta_ratio_mods_abs = []
                intron_miss_exon_flag = False
                intron_fix_flag = False
                for i in range(len(realign_intron_group)):
                    realign_intron_group[i] = modify_realign_region(realign_intron_group[i], read_cigar, read_start, float_flank_len)
                    delta_ratio_mods_abs.append(abs(realign_intron_group[i]["delta_ratio_mod"]))
                if simplify:
                    min_ind = delta_ratio_mods_abs.index(min(delta_ratio_mods_abs))
                    realign_intron_group = [realign_intron_group[min_ind]]
                for realign_ss in realign_intron_group:
                    # filter with delta_ratio
                    if abs(realign_ss["delta_ratio_mod"]) <= delta_ratio_thd:
                        read_miss_exon_flag = True
                        intron_miss_exon_flag = True
                        filter_list.append(realign_ss)
                        if not only_region:
                            realign_result = realign_read(read, read_cigar, realign_ss, ref_fa, score_matrix)
                            realn_cigars.append(realign_result[0])
                            realn_scores_increase.append(realign_result[1])
                if intron_miss_exon_flag:
                    misaligned_intron_num += 1
                    if not only_region:
                        # when realigned region improve the alignment score, we will keep the realignment with max score.
                        if max(realn_scores_increase) > 0:
                            read_cigar = realn_cigars[realn_scores_increase.index(max(realn_scores_increase))]
                            # check cigar string
                            # read_cigar.getstr()
                            read_fix_flag = True
                            intron_fix_flag = True
                            fix_intron_num += 1
            if not only_region:
                new_cigar_str = read_cigar.getstr()
                read.cigarstring = new_cigar_str
        if not only_region:
            realign_bam.write(read)
        read_i += 1
        total_intron += read_block.introns["intron_num"]
        if read_miss_exon_flag:
            misaligned_read_num += 1
        if read_fix_flag:
            fix_read_num += 1
    if not only_region:
        realign_bam.close()
    ori_bam.close()
    realign_df = pd.DataFrame(filter_list)
    realign_df.to_csv(out_realign_region_path, sep="\t", index=False, quoting=csv.QUOTE_NONE)

    end_time = time.process_time()
    print("Input BAM information:")
    print("\tTotal number of reads:", read_i)
    print("\tTotal number of introns:", total_intron)
    print("The result of finding misaligned exons:")
    if read_i == 0:
        print("\tThe number of misaligned reads:", misaligned_read_num)
    else:
        print("\tThe number of misaligned reads: {0}\tratio: {1:.2f}%".format(
            misaligned_read_num, misaligned_read_num/read_i*100
        ))
    if total_intron == 0:
        print("\tThe number of misaligned introns:", misaligned_intron_num)
    else:
        print("\tThe number of misaligned introns: {0}\tratio: {1:.2f}%".format(
            misaligned_intron_num, misaligned_intron_num/total_intron*100
        ))
    print("The result of realignment:")
    if misaligned_read_num == 0:
        print("\tThe number of fixed reads:", fix_read_num)
    else:
        print("\tThe number of fixed reads: {0}\tratio to misaligned reads: {1:.2f}%".format(
            fix_read_num, fix_read_num/misaligned_read_num*100
        ))
    if misaligned_intron_num == 0:
        print("\tThe number of fixed introns:", fix_intron_num)
    else:
        print("\tThe numberr of fixed introns: {0}\tratio to misaligned introns: {1:.2f}%".format(
            fix_intron_num, fix_intron_num/misaligned_intron_num*100
        ))
    print("Time used: {:.2f}s".format(end_time - start_time))



