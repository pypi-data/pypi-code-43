from operator import itemgetter


class Toolbox:

    @staticmethod
    def load_dictionary(path):
        """
        Load latest Hunspell dictionary

        :param path: dictionary path
        :return: list of dictionary words
        """
        return set(open(path, encoding='utf8').read().split())

    @staticmethod
    def load_tag_map(path):
        """
        Load Stanford Universal Tags map file

        :param path: the map file path
        :return: map of dependency labels to parts-of-speech.
        """
        map_dict = {}
        open_file = open(path, encoding='utf8').readlines()
        for line in open_file:
            line = line.strip().split("\t")
            # Change ADP to PREP; makes it clearer
            if line[1].strip() == "ADP":
                map_dict[line[0]] = "PREP"
            # Also change PROPN to NOUN; we don't need a prop noun tag
            elif line[1].strip() == "PROPN":
                map_dict[line[0]] = "NOUN"
            else:
                map_dict[line[0]] = line[1].strip()

        # Add some spacy PTB tags not in the original mapping.
        map_dict['""'] = "PUNCT"
        map_dict["SP"] = "SPACE"
        map_dict["_SP"] = "SPACE"   # spacy 2.2.1
        map_dict["ADD"] = "X"
        map_dict["GW"] = "X"
        map_dict["NFP"] = "X"
        map_dict["XX"] = "X"

        return map_dict

    @staticmethod
    def process_m2(info):
        """
        :param info: A sentence + edit block in an m2 file.
        :return: Output 1: The original sentence (a list of tokens)
                Output 2: A dictionary; key is coder id, value is a tuple.
                tuple[0] is the corrected sentence (a list of tokens), tuple[1] is the edits.
                Process M2 to extract sentences and edits.
        """
        info = info.split("\n")
        orig_sent = info[0][2:].split()  # [2:] ignore the leading "S "
        all_edits = info[1:]
        # Simplify the edits and group by coder id.
        edit_dict = Toolbox.process_edits(all_edits)
        out_dict = {}
        # Loop through each coder and their edits.
        for coder, edits in edit_dict.items():
            # Copy orig_sent. We will apply the edits to it to make cor_sent
            cor_sent = orig_sent[:]
            gold_edits = []
            offset = 0
            # Sort edits by start and end offset only. If they are the same, do not reorder.
            edits = sorted(edits, key=itemgetter(0))  # Sort by start offset
            edits = sorted(edits, key=itemgetter(1))  # Sort by end offset
            for edit in edits:
                # Do not apply noop or Um edits, but save them
                if edit[2] in {"noop", "Um"}:
                    gold_edits.append(edit + [-1, -1])
                    continue
                orig_start = edit[0]
                orig_end = edit[1]
                cor_toks = edit[3].split()
                # Apply the edit.
                cor_sent[orig_start + offset:orig_end + offset] = cor_toks
                # Get the cor token start and end positions in cor_sent
                cor_start = orig_start + offset
                cor_end = cor_start + len(cor_toks)
                # Keep track of how this affects orig edit offsets.
                offset = offset - (orig_end - orig_start) + len(cor_toks)
                # Save the edit with cor_start and cor_end
                gold_edits.append(edit + [cor_start] + [cor_end])
            # Save the cor_sent and gold_edits for each annotator in the out_dict.
            out_dict[coder] = (cor_sent, gold_edits)
        return orig_sent, out_dict

    @staticmethod
    def process_edits(edits):
        """
        :param edits: A list of edit lines for a sentence in an m2 file.
        :return: An edit dictionary; key is coder id, value is a list of edits.
        """
        edit_dict = {}
        for edit in edits:
            edit = edit.split("|||")
            span = edit[0][2:].split()  # [2:] ignore the leading "A "
            start = int(span[0])
            end = int(span[1])
            cat = edit[1]
            cor = edit[2]
            id = edit[-1]
            # Save the useful info as a list
            proc_edit = [start, end, cat, cor]
            # Save the proc edit inside the edit_dict using coder id.
            if id in edit_dict.keys():
                edit_dict[id].append(proc_edit)
            else:
                edit_dict[id] = [proc_edit]
        return edit_dict

    @staticmethod
    def apply_spacy(sent, nlp):
        """
        :param sent: A list of token strings in a sentence.
        :param nlp: A preloaded Spacy processing object.
        :return: Annotate tokens with POS, lemma and parse info.
        """
        # Convert tokens to spacy tokens and POS tag and parse.
        # sent = nlp.tokenizer.tokens_from_list(sent)
        # nlp.tagger(sent)
        # nlp.parser(sent)
        # return sent
        return nlp(sent)

    @staticmethod
    def minimise_edit(edit, orig, cor):
        """
        :param edit: An edit list. [orig_start, orig_end, cat, cor, cor_start, cor_end]
        :param orig: An original SpaCy sentence.
        :param cor: A corrected SpaCy sentence.
        :return: A minimised edit with duplicate words on both sides removed.
                    e.g. [was eaten -> has eaten] becomes [was -> has]
        """
        # edit = [orig_start, orig_end, cat, cor, cor_start, cor_end]
        orig_toks = orig[edit[0]:edit[1]]
        cor_toks = cor[edit[4]:edit[5]]
        # While the first token is the same string in both (and both are not null)
        while orig_toks and cor_toks and orig_toks[0].text == cor_toks[0].text:
            # Remove that token from the span, and adjust the start offset.
            orig_toks = orig_toks[1:]
            cor_toks = cor_toks[1:]
            edit[0] += 1
            edit[4] += 1
        # Then do the same from the last token.
        while orig_toks and cor_toks and orig_toks[-1].text == cor_toks[-1].text:
            # Remove that token from the span, and adjust the start offset.
            orig_toks = orig_toks[:-1]
            cor_toks = cor_toks[:-1]
            edit[1] -= 1
            edit[5] -= 1
        # If both sides are not null, save the new correction string.
        if orig_toks or cor_toks:
            edit[3] = " ".join([tok.text for tok in cor_toks])
            return edit

    @staticmethod
    def format_edit(edit, coder_id=0):
        """
        :param edit: An edit list = [orig_start, orig_end, cat, cor, cor_start, cor_end]
        :param coder_id: A coder id for the specific annotator.
        :return: An edit in m2 file format.
        """
        span = " ".join(["A", str(edit[0]), str(edit[1])])
        return "|||".join([span, edit[2], edit[3], "REQUIRED", "-NONE-", str(coder_id)])