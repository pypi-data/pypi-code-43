import argparse
from collections import Counter


class CompareM2:

    @staticmethod
    def compare(hyp_m2, ref_m2, detection_tokens=False, detection_spans=False, correction_type='cs', score_category=1,
                only_single=False, only_multi=False, filters=None, fscore_beta=0.5, verbose=False):
        """
        :param hyp_m2: A hypothesis M2 file
        :param ref_m2: A reference M2 file
        :param detection_tokens: Evaluate Detection in terms of Tokens
        :param detection_spans: Evaluate Detection in terms of Spans
        :param correction_type: Evaluate Correction in terms of Spans ('cs') or Spans with Error types ('cse) (default: cs)
        :param score_category: Show error category scores (default: 1), possible values:
                                1: Only show operation tier scores; e.g. R.
                                2: Only show main tier scores; e.g. NOUN.
                                3: Show all category scores; e.g. R:NOUN.
        :param only_single: Only evaluate single token edits; i.e. 0:1, 1:0 or 1:1 (default: False)
        :param only_multi: Only evaluate multi token edits; i.e. 2+:n or n:2+ (default: False)
        :param filters: Do not evaluate the specified error types (default: empty)
        :param fscore_beta: Value of beta in F-score. (default: 0.5)
        :param verbose: Print verbose output (default: False)
        :return: string representation of compare result
        """
        if filters is None:
            filters = []
        # Open hypothesis and reference m2 files and split into chunks
        hyp_m2_strings = open(hyp_m2, encoding='utf8').read().strip().split("\n\n")
        ref_m2_strings = open(ref_m2, encoding='utf8').read().strip().split("\n\n")
        # Make sure they have the same number of sentences
        assert len(hyp_m2_strings) == len(ref_m2_strings)

        # Store global corpus level best counts here
        best_dict = Counter({"tp": 0, "fp": 0, "fn": 0})
        best_cats = {}
        # Process each sentence
        sents = zip(hyp_m2_strings, ref_m2_strings)
        for sent_id, sent in enumerate(sents):
            # Simplify the edits into lists of lists
            hyp_edits = CompareM2.simplify_edits(sent[0])
            ref_edits = CompareM2.simplify_edits(sent[1])
            # Process the edits for detection/correction based on detection_type/correction_type
            hyp_dict = CompareM2.process_edits(hyp_edits, detection_tokens, detection_spans, correction_type,
                                               only_single, only_multi, filters)
            ref_dict = CompareM2.process_edits(ref_edits, detection_tokens, detection_spans, correction_type,
                                               only_single, only_multi, filters)
            # Evaluate the edits and get the best TP, FP, FN counts for the best hyp+ref combo.
            count_dict, cat_dict = CompareM2.evaluate_edits(hyp_dict, ref_dict, best_dict, sent_id, fscore_beta,
                                                            verbose)
            # Merge these dicts with best_dict and best_cats
            best_dict += Counter(count_dict)
            best_cats = CompareM2.merge_dict(best_cats, cat_dict)
        # Print results
        res = CompareM2.stringify_results(best_dict, best_cats, detection_tokens, detection_spans, correction_type,
                                score_category, fscore_beta)
        print(res)
        return res

    @staticmethod
    def simplify_edits(sent):
        """

        :param sent: An m2 format sentence with edits.
        :return: A list of lists. Each edit: [start, end, cat, cor, coder]
        """
        out_edits = []
        # Get the edit lines from an m2 block.
        edits = sent.split("\n")[1:]
        # Loop through the edits
        for edit in edits:
            # Preprocessing
            edit = edit[2:].split("|||")  # Ignore "A " then split.
            span = edit[0].split()
            start = int(span[0])
            end = int(span[1])
            cat = edit[1]
            cor = edit[2]
            coder = int(edit[-1])
            out_edit = [start, end, cat, cor, coder]
            out_edits.append(out_edit)
        return out_edits

    @staticmethod
    def process_edits(edits, detection_tokens, detection_spans, correction_type, only_single, only_multi, filters):
        """

        :param edits: A list of edits. Each edit: [start, end, cat, cor, coder]
        :param detection_tokens: Evaluate Detection in terms of Tokens
        :param detection_spans: Evaluate Detection in terms of Spans
        :param correction_type: Evaluate Correction in terms of Spans or Spans with Error types
        :param filters: Do not evaluate the specified error types
        :param only_single: Only evaluate single token edits; i.e. 0:1, 1:0 or 1:1
        :param only_multi: Only evaluate multi token edits; i.e. 2+:n or n:2+
        :return: A dict; key is coder, value is edit dict. edit dict format varies based on parameters.
        """
        coder_dict = {}
        # Add an explicit noop edit if there are no edits.
        if not edits: edits = [[-1, -1, "noop", "-NONE-", 0]]
        # Loop through the edits
        for edit in edits:
            # Name the edit elements for clarity
            start = edit[0]
            end = edit[1]
            cat = edit[2]
            cor = edit[3]
            coder = edit[4]
            # Add the coder to the coder_dict if necessary
            if coder not in coder_dict: coder_dict[coder] = {}

            # Optionally apply filters based on parameters
            # 1. UNK type edits are only useful for detection, not correction.
            if not detection_tokens and not detection_spans and cat == "UNK": continue
            # 2. Only evaluate single token edits; i.e. 0:1, 1:0 or 1:1
            if only_single and (end - start >= 2 or len(cor.split()) >= 2): continue
            # 3. Only evaluate multi token edits; i.e. 2+:n or n:2+
            if only_multi and end - start < 2 and len(cor.split()) < 2: continue
            # 4. If there is a filter, ignore the specified error types
            if filters and cat in filters: continue

            # Token Based Detection
            if detection_tokens:
                # Preserve noop edits.
                if start == -1:
                    if (start, start) in coder_dict[coder].keys():
                        coder_dict[coder][(start, start)].append(cat)
                    else:
                        coder_dict[coder][(start, start)] = [cat]
                # Insertions defined as affecting the token on the right
                elif start == end and start >= 0:
                    if (start, start + 1) in coder_dict[coder].keys():
                        coder_dict[coder][(start, start + 1)].append(cat)
                    else:
                        coder_dict[coder][(start, start + 1)] = [cat]
                # Edit spans are split for each token in the range.
                else:
                    for tok_id in range(start, end):
                        if (tok_id, tok_id + 1) in coder_dict[coder].keys():
                            coder_dict[coder][(tok_id, tok_id + 1)].append(cat)
                        else:
                            coder_dict[coder][(tok_id, tok_id + 1)] = [cat]

            # Span Based Detection
            elif detection_spans:
                if (start, end) in coder_dict[coder].keys():
                    coder_dict[coder][(start, end)].append(cat)
                else:
                    coder_dict[coder][(start, end)] = [cat]

            # Span Based Correction
            else:
                # With error type classification
                if correction_type == 'cse':
                    if (start, end, cat, cor) in coder_dict[coder].keys():
                        coder_dict[coder][(start, end, cat, cor)].append(cat)
                    else:
                        coder_dict[coder][(start, end, cat, cor)] = [cat]
                # Without error type classification
                else:
                    if (start, end, cor) in coder_dict[coder].keys():
                        coder_dict[coder][(start, end, cor)].append(cat)
                    else:
                        coder_dict[coder][(start, end, cor)] = [cat]
        return coder_dict

    @staticmethod
    def evaluate_edits(hyp_dict, ref_dict, best, sent_id, fscore_beta, verbose):
        """

        :param hyp_dict: A hyp dict; key is coder_id, value is dict of processed hyp edits.
        :param ref_dict: A ref dict; key is coder_id, value is dict of processed ref edits.
        :param best: A dictionary of the best corpus level TP, FP and FN counts so far.
        :param sent_id: Sentence ID (for verbose output only)
        :param fscore_beta: Value of beta in F-score
        :param verbose: Print verbose output
        :return: A dict of the best corpus level TP, FP and FN counts for the input sentence.
                    A dict of the equivalent error types for the best corpus level TP, FP and FNs.
        """
        # Store the best sentence level scores and hyp+ref combination IDs
        # best_f is initialised as -1 cause 0 is a valid result.
        best_tp, best_fp, best_fn, best_f, best_hyp, best_ref = 0, 0, 0, -1, 0, 0
        best_cat = {}
        # Compare each hyp and ref combination
        for hyp_id in hyp_dict.keys():
            for ref_id in ref_dict.keys():
                # Get the local counts for the current combination.
                tp, fp, fn, cat_dict = CompareM2.compare_edits(hyp_dict[hyp_id], ref_dict[ref_id])
                # Compute the local sentence scores (for verbose output only)
                loc_p, loc_r, loc_f = CompareM2.compute_Fscore(tp, fp, fn, fscore_beta)
                # Compute the global sentence scores
                p, r, f = CompareM2.compute_Fscore(tp + best["tp"], fp + best["fp"], fn + best["fn"], fscore_beta)
                # Save the scores if they are the current best hyp+ref combo in terms of:
                # 1. Higher F-score
                # 2. Same F-score, higher TP
                # 3. Same F-score and TP, lower FP
                # 4. Same F-score, TP and FP, lower FN
                if (f > best_f) or \
                        (f == best_f and tp > best_tp) or \
                        (f == best_f and tp == best_tp and fp < best_fp) or \
                        (f == best_f and tp == best_tp and fp == best_fp and fn < best_fn):
                    best_tp, best_fp, best_fn, best_f, best_hyp, best_ref = tp, fp, fn, f, hyp_id, ref_id
                    best_cat = cat_dict
                # Verbose output
                if verbose:
                    # Prepare verbose output edits.
                    hyp_verb = list(sorted(hyp_dict[hyp_id].keys()))
                    ref_verb = list(sorted(ref_dict[ref_id].keys()))
                    # Ignore noop edits
                    if not hyp_verb or hyp_verb[0][0] == -1: hyp_verb = []
                    if not ref_verb or ref_verb[0][0] == -1: ref_verb = []
                    # Print verbose info
                    print('{:-^40}'.format(""))
                    print("SENTENCE " + str(sent_id) + " - HYP " + str(hyp_id) + " - REF " + str(ref_id))
                    print("HYPOTHESIS EDITS :", hyp_verb)
                    print("REFERENCE EDITS  :", ref_verb)
                    print("Local TP/FP/FN   :", str(tp), str(fp), str(fn))
                    print("Local P/R/F" + str(fscore_beta) + "  :", str(loc_p), str(loc_r), str(loc_f))
                    print("Global TP/FP/FN  :", str(tp + best["tp"]), str(fp + best["fp"]), str(fn + best["fn"]))
                    print("Global P/R/F" + str(fscore_beta) + "  :", str(p), str(r), str(f))
        # Verbose output: display the best hyp+ref combination
        if verbose:
            print('{:-^40}'.format(""))
            print("^^ HYP " + str(best_hyp) + ", REF " + str(best_ref) + " chosen for sentence " + str(sent_id))
        # Save the best TP, FP and FNs as a dict, and return this and the best_cat dict
        best_dict = {"tp": best_tp, "fp": best_fp, "fn": best_fn}
        return best_dict, best_cat

    @staticmethod
    def compare_edits(hyp_edits, ref_edits):
        """

        :param hyp_edits: A dictionary of hypothesis edits for a single system.
        :param ref_edits: A dictionary of reference edits for a single annotator.
        :return: 1-3: The TP, FP and FN for the hyp vs the given ref annotator.
                    4: A dictionary of the error type counts.
        """
        tp = 0  # True Positives
        fp = 0  # False Positives
        fn = 0  # False Negatives
        cat_dict = {}  # {cat: [tp, fp, fn], ...}

        for h_edit, h_cats in hyp_edits.items():
            # noop hyp edits cannot be TP or FP
            if h_cats[0] == "noop": continue
            # TRUE POSITIVES
            if h_edit in ref_edits.keys():
                # On occasion, multiple tokens at same span.
                for h_cat in ref_edits[h_edit]:  # Use ref dict for TP
                    tp += 1
                    # Each dict value [TP, FP, FN]
                    if h_cat in cat_dict.keys():
                        cat_dict[h_cat][0] += 1
                    else:
                        cat_dict[h_cat] = [1, 0, 0]
            # FALSE POSITIVES
            else:
                # On occasion, multiple tokens at same span.
                for h_cat in h_cats:
                    fp += 1
                    # Each dict value [TP, FP, FN]
                    if h_cat in cat_dict.keys():
                        cat_dict[h_cat][1] += 1
                    else:
                        cat_dict[h_cat] = [0, 1, 0]
        for r_edit, r_cats in ref_edits.items():
            # noop ref edits cannot be FN
            if r_cats[0] == "noop": continue
            # FALSE NEGATIVES
            if r_edit not in hyp_edits.keys():
                # On occasion, multiple tokens at same span.
                for r_cat in r_cats:
                    fn += 1
                    # Each dict value [TP, FP, FN]
                    if r_cat in cat_dict.keys():
                        cat_dict[r_cat][2] += 1
                    else:
                        cat_dict[r_cat] = [0, 0, 1]
        return tp, fp, fn, cat_dict

    @staticmethod
    def compute_Fscore(tp, fp, fn, beta):
        """

        :param tp: True positives
        :param fp: false positives
        :param fn: false negatives
        :param beta: Value of beta in F-score.
        :return: 1-3: Precision, Recall and F-score rounded to 4dp.
        """
        p = float(tp) / (tp + fp) if fp else 1.0
        r = float(tp) / (tp + fn) if fn else 1.0
        f = float((1 + (beta ** 2)) * p * r) / (((beta ** 2) * p) + r) if p + r else 0.0
        return round(p, 4), round(r, 4), round(f, 4)

    @staticmethod
    def merge_dict(dict1, dict2):
        """

        :param dict1: error category dicts. Key is cat, value is list of TP, FP, FN.
        :param dict2: error category dicts. Key is cat, value is list of TP, FP, FN.
        :return: The dictionaries combined with cumulative TP, FP, FN.
        """
        for cat, stats in dict2.items():
            if cat in dict1.keys():
                dict1[cat] = [x + y for x, y in zip(dict1[cat], stats)]
            else:
                dict1[cat] = stats
        return dict1

    @staticmethod
    def process_categories(cat_dict, score_category):
        """

        :param cat_dict: A dict; key is error cat, value is counts for [tp, fp, fn]
        :param score_category: Integer value denoting level of error category granularity.
                Specifically, 1: Operation tier; e.g. M, R, U.  2: Main tier; e.g. NOUN, VERB  3: Everything.
        :return: A dictionary of category TP, FP and FN based on Input 2.
        """
        # Otherwise, do some processing.
        proc_cat_dict = {}
        for cat, cnt in cat_dict.items():
            if cat == "UNK":
                proc_cat_dict[cat] = cnt
                continue
            # M, U, R or UNK combined only.
            if score_category == 1:
                if cat[0] in proc_cat_dict.keys():
                    proc_cat_dict[cat[0]] = [x + y for x, y in zip(proc_cat_dict[cat[0]], cnt)]
                else:
                    proc_cat_dict[cat[0]] = cnt
            # Everything without M, U or R.
            elif score_category == 2:
                if cat[2:] in proc_cat_dict.keys():
                    proc_cat_dict[cat[2:]] = [x + y for x, y in zip(proc_cat_dict[cat[2:]], cnt)]
                else:
                    proc_cat_dict[cat[2:]] = cnt
            # All error category combinations
            else:
                return cat_dict
        return proc_cat_dict

    @staticmethod
    def stringify_results(best, best_cats, detection_tokens, detection_spans, correction_type, score_category, fscore_beta):
        """
        :param best: A dict of global best TP, FP and FNs
        :param best_cats: A dict of error types and counts for those TP, FP and FNs
        :param detection_tokens: Evaluate Detection in terms of Tokens
        :param detection_spans: Evaluate Detection in terms of Spans
        :param correction_type: Evaluate Correction in terms of Spans or Spans with Error types
        :param score_category: Show error category scores, possible values:
                                1: Only show operation tier scores; e.g. R.
                                2: Only show main tier scores; e.g. NOUN.
                                3: Show all category scores; e.g. R:NOUN.
        :param fscore_beta: Value of beta in F-score
        :return:
        """
        res = ''
        # Prepare output title.
        if detection_tokens:
            title = ' Token-Based Detection '
        elif detection_spans:
            title = ' Span-Based Detection '
        elif correction_type == 'cse':
            title = ' Span-Based Correction + Classification '
        else:
            title = ' Span-Based Correction '

        # Category Scores
        if score_category:
            best_cats = CompareM2.process_categories(best_cats, score_category)
            res += '\n'
            res += '{:=^66}'.format(title) + '\n'
            res += ''.join(map(str, ['Category'.ljust(14), 'TP'.ljust(8), 'FP'.ljust(8), 'FN'.ljust(8), 'P'.ljust(8), 'R'.ljust(8), 'F' + str(fscore_beta)])) + '\n'
            for cat, cnts in sorted(best_cats.items()):
                cat_p, cat_r, cat_f = CompareM2.compute_Fscore(cnts[0], cnts[1], cnts[2], fscore_beta)
                res += ''.join(map(str, [cat.ljust(14), str(cnts[0]).ljust(8), str(cnts[1]).ljust(8), str(cnts[2]).ljust(8), str(cat_p).ljust(8), str(cat_r).ljust(8), cat_f])) + '\n'

        # Print the overall results.
        res += '{:=^46}'.format(title) + '\n'
        res += '\t'.join(['TP', 'FP', 'FN', 'Prec', 'Rec', 'F' + str(fscore_beta)]) + '\n'
        res += '\t'.join(map(str, [best['tp'], best['fp'], best['fn']] + list(CompareM2.compute_Fscore(best['tp'], best['fp'], best['fn'], fscore_beta)))) + '\n'
        res += '{:=^46}'.format('') + '\n'
        res += '\n'
        return res


if __name__ == "__main__":
    # Define and parse program input
    parser = argparse.ArgumentParser(description='''
Calculate F-scores for error detection and/or correction.\n"
Flags let you evaluate error types at different levels of granularity.
''',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     usage="%(prog)s [options] -hyp HYP -ref REF")
    parser.add_argument("-hyp", help="A hypothesis M2 file", required=True)
    parser.add_argument("-ref", help="A reference M2 file", required=True)
    parser.add_argument("-b", "--beta", help="Value of beta in F-score. (default: 0.5)", default=0.5, type=float)
    parser.add_argument("-v", "--verbose", help="Print verbose output.", action="store_true")
    eval_type = parser.add_mutually_exclusive_group()
    eval_type.add_argument("-dt", help="Evaluate Detection in terms of Tokens.", action="store_true")
    eval_type.add_argument("-ds", help="Evaluate Detection in terms of Spans.", action="store_true")
    eval_type.add_argument("-cs", help="Evaluate Correction in terms of Spans. (default)", action="store_true")
    eval_type.add_argument("-cse", help="Evaluate Correction in terms of Spans and Error types.", action="store_true")
    parser.add_argument("-single", help="Only evaluate single token edits; i.e. 0:1, 1:0 or 1:1", action="store_true")
    parser.add_argument("-multi", help="Only evaluate multi token edits; i.e. 2+:n or n:2+", action="store_true")
    parser.add_argument("-filt", help="Do not evaluate the specified error types", default=[], nargs="+")
    parser.add_argument("-cat",
                        help='''
Show error category scores.
1: Only show operation tier scores; e.g. R.
2: Only show main tier scores; e.g. NOUN.
3: Show all category scores; e.g. R:NOUN.
''',
                        choices=[1, 2, 3],
                        type=int
                        )
    args = parser.parse_args()

    arg_correction_type = 'cse' if (args.cse is True) else 'cs'

    # Run the program
    CompareM2.compare(args.hyp, args.ref, args.dt, args.ds, arg_correction_type, args.cat, args.single, args.multi,
                      args.filt, args.beta, args.verbose)
