#!/usr/bin/env python
"""                                                                            
Algorithm that lists possible English acronyms from a listed keywords. 
It is inspired by ACRONYM (Acronym CReatiON for You and Me, https://github.com/bacook17/acronym) but unlike ACRONYM this algporithm creates proper acronyms using the first letters keywords in all possible combinations.
Keywords are to be entered separated by spaces (e.g., `large code`). To allow the code to substitute a word with its synonyms, put a `*` in front of the word (e.g., `*good`). It is also possible to group words together by listing them one after another, separeted by commas and no whitespaces, from each group only one word is used in an acronym (e.g., `bike,car`)

Usage: acronym_gen.py <keywords> ... [options]

Options:                                                                       
   -h --help                         Show this screen.
   --forced_words=<words>            List of words (separated by commas) that MUST be part of the acronym (these words should be already included with keywords).
   --min_acronymlength=<N>           Minimum length of the acronym [default: 3]
   --max_letters_to_use=<N>          Sets the maximum number of letters that can be used from the beginning of keywords [default: 5]
   --use_synonyms_for_all            If turned on, all keywords can have synonyms. Note that this can drastically increase the number of results
   --strict=<f>                      Sets how strictly should words be related to English by changing the `nltk` word corpus (0: `words`, 1: `brown`, other: `gutenberg`) [default: None]
"""
from __future__ import print_function
import numpy as np
import nltk
try:
    nltk.corpus.words.ensure_loaded()
    nltk.corpus.brown.ensure_loaded()
    nltk.corpus.gutenberg.ensure_loaded()
    nltk.corpus.wordnet.ensure_loaded()
except LookupError:
    print('Initial downloading of word corpus')
    for d in ['words', 'brown', 'gutenberg', 'wordnet']:
        nltk.download(d)
from docopt import docopt
        

def get_synonyms(word):
    #Get the synonyms for a word from Wordnet
    res = []
    for syn in nltk.corpus.wordnet.synsets(word):
        for l in syn.lemmas():
            res.append(l.name())
    return res
               
#global
combinations=[]

def next_piece_in_word(wordlist, word, group_list, orig_word=None,prev_choices=[],max_letters_to_use=3,):
    #Checks which strings from wordlist matches the beginning of word, using 1-max_letters_to_use size chunks.
    #Recursive code, if it is possible to reconstruct the full word then the appropriate choices are saved to the global variable combinations
    global combinations
    if (orig_word is None):
        orig_word=word
    for j, w in enumerate(wordlist):
        for i in range(np.min([len(w),max_letters_to_use])):
            s=w[0:(i+1)]
            if (s==word[0:(i+1)]): # we have a match
                new_choices=prev_choices[:]
                new_choices.append([w,i]) #each choice is represented by the word we used and the index of the last letter used
                if (len(s)==len(word)): # we have finished the word
                    combinations.append(new_choices) #store solution
                else:
                    #find unique ID of w 
                    new_wordlist=wordlist[group_list!=group_list[j]] #remove the word we have just used, we can't repeat them or any of its dependents (e.g. synonyms)
                    new_group_list = group_list[group_list!=group_list[j]]
                    if len(new_wordlist):
                        new_word=word[(i+1):] #move onto the rest of the word we want to construct
                        #Call recursion
                        next_piece_in_word(new_wordlist, new_word, new_group_list, orig_word=orig_word,\
                                              prev_choices=new_choices,max_letters_to_use=max_letters_to_use)

def main():
    # Get options
    options = docopt(__doc__)    
    keywordlist = [w.lower()  for w in options["<keywords>"]]
    # Handle forced words
    if options["--forced_words"]:
        forced_words = [w.lower()  for w in options["--forced_words"].split(',')]
        # Check if all the forced words are included with keywords
        for fw in forced_words:
            if not np.sum(np.array(keywordlist)==fw):
                print("Forced word "+fw+" not included in keywords, adding it now (may cause errors with other settings).")
                keywordlist.append(fw)
    #Init grouping
    group_list=list(range(len(keywordlist)))
    #Look for grouped words
    temp_keywordlist=keywordlist[:]; temp_group_list=group_list[:]
    for i,w in enumerate(keywordlist):
        if (len(w.split(','))>1):
            temp_keywordlist.remove(w)
            groupid=group_list[i]
            temp_group_list.remove(groupid)
            for w2 in w.split(','):
                temp_keywordlist.append(w2)
                temp_group_list.append(groupid)
    keywordlist=temp_keywordlist[:]; group_list=temp_group_list[:]
    # Look for words that allow synonyms
    if options["--use_synonyms_for_all"]:
        use_synonyms = np.full(len(keywordlist),True)
    else:
        use_synonyms = np.full(len(keywordlist),False)
        for i,w in enumerate(keywordlist):
            if (w[0]=='*'):
                use_synonyms[i]=True
                keywordlist[i]=w[1:]

    min_acronymlength=int(options["--min_acronymlength"])
    max_letters_to_use=int(options["--max_letters_to_use"])
    strict=options["--strict"]
    if (strict!='None'): strict=int(strict)
    #init global    
    global combinations
    combinations = []
    #Add synonyms if needed, note that this will add a LOT of new results many using synonyms of the same word several times
    if np.sum(use_synonyms):
        temp_keywordlist=keywordlist[:]
        temp_group_list=group_list[:]
        for i, w in enumerate(keywordlist):
            if use_synonyms[i]:
                syns=get_synonyms(w)
                for s in syns:
                    if (s.isalpha()):
                        temp_keywordlist.append(s.lower())
                        temp_group_list.append(group_list[i])
        temp_keywordlist, uniq_idx=np.unique(temp_keywordlist,return_index=True)
        keywordlist=temp_keywordlist[:]
        group_list = np.array(temp_group_list)[uniq_idx]
    #Print keywords
    print("Using %d keywords: "%(len(keywordlist)),' '.join(keywordlist))
    keywordlist=np.array(keywordlist)
    group_list=np.array(group_list)
    if (len(np.unique(group_list))!=len(group_list)):
        print("Keyword groups: ", group_list)
    #Collect all the letters of the alphabet used in keywords, used to filter the words to test
    key_chars=[]
    for w in keywordlist:
        for c in w[0:max_letters_to_use]:
            key_chars.append(c)
    key_chars=np.unique(key_chars)
    #Choose word corpus based on how strict we are with the words we can use
    if strict == 0:
        corpus = nltk.corpus.words
    elif strict == 1:
        corpus = nltk.corpus.brown
    else:
        corpus = nltk.corpus.gutenberg
    #Choose words that have letter that are present in keywords and have at least the minimum length
    word_list = np.unique([w.lower() for w in corpus.words() if w.isalpha() and (len(w)>=min_acronymlength) and set(list(w)).issubset(set(key_chars))])    
    print("Number of words to process %d"%(len(word_list)))
    #See which ones of these can be recovered
    for w in word_list:
        next_piece_in_word(keywordlist, w, group_list, max_letters_to_use=max_letters_to_use)
    #List possible acronyms
    if len(combinations):
        print("Words processed, %d acronyms found, filtering for extra criteria... "%(len(combinations)))
        #List possibilities
        for seq in combinations:
            #Recreate word and choices
            acronym=''
            exp_acronym=''
            for piece in seq:
                capital_part=(piece[0][0:(piece[1]+1)]).upper()
                noncapital_part=(piece[0][(piece[1]+1):]).lower()
                acronym+=capital_part
                exp_acronym+=capital_part+noncapital_part+' '
            used_all_forced_words=True
            if options["--forced_words"]:
                for fw in forced_words:
                    used_all_forced_words&=(fw in exp_acronym.lower())
            if used_all_forced_words:
                print("\t"+acronym+' : '+exp_acronym)
    else:
        print("No appropriate acronyms found.")
        

if __name__ == "__main__": main()
