import argparse
import os
from contextlib import ExitStack

import spacy
from nltk.stem.lancaster import LancasterStemmer
from errant import AlignText
from errant import CatRules
from errant import Toolbox


class ParallelToM2:

    @staticmethod
    def convert(original_file, corrected_files, output_file, merge_strategy='rules', levenshtein=False):
        """
        :param original_file: The path to the original tokenized text file
        :param corrected_files: list - The paths to >= 1 corrected tokenized text files
        :param output_file: The output file path
        :param merge_strategy: Choose a merging strategy for automatic alignment, possible values:
                                rules: Use a rule-based merging strategy (default)
                                all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I
                                all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI
                                all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I
        :param levenshtein: Use standard Levenshtein to align sentences
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

        # ExitStack lets us process an arbitrary number of files line by line simultaneously.
        # See https://stackoverflow.com/questions/24108769/how-to-read-and-process-multiple-files-simultaneously-in-python
        print("Processing files...")
        with ExitStack() as stack:
            in_files = [stack.enter_context(open(i, encoding='utf8')) for i in [original_file] + corrected_files]
            # Process each line of all input files.
            for line_id, line in enumerate(zip(*in_files)):
                orig_sent = line[0].strip()
                cor_sents = line[1:]
                # If orig sent is empty, skip the line
                if not orig_sent: continue
                # Write the original sentence to the output m2 file.
                out_m2.write("S " + orig_sent + "\n")
                # Markup the original sentence with spacy (assume tokenized)
                proc_orig = nlp(orig_sent)
                # Loop through the corrected sentences
                for cor_id, cor_sent in enumerate(cor_sents):
                    cor_sent = cor_sent.strip()
                    # Identical sentences have no edits, so just write noop.
                    if orig_sent == cor_sent:
                        out_m2.write("A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||" + str(cor_id) + "\n")
                    # Otherwise, do extra processing.
                    else:
                        # Markup the corrected sentence with spacy (assume tokenized)
                        proc_cor = nlp(cor_sent)
                        # Auto align the parallel sentences and extract the edits.
                        auto_edits = AlignText.get_auto_aligned_edits(proc_orig, proc_cor, merge_strategy, levenshtein)
                        # Loop through the edits.
                        for auto_edit in auto_edits:
                            # Give each edit an automatic error type.
                            cat = CatRules.auto_type_edit(auto_edit, proc_orig, proc_cor, gb_spell, tag_map, nlp,
                                                          stemmer)
                            auto_edit[2] = cat
                            # Write the edit to the output m2 file.
                            out_m2.write(Toolbox.format_edit(auto_edit, cor_id) + "\n")
                # Write a newline when we have processed all corrections for a given sentence.
                out_m2.write("\n")


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(
        description='''
Convert parallel original and corrected text files (1 sentence per line) into M2 format.
The default uses Damerau-Levenshtein and merging rules and assumes tokenized text.
''',
        formatter_class=argparse.RawTextHelpFormatter,
        usage="%(prog)s [-h] [options] -orig ORIG -cor COR [COR ...] -out OUT")
    parser.add_argument("-orig", help="The path to the original tokenized text file.", required=True)
    parser.add_argument("-cor", help="The paths to >= 1 corrected tokenized text files.", nargs="+", default=[], required=True)
    parser.add_argument("-out", help="The output file path.", required=True)
    parser.add_argument("-lev", help="Use standard Levenshtein to align sentences.", action="store_true")
    parser.add_argument(
        "-merge",
        choices=["rules", "all-split", "all-merge", "all-equal"], default="rules",
        help='''
Choose a merging strategy for automatic alignment.
rules: Use a rule-based merging strategy (default)
all-split: Merge nothing; e.g. MSSDI -> M, S, S, D, I
all-merge: Merge adjacent non-matches; e.g. MSSDI -> M, SSDI
all-equal: Merge adjacent same-type non-matches; e.g. MSSDI -> M, SS, D, I
'''
    )
    args = parser.parse_args()

    # Run the program.
    ParallelToM2.convert(args.orig, args.cor, args.out, args.merge, args.lev)
