#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import os, sys

class Profane(): 

    @staticmethod
    def find_all(text, substring):
        return [m.start() for m in re.finditer(substring, text)]
    
    @staticmethod
    def compare_scheme(bt, white_hit_list, mode):
        mem = bt
        for wt in white_hit_list:
            if mode == "ignore":
                return True, bt
            elif mode == "preserve":
                if wt[0] <= bt[0] and bt[1] <= wt[1]:
                    return False, None
                elif wt[0] <= bt[0] and wt[1] <= bt[1] and bt[0] < wt[1]:
                    return False, None
                elif bt[0] <= wt[0] and bt[1] <= wt[1] and wt[0] < bt[1]:
                    return False, None
                else :
                    mem = bt
                    continue
            elif mode == "overlap":
                if wt[0] <= bt[0] and bt[1] <= wt[1]:
                    return False, None
                elif wt[0] <= bt[0] and wt[1] <= bt[1] and bt[0] < wt[1]:
                    mem = (wt[1], bt[1])
                    continue
                elif bt[0] <= wt[0] and bt[1] <= wt[1] and wt[0] < bt[1]:
                    mem = (bt[0],wt[0])
                    continue
                else :
                    mem = bt
                    continue
        return True, mem

    @staticmethod
    def _censorProfane(filter_black_list, text, mark):
        censor_text = text
        for tobe_censor in filter_black_list:
            a = tobe_censor[0]
            b = tobe_censor[1]
            censor_part = mark * int((b-a) / (1 if isinstance(censor_text[a:b], str) else 3))
            censor_text = censor_text[:a] + censor_part + censor_text[b:]
        return censor_text

    @staticmethod
    def _filter(black_hit_list, white_hit_list, mode):
        filter_black_list = []
        for bt in black_hit_list:
            result, new_term = Profane.compare_scheme(bt, white_hit_list, mode)
            if result:
                filter_black_list.append(new_term)
        return set(filter_black_list)

    @staticmethod
    def _screenProfane(whitelist, blacklist, text, mode):
        white_hit_list = []
        for white_term in whitelist:
            for hit_id in Profane.find_all(text, white_term):
                white_hit_list.append((hit_id, hit_id + len(white_term)))

        black_hit_list = []
        for profane_term in blacklist:
            for hit_id in Profane.find_all(text, profane_term):
                black_hit_list.append((hit_id, hit_id + len(profane_term)))

        filter_black_list = set([])
        if len(white_hit_list) == 0:
            filter_black_list = set(black_hit_list)
        else:
            filter_black_list = Profane._filter(black_hit_list, white_hit_list, mode)
        return filter_black_list

    @staticmethod
    def _verifyParam(text, whitelist, blacklist, mode):
        assert isinstance(text, str), "text must be string {}".format(type(text))
        for term in whitelist:
            assert isinstance(term, str), "whitelist term must be string : {}".format(term)
        for term in blacklist:
            assert isinstance(term, str), "blacklist term must be string : {}".format(term)
        
        assert mode in ["ignore", "preserve", "overlap"], "mode must be 'ignore', 'preserve', 'overlap'"

    @staticmethod
    def _removeBlacktermSubstring(ProfaneFound):
        removeDupProfaneFound = []
        for i in range(0, len(ProfaneFound)):
            a = ProfaneFound[i]
            substringFound = False
            for j in range(0, len(ProfaneFound)):
                b = ProfaneFound[j]
                if i != j:
                    if b[1] <= a[1] and a[2] <= b[2]:
                        substringFound = True
            if not substringFound:
                removeDupProfaneFound.append(a)
        return removeDupProfaneFound

    @staticmethod
    def censor(text, whitelist = [], blacklist = [],mark = "*", mode = "preserve"):
        Profane._verifyParam(text, whitelist, blacklist, mode)

        whitelist_default = set([])
        with open(os.path.dirname(os.path.abspath(__file__))+"/thai_white_wordlist.txt") as file:
            whitelist_default = set([l.strip() for l in file])
        whitelist_default = whitelist_default | set(whitelist)

        blacklist_default = set([])
        with open(os.path.dirname(os.path.abspath(__file__))+"/thai_profane_wordlist.txt") as file:
            blacklist_default = set([l.strip() for l in file])
        blacklist_default = blacklist_default | set(blacklist)

        filter_black_list = Profane._screenProfane(whitelist_default, blacklist_default, text, mode)

        censored_text = Profane._censorProfane(filter_black_list, text, mark)
        return censored_text
    
    @staticmethod
    def check(text, whitelist = [], blacklist = [], mode = "preserve"):
        Profane._verifyParam(text, whitelist, blacklist, mode)

        whitelist_default = set([])
        with open(os.path.dirname(os.path.abspath(__file__))+"/thai_white_wordlist.txt") as file:
            whitelist_default = set([l.strip() for l in file])
        whitelist_default = whitelist_default | set(whitelist)

        blacklist_default = set([])
        with open(os.path.dirname(os.path.abspath(__file__))+"/thai_profane_wordlist.txt") as file:
            blacklist_default = set([l.strip() for l in file])
        blacklist_default = blacklist_default | set(blacklist)
        filter_black_list = Profane._screenProfane(whitelist_default, blacklist_default, text, mode)

        ProfaneFound = []
        for tobe_censor in filter_black_list:
            fid = tobe_censor[0]
            lid = tobe_censor[1]
            ProfaneFound.append((text[fid:lid],fid,lid))

        ProfaneFound = Profane._removeBlacktermSubstring(ProfaneFound)
        return ProfaneFound

#save
#load
#censor
#detect (yes no)