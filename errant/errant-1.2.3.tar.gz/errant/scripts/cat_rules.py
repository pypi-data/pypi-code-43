from difflib import SequenceMatcher
from spacy.lemmatizer import Lemmatizer

import spacy.parts_of_speech as spos


class CatRules:
    # Contractions
    CONTS = {"'d", "'ll", "'m", "n't", "'re", "'s", "'ve"}

    # Rare POS tags that make uninformative error categories
    RARE_TAGS = {"INTJ", "NUM", "SYM", "X"}

    # Special auxiliaries in contractions.
    SPECIAL_AUX1 = ({"ca", "can"}, {"sha", "shall"}, {"wo", "will"})
    SPECIAL_AUX2 = {"ca", "sha", "wo"}

    # Open class spacy POS tag objects
    OPEN_POS = (spos.ADJ, spos.ADV, spos.NOUN, spos.VERB)

    # Open class POS tags
    OPEN_TAGS = {"ADJ", "ADV", "NOUN", "VERB"}

    # Some dep labels that map to pos tags.
    DEP_MAP = {"acomp": "ADJ",
               "amod": "ADJ",
               "advmod": "ADV",
               "det": "DET",
               "prep": "PREP",
               "prt": "PART",
               "punct": "PUNCT"}

    @staticmethod
    def auto_type_edit(edit, orig_sent, cor_sent, gb_spell, tag_map, nlp, stemmer):
        """

        :param edit: An edit list. [orig_start, orig_end, cat, cor, cor_start, cor_end]
        :param orig_sent: An original SpaCy sentence.
        :param cor_sent: A corrected SpaCy sentence.
        :param gb_spell: A set of valid GB English words.
        :param tag_map: A dictionary to map PTB tags to Stanford Universal Dependency tags.
        :param nlp: A preloaded spacy processing object.
        :param stemmer: The Lancaster stemmer in NLTK.
        :return: The input edit with new error tag, in M2 edit format.
        """
        # Get the tokens in the edit.
        orig_toks = orig_sent[edit[0]:edit[1]]
        cor_toks = cor_sent[edit[4]:edit[5]]
        # Nothing to nothing is a detected, but not corrected edit.
        if not orig_toks and not cor_toks:
            return "UNK"
        # Missing
        elif not orig_toks and cor_toks:
            op = "M:"
            cat = CatRules.get_one_sided_type(cor_toks, tag_map)
        # Unnecessary
        elif orig_toks and not cor_toks:
            op = "U:"
            cat = CatRules.get_one_sided_type(orig_toks, tag_map)
        # Replacement and special cases
        else:
            # Same to same is a detected, but not corrected edit.
            if orig_toks.text == cor_toks.text:
                return "UNK"
            # Special: Orthographic errors at the end of multi-token edits are ignored.
            # E.g. [Doctor -> The doctor], [The doctor -> Dcotor], [, since -> . Since]
            # Classify the edit as if the last token weren't there.
            elif orig_toks[-1].lower_ == cor_toks[-1].lower_ and \
                    (len(orig_toks) > 1 or len(cor_toks) > 1):
                min_edit = edit[:]
                min_edit[1] -= 1
                min_edit[5] -= 1
                return CatRules.auto_type_edit(min_edit, orig_sent, cor_sent, gb_spell, tag_map, nlp, stemmer)
            # Replacement
            else:
                op = "R:"
                cat = CatRules.get_two_sided_type(orig_toks, cor_toks, gb_spell, tag_map, nlp, stemmer)
        return op + cat

    @staticmethod
    def get_edit_info(toks, tag_map):
        """

        :param toks: Spacy tokens
        :param tag_map: A map dict from PTB to universal dependency pos tags.
        :return: A list of token, pos and dep tag strings.
        """
        str = []
        pos = []
        dep = []
        for tok in toks:
            str.append(tok.text)
            pos.append(tag_map[tok.tag_])
            dep.append(tok.dep_)
        return str, pos, dep

    @staticmethod
    def get_one_sided_type(toks, tag_map):
        """

        :param toks: Spacy tokens.
        :param tag_map: A map dict from PTB to universal dependency pos tags.
        :return: An error type string.
                When one side of the edit is null, we can only use the other side.
        """
        # Extract strings, pos tags and parse info from the toks.
        str_list, pos_list, dep_list = CatRules.get_edit_info(toks, tag_map)

        # Special cases.
        if len(toks) == 1:
            # Possessive noun suffixes; e.g. ' -> 's
            if toks[0].tag_ == "POS":
                return "NOUN:POSS"
            # Contraction. Rule must come after possessive.
            if toks[0].lower_ in CatRules.CONTS:
                return "CONTR"
            # Infinitival "to" is treated as part of a verb form.
            if toks[0].lower_ == "to" and toks[0].pos_ == "PART" and toks[0].dep_ != "prep":
                return "VERB:FORM"
        # Auxiliary verbs.
        if set(dep_list).issubset({"aux", "auxpass"}):
            return "VERB:TENSE"
        # POS-based tags. Ignores rare, uninformative categories.
        if len(set(pos_list)) == 1 and pos_list[0] not in CatRules.RARE_TAGS:
            return pos_list[0]
        # More POS-based tags using special dependency labels.
        if len(set(dep_list)) == 1 and dep_list[0] in CatRules.DEP_MAP.keys():
            return CatRules.DEP_MAP[dep_list[0]]
        # To-infinitives and phrasal verbs.
        if set(pos_list) == {"PART", "VERB"}:
            return "VERB"
        # Tricky cases
        else:
            return "OTHER"

    @staticmethod
    def get_two_sided_type(orig_toks, cor_toks, gb_spell, tag_map, nlp, stemmer):
        """

        :param orig_toks: Original text spacy tokens.
        :param cor_toks: Corrected text spacy tokens.
        :param gb_spell: A set of valid GB English words.
        :param tag_map: A map from PTB to universal dependency pos tags.
        :param nlp: A preloaded spacy processing object.
        :param stemmer: The Lancaster stemmer in NLTK.
        :return: An error type string.
        """
        # Extract strings, pos tags and parse info from the toks.
        orig_str, orig_pos, orig_dep = CatRules.get_edit_info(orig_toks, tag_map)
        cor_str, cor_pos, cor_dep = CatRules.get_edit_info(cor_toks, tag_map)

        # Orthography; i.e. whitespace and/or case errors.
        if CatRules.only_orth_change(orig_str, cor_str):
            return "ORTH"
        # Word Order; only matches exact reordering.
        if CatRules.exact_reordering(orig_str, cor_str):
            return "WO"

        # 1:1 replacements (very common)
        if len(orig_str) == len(cor_str) == 1:
            # 1. SPECIAL CASES
            # Possessive noun suffixes; e.g. ' -> 's
            if orig_toks[0].tag_ == "POS" or cor_toks[0].tag_ == "POS":
                return "NOUN:POSS"
            # Contraction. Rule must come after possessive.
            if (orig_str[0].lower() in CatRules.CONTS or cor_str[0].lower() in CatRules.CONTS) and orig_pos == cor_pos:
                return "CONTR"
            # Special auxiliaries in contractions (1); e.g. ca -> can
            if set(orig_str[0].lower() + cor_str[0].lower()) in CatRules.SPECIAL_AUX1:
                return "CONTR"
            # Special auxiliaries in contractions (2); e.g. ca -> could
            if orig_str[0].lower() in CatRules.SPECIAL_AUX2 or cor_str[0].lower() in CatRules.SPECIAL_AUX2:
                return "VERB:TENSE"
            # Special: "was" and "were" are the only past tense SVA.
            if {orig_str[0].lower(), cor_str[0].lower()} == {"was", "were"}:
                return "VERB:SVA"

            # 2. SPELLING AND INFLECTION
            # Only check alphabetical strings on the original side.
            # Spelling errors take precendece over POS errors so this rule is ordered.
            if orig_str[0].isalpha():
                # Check a GB English dict for both orig and lower case.
                # "cat" is in the dict, but "Cat" is not.
                if orig_str[0] not in gb_spell and orig_str[0].lower() not in gb_spell:
                    # Check if both sides have a common lemma
                    if CatRules.same_lemma(orig_toks[0], cor_toks[0], nlp):
                        # Inflection; Usually count vs mass nouns or e.g. got vs getted
                        if orig_pos == cor_pos and orig_pos[0] in {"NOUN", "VERB"}:
                            return orig_pos[0] + ":INFL"
                        # Unknown morphology; i.e. we cannot be more specific.
                        else:
                            return "MORPH"
                    # Use string similarity to detect true spelling errors.
                    else:
                        char_ratio = SequenceMatcher(None, orig_str[0], cor_str[0]).ratio()
                        # Ratio > 0.5 means both side share at least half the same chars.
                        # WARNING: THIS IS AN APPROXIMATION.
                        if char_ratio > 0.5:
                            return "SPELL"
                        # If ratio is <= 0.5, this may be a spelling+other error; e.g. tolk -> say
                        else:
                            # If POS is the same, this takes precedence over spelling.
                            if orig_pos == cor_pos and orig_pos[0] not in CatRules.RARE_TAGS:
                                return orig_pos[0]
                            # Tricky cases.
                            else:
                                return "OTHER"

            # 3. MORPHOLOGY
            # Only ADJ, ADV, NOUN and VERB with same lemma can have inflectional changes.
            if CatRules.same_lemma(orig_toks[0], cor_toks[0], nlp) and \
                    orig_pos[0] in CatRules.OPEN_TAGS and cor_pos[0] in CatRules.OPEN_TAGS:
                # Same POS on both sides
                if orig_pos == cor_pos:
                    # Adjective form; e.g. comparatives
                    if orig_pos[0] == "ADJ":
                        return "ADJ:FORM"
                    # Noun number
                    if orig_pos[0] == "NOUN":
                        return "NOUN:NUM"
                    # Verbs - various types
                    if orig_pos[0] == "VERB":
                        # NOTE: These rules are carefully ordered.
                        # Use the dep parse to find some form errors.
                        # Main verbs preceded by aux cannot be tense or SVA.
                        if CatRules.preceded_by_aux(orig_toks, cor_toks):
                            return "VERB:FORM"
                        # Use fine PTB tags to find various errors.
                        # FORM errors normally involve VBG or VBN.
                        if orig_toks[0].tag_ in {"VBG", "VBN"} or cor_toks[0].tag_ in {"VBG", "VBN"}:
                            return "VERB:FORM"
                        # Of what's left, TENSE errors normally involved VBD.
                        if orig_toks[0].tag_ == "VBD" or cor_toks[0].tag_ == "VBD":
                            return "VERB:TENSE"
                        # Of what's left, SVA errors normally involve VBZ.
                        if orig_toks[0].tag_ == "VBZ" or cor_toks[0].tag_ == "VBZ":
                            return "VERB:SVA"
                        # Any remaining aux verbs are called TENSE.
                        if orig_dep[0].startswith("aux") and cor_dep[0].startswith("aux"):
                            return "VERB:TENSE"
                # Use dep labels to find some more ADJ:FORM
                if set(orig_dep + cor_dep).issubset({"acomp", "amod"}):
                    return "ADJ:FORM"
                # Adj to plural noun is usually a noun number error; e.g. musical -> musicals.
                if orig_pos[0] == "ADJ" and cor_toks[0].tag_ == "NNS":
                    return "NOUN:NUM"
                # For remaining verb errors (rare), rely on cor_pos
                if cor_toks[0].tag_ in {"VBG", "VBN"}:
                    return "VERB:FORM"
                # Cor VBD = TENSE
                if cor_toks[0].tag_ == "VBD":
                    return "VERB:TENSE"
                # Cor VBZ = SVA
                if cor_toks[0].tag_ == "VBZ":
                    return "VERB:SVA"
                # Tricky cases that all have the same lemma.
                else:
                    return "MORPH"
            # Derivational morphology.
            if stemmer.stem(orig_str[0]) == stemmer.stem(cor_str[0]) and \
                    orig_pos[0] in CatRules.OPEN_TAGS and cor_pos[0] in CatRules.OPEN_TAGS:
                return "MORPH"

            # 4. GENERAL
            # Auxiliaries with different lemmas
            if orig_dep[0].startswith("aux") and cor_dep[0].startswith("aux"):
                return "VERB:TENSE"
            # POS-based tags. Some of these are context sensitive mispellings.
            if orig_pos == cor_pos and orig_pos[0] not in CatRules.RARE_TAGS:
                return orig_pos[0]
            # Some dep labels map to POS-based tags.
            if orig_dep == cor_dep and orig_dep[0] in CatRules.DEP_MAP.keys():
                return CatRules.DEP_MAP[orig_dep[0]]
            # Phrasal verb particles.
            if set(orig_pos + cor_pos) == {"PART", "PREP"} or set(orig_dep + cor_dep) == {"prt", "prep"}:
                return "PART"
            # Can use dep labels to resolve DET + PRON combinations.
            if set(orig_pos + cor_pos) == {"DET", "PRON"}:
                # DET cannot be a subject or object.
                if cor_dep[0] in {"nsubj", "nsubjpass", "dobj", "pobj"}:
                    return "PRON"
                # "poss" indicates possessive determiner
                if cor_dep[0] == "poss":
                    return "DET"
            # Tricky cases.
            else:
                return "OTHER"

        # Multi-token replacements (uncommon)
        # All auxiliaries
        if set(orig_dep + cor_dep).issubset({"aux", "auxpass"}):
            return "VERB:TENSE"
        # All same POS
        if len(set(orig_pos + cor_pos)) == 1:
            # Final verbs with the same lemma are tense; e.g. eat -> has eaten
            if orig_pos[0] == "VERB" and CatRules.same_lemma(orig_toks[-1], cor_toks[-1], nlp):
                return "VERB:TENSE"
            # POS-based tags.
            elif orig_pos[0] not in CatRules.RARE_TAGS:
                return orig_pos[0]
        # All same special dep labels.
        if len(set(orig_dep + cor_dep)) == 1 and orig_dep[0] in CatRules.DEP_MAP.keys():
            return CatRules.DEP_MAP[orig_dep[0]]
        # Infinitives, gerunds, phrasal verbs.
        if set(orig_pos + cor_pos) == {"PART", "VERB"}:
            # Final verbs with the same lemma are form; e.g. to eat -> eating
            if CatRules.same_lemma(orig_toks[-1], cor_toks[-1], nlp):
                return "VERB:FORM"
            # Remaining edits are often verb; e.g. to eat -> consuming, look at -> see
            else:
                return "VERB"
        # Possessive nouns; e.g. friends -> friend 's
        if (orig_pos == ["NOUN", "PART"] or cor_pos == ["NOUN", "PART"]) and \
                CatRules.same_lemma(orig_toks[0], cor_toks[0], nlp):
            return "NOUN:POSS"
        # Adjective forms with "most" and "more"; e.g. more free -> freer
        if (orig_str[0].lower() in {"most", "more"} or cor_str[0].lower() in {"most", "more"}) and \
                CatRules.same_lemma(orig_toks[-1], cor_toks[-1], nlp) and len(orig_str) <= 2 and len(cor_str) <= 2:
            return "ADJ:FORM"

        # Tricky cases.
        else:
            return "OTHER"

    @staticmethod
    def only_orth_change(orig_str, cor_str):
        """

        :param orig_str: A list of original token strings
        :param cor_str: A list of corrected token strings
        :return: Boolean; the difference between the inputs is only whitespace or case.
        """
        orig_join = "".join(orig_str).lower()
        cor_join = "".join(cor_str).lower()
        if orig_join == cor_join:
            return True
        return False

    @staticmethod
    def exact_reordering(orig_str, cor_str):
        """

        :param orig_str: A list of original token strings
        :param cor_str: A list of corrected token strings
        :return: Boolean; the tokens are exactly the same but in a different order.
        """
        # Sorting lets us keep duplicates.
        orig_set = sorted([tok.lower() for tok in orig_str])
        cor_set = sorted([tok.lower() for tok in cor_str])
        if orig_set == cor_set:
            return True
        return False

    @staticmethod
    def same_lemma(orig_tok, cor_tok, nlp):
        """

        :param orig_tok: An original text spacy token.
        :param cor_tok: A corrected text spacy token.
        :param nlp: A spaCy processing object.
        :return: Boolean; the tokens have the same lemma.
                    Spacy only finds lemma for its predicted POS tag. Sometimes these are wrong,
                    so we also consider alternative POS tags to improve chance of a match.
        """
        orig_lemmas = set()
        cor_lemmas = set()

        lemmatizer = Lemmatizer(nlp.vocab.lookups)

        for pos in CatRules.OPEN_POS:
            # Pass the lower cased form of the word for lemmatization; improves accuracy.
            orig_lemmas.update(lemmatizer(orig_tok.text.lower(), pos))
            cor_lemmas.update(lemmatizer(cor_tok.text.lower(), pos))
        if set(orig_lemmas).intersection(set(cor_lemmas)):
            return True
        return False

    @staticmethod
    def preceded_by_aux(orig_tok, cor_tok):
        """

        :param orig_tok: An original text spacy token.
        :param cor_tok: A corrected text spacy token.
        :return: Boolean; both tokens have a dependant auxiliary verb.
        """
        # If the toks are aux, we need to check if they are the first aux.
        if orig_tok[0].dep_.startswith("aux") and cor_tok[0].dep_.startswith("aux"):
            # Find the parent verb
            orig_head = orig_tok[0].head
            cor_head = cor_tok[0].head
            # Find the children of the parent
            orig_children = orig_head.children
            cor_children = cor_head.children
            # Check the orig children.
            for orig_child in orig_children:
                # Look at the first aux...
                if orig_child.dep_.startswith("aux"):
                    # Check if the string matches orig_tok
                    if orig_child.text != orig_tok[0].text:
                        # If it doesn't, orig_tok is not the first aux so check the cor children
                        for cor_child in cor_children:
                            # Find the first aux in cor...
                            if cor_child.dep_.startswith("aux"):
                                # If that doesn't match cor_tok, there cor_tok also isnt first aux.
                                if cor_child.text != cor_tok[0].text:
                                    # Therefore, both orig and cor are not first aux.
                                    return True
                                # Break after the first cor aux
                                break
                    # Break after the first orig aux.
                    break
        # Otherwise, the toks are main verbs so we need to look for any aux.
        else:
            orig_deps = [orig_dep.dep_ for orig_dep in orig_tok[0].children]
            cor_deps = [cor_dep.dep_ for cor_dep in cor_tok[0].children]
            if "aux" in orig_deps or "auxpass" in orig_deps:
                if "aux" in cor_deps or "auxpass" in cor_deps:
                    return True
        return False
