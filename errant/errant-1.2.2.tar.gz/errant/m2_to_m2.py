import argparse
import os

import spacy
from nltk.stem.lancaster import LancasterStemmer
from errant import AlignText
from errant import CatRules
from errant import Toolbox


class M2ToM2:

    @staticmethod
    def convert(m2_file, output_file, edit_type, merge_strategy='rules', levenshtein=False, max_edits=False,
                old_cats=False):
        """
        :param m2_file: A path to an m2 file
        :param output_file: The output file path
        :param edit_type: Extract edits automatically ('auto'), Use existing edit alignments ('gold'
        :param merge_strategy: Choose a merging strategy for automatic alignment, possible values:
                                rules: Use a rule-based merging strategy (default)
                                all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I
                                all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI
                                all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I
        :param levenshtein: Use standard Levenshtein to align sentences
        :param max_edits: Do not minimise edit spans. (gold only)
        :param old_cats: Do not reclassify the edits. (gold only)
        :return:
        """
        # Get base working directory.
        basename = os.path.dirname(os.path.realpath(__file__))
        print("Loading resources...")
        # Load Tokenizer and other resources
        nlp = spacy.load("en")
        # Lancaster Stemmer
        stemmer = LancasterStemmer()
        # GB English word list (inc -ise and -ize)
        gb_spell = Toolbox.load_dictionary(basename + "/resources/en_GB-large.txt")
        # Part of speech map file
        tag_map = Toolbox.load_tag_map(basename + "/resources/en-ptb_map")
        # Setup output m2 file
        out_m2 = open(output_file, 'w', encoding='utf8')

        print("Processing files...")
        # Open the m2 file and split into sentence+edit chunks.
        m2_file_strings = open(m2_file, encoding='utf8').read().strip().split("\n\n")
        for info in m2_file_strings:
            # Get the original and corrected sentence + edits for each annotator.
            orig_sent, coder_dict = Toolbox.process_m2(info)
            # Write the orig_sent to the output m2 file.
            out_m2.write("S " + " ".join(orig_sent) + "\n")
            # Only process sentences with edits.
            if coder_dict:
                # Save marked up original sentence here, if required.
                proc_orig = ""
                # Loop through the annotators
                for coder, coder_info in sorted(coder_dict.items()):
                    cor_sent = coder_info[0]
                    gold_edits = coder_info[1]
                    # If there is only 1 edit and it is noop, just write it.
                    if gold_edits[0][2] == "noop":
                        out_m2.write(Toolbox.format_edit(gold_edits[0], coder) + "\n")
                        continue
                    # Markup the orig and cor sentence with spacy (assume tokenized)
                    # Orig is marked up only once for the first coder that needs it.
                    proc_orig = nlp(' '.join(orig_sent)) if not proc_orig else proc_orig
                    proc_cor = nlp(' '.join(cor_sent))
                    # Loop through gold edits.
                    for gold_edit in gold_edits:
                        # Um and UNK edits (uncorrected errors) are always preserved.
                        if gold_edit[2] in {"Um", "UNK"}:
                            # Um should get changed to UNK unless using old categories.
                            if gold_edit[2] == "Um" and not old_cats: gold_edit[2] = "UNK"
                            out_m2.write(Toolbox.format_edit(gold_edit, coder) + "\n")
                        # Gold edits
                        elif edit_type == 'gold':
                            # Minimise the edit; e.g. [has eaten -> was eaten] = [has -> was]
                            if not max_edits:
                                gold_edit = Toolbox.minimise_edit(gold_edit, proc_orig, proc_cor)
                                # If minimised to nothing, the edit disappears.
                                if not gold_edit: continue
                            # Give the edit an automatic error type.
                            if not old_cats:
                                cat = CatRules.auto_type_edit(gold_edit, proc_orig, proc_cor, gb_spell, tag_map, nlp,
                                                              stemmer)
                                gold_edit[2] = cat
                            # Write the edit to the output m2 file.
                            out_m2.write(Toolbox.format_edit(gold_edit, coder) + "\n")
                    # Auto edits
                    if edit_type == 'auto':
                        # Auto align the parallel sentences and extract the edits.
                        auto_edits = AlignText.get_auto_aligned_edits(proc_orig, proc_cor, merge_strategy, levenshtein)
                        # Loop through the edits.
                        for auto_edit in auto_edits:
                            # Give each edit an automatic error type.
                            cat = CatRules.auto_type_edit(auto_edit, proc_orig, proc_cor, gb_spell, tag_map, nlp,
                                                          stemmer)
                            auto_edit[2] = cat
                            # Write the edit to the output m2 file.
                            out_m2.write(Toolbox.format_edit(auto_edit, coder) + "\n")
            # Write a newline when there are no more coders.
            out_m2.write("\n")


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description="Automatically extract and/or type edits in an m2 file.",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s [-h] (-auto | -gold) [options] m2 -out OUT")
    parser.add_argument("m2", help="A path to an m2 file.")
    type_group = parser.add_mutually_exclusive_group(required=True)
    type_group.add_argument("-auto", help="Extract edits automatically.", action="store_true")
    type_group.add_argument("-gold", help="Use existing edit alignments.", action="store_true")
    parser.add_argument("-out", help="The output file path.", required=True)
    parser.add_argument("-max_edits", help="Do not minimise edit spans. (gold only)", action="store_true")
    parser.add_argument("-old_cats", help="Do not reclassify the edits. (gold only)", action="store_true")
    parser.add_argument("-lev", help="Use standard Levenshtein to align sentences.", action="store_true")
    parser.add_argument("-merge",
                        choices=["rules", "all-split", "all-merge", "all-equal"],
                        default="rules",
                        help='''
Choose a merging strategy for automatic alignment.
rules: Use a rule-based merging strategy (default)
all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I
all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI
all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I					
'''
                        )
    args = parser.parse_args()
    arg_edit_type = 'gold' if (args.gold is True) else 'auto'

    M2ToM2.convert(args.m2, args.out, arg_edit_type, args.merge, args.lev, args.max_edits, args.old_cats)
