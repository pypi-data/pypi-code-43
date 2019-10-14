# -*- coding: utf-8 -*-

from lazyme import per_section

with open('10sents.soft') as fin:
    for sentence_attention in per_section(fin):
        # Reading the headerline
        headers = sentence_attention[0]
        sent_id, trg_str, score, src_str, num_src, num_trg = headers
        sent_id, score, num_src, num_trg = int(sent_id), float(score), int(num_src), int(num_trg)

        trg_str = trg_str.split()
        src_str = src_str.split()
