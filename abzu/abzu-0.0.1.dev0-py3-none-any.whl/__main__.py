#!/usr/bin/env python3
# encoding: utf-8

"""
__main__.py

Module for command-line execution of Abzu.
"""

# Import Python standard libraries
import argparse
import logging
import random

import abzu


def quick_test():
    param = {}

    print("--> random_vowel_inv()")
    for i in range(4):
        print("  %i %s" % (i, abzu.kiss.random_vowel_inv()))
    print()

    print("--> random_syll_pattern()")
    for i in range(4):
        print("  %i %s" % (i, abzu.kiss.random_syll_pattern()))
    print()

    print("--> random_cons_inv()")
    for i in range(4):
        pattern = abzu.kiss.random_syll_pattern()
        distr = {
            key: value
            for key, value in abzu.kiss.CONS_INV.items()
            if value["PATTERN"] == pattern
        }
        initials, medials, finals = abzu.kiss.random_cons_inv(distr)
        print(
            "  %i %i/%i/%i (%s)"
            % (i, len(initials), len(medials), len(finals), pattern)
        )
    print()

    print("--> random_global_freq()")
    base_freq = {
        v["GRAPHEME"]: float(v["FREQUENCY"]) for v in abzu.kiss.PHONEME_FREQ.values()
    }
    print("  items: %i" % len(base_freq))
    print()

    print("--> random_frequency()")
    for i in range(4):
        pattern = abzu.kiss.random_syll_pattern()
        inv = {}
        inv["vowels"] = abzu.kiss.random_vowel_inv()
        cons_distr = {
            key: value
            for key, value in abzu.kiss.CONS_INV.items()
            if value["PATTERN"] == pattern
        }
        inv["initials"], inv["medials"], inv["finals"] = abzu.kiss.random_cons_inv(
            cons_distr
        )
        phonology = abzu.kiss.random_phonology(inv, param)

        print(
            "  items: %i/%i/%i/%i"
            % (
                len(phonology["vowels"]),
                len(phonology["initials"]),
                len(phonology["medials"]),
                len(phonology["finals"]),
            )
        )
    print()

    print("--> random_words()")
    for i in range(4):
        print("  l:", abzu.kiss.random_words(15, param))
    print()


def full_test(args):
    epoch = 0

    lang_a = abzu.textgen.random_labels(5)
    print("Creating random langs at epoch 0")
    print(lang_a)

    for i in range(10):
        epoch += 1
        if random.randint(0, 10) == 7:
            w = abzu.textgen.random_labels(1)[0]
            lang_a[random.randint(0, len(lang_a) - 1)] = w
            print("Random new word in lang_a at epoch %i" % epoch)

    print(lang_a)

    quick_test()


def entry(args):
    print("Language: %s" % abzu.textgen.random_labels(1, args.seed)[0])
    for idx, word in enumerate(
        abzu.kiss.random_words(args.size, param={}, seed=args.seed)
    ):
        print("  %i:\t%s" % (idx + 1, word))


def main():
    # Define the parser for when called from command line
    parser = argparse.ArgumentParser(description="Abzu language simulation.")
    parser.add_argument(
        "--seed", type=str, help="The RNG seed, for reproducibility. Defaults to None."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Whether to log debug information. Defaults to False.",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="The number of words in the vocabulary to be generated. Defaults to 10.",
    )
    ARGS = parser.parse_args()

    # Set the requested logging level (either DEBUG or INFO)
    if ARGS.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Log command-line options, if in debug
    logging.debug(str(ARGS))

    # Apply random seed, if any
    logging.debug("Setting the RNG seed to `%s`", ARGS.seed)
    random.seed(ARGS.seed)

    entry(ARGS)
