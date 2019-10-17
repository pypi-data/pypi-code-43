# encoding: utf-8

"""
Simpler and (almost) self-contained version of Abzu.

Intended as a "Keep It Simple, Stupid" version.
"""

# Import Python standard libraries
import csv
import hashlib
import numpy as np
from os import path
import re

# TODO: move _RESOURCE_DIR and reading to a utils.py module

# Set the resource directory; this is sage as we already added
# `zip_safe=False` to setup.py
_RESOURCE_DIR = path.join(path.dirname(path.dirname(__file__)), "resources")


def read_data(filename):
    filename = path.join(_RESOURCE_DIR, filename)

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        data = {row.pop("ID"): row for row in reader}

    return data


VOWEL_INV = read_data("vowel_inventories.tsv")
SYLL_PATTERN = read_data("syllable_patterns.tsv")
CONS_INV = read_data("consonant_inventories.tsv")
PHONEME_FREQ = read_data("phoneme_frequency.tsv")

# TODO: move to a utils function
def _np_seed(seed):
    # allows using strings as np seeds, which only takes uint32 or arrays of
    # NOTE: won't set the seed if it is None: if you want to seed none
    # as seed, manuallz call np.random.seed()
    if not seed:
        return
    elif isinstance(seed, str):
        _seed = np.frombuffer(
            hashlib.sha256(seed.encode("utf-8")).digest(), dtype=np.uint32
        )
    else:
        _seed = seed

    np.random.seed(_seed)


def random_vowel_inv(distr=None, seed=None):
    """
    Returns a random vowel inventory.

    This does not include probabilities for weighted random draws inside
    the inventory.
    """

    # if no distribution of inventories/weights is given, build one
    # from abzu_data
    if not distr:
        # initialize an empty distribution
        distr = {}

        # TODO: properly split with zip
        # TODO: rename frequency to weight
        # copy the inventories as a `pop`ulation
        distr["pop"] = [VOWEL_INV[inv_id]["VOWELS"] for inv_id in sorted(VOWEL_INV)]

        # get the ratio and copy the frequencies as `weights`
        weights = [
            float(VOWEL_INV[inv_id]["FREQUENCY"]) for inv_id in sorted(VOWEL_INV)
        ]
        weight_sum = sum(weights)
        distr["weights"] = [w / weight_sum for w in weights]

    # get a random weighted individual
    _np_seed(seed)
    vowel_inv = np.random.choice(distr["pop"], p=distr["weights"], size=1)[0]

    return vowel_inv.split("|")


def random_syll_pattern(distr=None, seed=None):
    """
    Returns a random syllable pattern.
    """

    # if no distribution of inventories/weights is given, build one
    # from abzu_data
    if not distr:
        # initialize an empty distribution
        distr = {}

        # TODO: properly split with zip
        # TODO: rename frequency to weight

        # copy the patterns as a `pop`ulation
        distr["pop"] = [SYLL_PATTERN[pid]["PATTERN"] for pid in sorted(SYLL_PATTERN)]
        # distr["pop"] = [entry["PATTERN"] for entry in SYLL_PATTERN.values()]

        # get the ratio and copy the frequencies as `weights`
        weights = [
            float(SYLL_PATTERN[pid]["FREQUENCY"]) for pid in sorted(SYLL_PATTERN)
        ]
        # weights = [int(entry["FREQUENCY"]) for entry in SYLL_PATTERN.values()]
        weight_sum = sum(weights)
        distr["weights"] = [w / weight_sum for w in weights]

    # get a random weighted individual
    _np_seed(seed)
    pat = np.random.choice(distr["pop"], p=distr["weights"], size=1)[0]

    return pat


def random_cons_inv(distr, seed=None):
    """
    Returns a random consonant inventory from a list of possibilities.
    """

    # numpy.random.choice only works with 1-dimensional values,
    # so we choose the index

    # TODO: add frequency here as well?
    distr_list = [
        [
            distr[distr_id]["INITIAL"],
            distr[distr_id]["MEDIAL"],
            distr[distr_id]["FINAL"],
        ]
        for distr_id in sorted(distr)
    ]

    _np_seed(seed)
    initials, medials, finals = distr_list[np.random.choice(len(distr_list), size=1)[0]]

    # Split the lists of phonemes, making sure there are no empty strings
    # in case of empty lists
    initials = [sound for sound in initials.split("|") if sound]
    medials = [sound for sound in medials.split("|") if sound]
    finals = [sound for sound in finals.split("|") if sound]

    return initials, medials, finals


def random_phonology(inventory, param, base_freq=None, seed=None):
    """
    Returns consonant and vowel inventories with random frequencies.
    """

    # set seed
    _np_seed(seed)

    # load parameters
    perturbation = param.get("perturbation", 1.5)

    # load the base frequency, if it was not provided
    if not base_freq:
        base_freq = {
            v["GRAPHEME"]: float(v["FREQUENCY"]) for v in PHONEME_FREQ.values()
        }

    # the perturbation is basically done by selecting a random number in
    # the requested range, for which we compute the lower and upper bound,
    # and taking the original frequency to that power; a pertubation of zero
    # samples in [1.0, 1.0], which means using the base_freq
    perturb_low = 1.0 - (perturbation / 2.0)
    perturb_high = 1.0 + (perturbation / 2.0)

    # get the mean frequency divided by 1.5, so we have something to default
    # in case of missing graphemes (especially clusters)
    # TODO: this is applying to all clusters right now, as we have a space
    #       between the graphemes in abzu_data but not in phoible
    default_freq = np.mean(list(base_freq.values())) / 1.5

    # compute random frequencies
    vowels = {
        vowel: base_freq.get(vowel, default_freq)
        ** np.random.uniform(low=perturb_low, high=perturb_high)
        for vowel in sorted(inventory["vowels"])
    }

    initials = {
        cons: base_freq.get(cons, default_freq)
        ** np.random.uniform(low=perturb_low, high=perturb_high)
        for cons in sorted(inventory["initials"])
    }

    medials = {
        cons: base_freq.get(cons, default_freq)
        ** np.random.uniform(low=perturb_low, high=perturb_high)
        for cons in sorted(inventory["medials"])
    }

    finals = {
        cons: base_freq.get(cons, default_freq)
        ** np.random.uniform(low=perturb_low, high=perturb_high)
        for cons in sorted(inventory["finals"])
    }

    # correct the new probabilities, so they sum 1.0
    new_inventory = {}
    new_inventory["vowels"] = {k: v / sum(vowels.values()) for k, v in vowels.items()}
    new_inventory["initials"] = {
        k: v / sum(initials.values()) for k, v in initials.items()
    }
    new_inventory["medials"] = {
        k: v / sum(medials.values()) for k, v in medials.items()
    }
    new_inventory["finals"] = {k: v / sum(finals.values()) for k, v in finals.items()}

    return new_inventory


def random_words(num_words, param, seed=None):
    # set the seed
    _np_seed(seed)

    # get parameters as specified or default
    # TODO: default `no_consonant` should depend on the system entropy
    no_cons_low = param.get("no_cons_low", 0.33)
    no_cons_high = param.get("no_cons_high", 0.66)
    base_syl_lambda = param.get("base_syl_lambda", 10)
    remove_length = param.get("remove_length", 0.33)

    # get the 'phonotactics' of the language
    pattern = random_syll_pattern()
    inv = {}
    inv["vowels"] = random_vowel_inv()
    cons_distr = {
        key: value for key, value in CONS_INV.items() if value["PATTERN"] == pattern
    }
    inv["initials"], inv["medials"], inv["finals"] = random_cons_inv(cons_distr)
    phonology = random_phonology(inv, param)
    no_consonant = np.random.uniform(low=no_cons_low, high=no_cons_high)

    # cache keys/values/lengths
    v_keys = sorted(phonology["vowels"])
    v_values = [phonology["vowels"][vowel] for vowel in v_keys]
    v_len = len(v_keys)
    v_range = list(range(len(v_keys)))

    i_keys = sorted(phonology["initials"])
    i_values = [phonology["initials"][initial] for initial in i_keys]
    i_len = len(i_keys)
    i_range = list(range(len(i_keys)))

    m_keys = sorted(phonology["medials"])
    m_values = [phonology["medials"][medial] for medial in m_keys]
    m_len = len(m_keys)
    m_range = list(range(len(m_keys)))

    f_keys = sorted(phonology["finals"])
    f_values = [phonology["finals"][final] for final in f_keys]
    f_len = len(f_keys)
    f_range = list(range(len(f_keys)))

    # generate all words
    words = []
    for word_idx in range(num_words):
        # get the number of syllables from a poisson distribution; we try to
        # correct for entropy by manipulating the lambda, so that languages with
        # simpler phonotactics will tend to have more syllables; we also
        # currently restrict to at most 5 syllables
        syl_lambda = base_syl_lambda / np.sqrt(v_len + m_len)
        num_syl = min(np.random.poisson(syl_lambda) + 1, 5)

        # if we got a single syllable, increase it with another one 66% of the
        # time -- not very chinese like
        # TODO: this is needed because the syllable length distribution in
        #       world languages does not seem to be a Poisson distirbution,
        #       but one whose shape is closer to a gamma one, with many other
        #       factors involved (such as size of inventory)
        if num_syl == 1:
            if np.random.random() < 0.66:
                num_syl = 2

        syl_sounds = []
        for syl in range(num_syl):
            # get a random initial or medial (or nothing)
            if np.random.random() < no_consonant:
                if syl == 0:
                    _ = np.random.choice(i_len, p=i_values)
                    syl_sounds.append(i_keys[_])
                else:
                    _ = np.random.choice(m_len, p=m_values)
                    syl_sounds.append(m_keys[_])

            # get a random vowel
            _ = np.random.choice(v_len, p=v_values)
            syl_sounds.append(v_keys[_])

            # get a random final (or not) if at last syllable and if
            # finals are used
            if syl == num_syl - 1 and f_len:
                if np.random.random() < no_consonant:
                    _ = np.random.choice(f_len, p=f_values)
                    syl_sounds.append(f_keys[_])

        # collect
        words.append(" ".join(syl_sounds))

    # apply basic, "universal", phonotactics
    words = [apply_basic_phonotactics(word) for word in words]

    # remove all length symbols by random decision
    if np.random.random() < remove_length:
        words = [word.replace("ː", "") for word in words]

    return words


# TODO: redo with the sound change engine later
# TODO: make sure there is something left
def apply_basic_phonotactics(word):
    rules = [
        # remove runs of three equal sounds, lengthening
        [r" (.) \1 \1 ", r" \1ː "],
        # remove runs of two equal sounds, lengthening
        [r" (.) \1 ", r" \1ː "],
        # remove runs of two equal sounds, the first long, lengthening
        [r" (.)ː \1 ", r" \1ː "],
        # converts most vowel clusters to vowel+glide or glide + vowel
        [r" (i|y|ɨ|ʉ|ɯ|u|ɪ|ʏ|ʊ|e|o|ɛ|ɜ|ʌ|ɔ|æ|ɐ|a|ɑ|ɒ) (i|y|ɨ|ʏ) ", r" \1 j "],
        [r" (i|y|ɨ|ʉ|ɯ|u|ɪ|ʏ|ʊ|e|o|ɛ|ɜ|ʌ|ɔ|æ|ɐ|a|ɑ|ɒ) (ɯ|u|ʊ) ", r" \1 w "],
        [r" (i|y|ɨ|ʏ) (i|y|ɨ|ʉ|ɯ|u|ɪ|ʏ|ʊ|e|o|ɛ|ɜ|ʌ|ɔ|æ|ɐ|a|ɑ|ɒ) ", r" j \1 "],
        [r" (ɯ|u|ʊ) (i|y|ɨ|ʉ|ɯ|u|ɪ|ʏ|ʊ|e|o|ɛ|ɜ|ʌ|ɔ|æ|ɐ|a|ɑ|ɒ) ", r" w \1 "],
        # don't allow long glides
        [r" (j|w)ː ", r" \1 "],
        # remove less stable glide+vowel combinations
        [r" (i|y|ɨ|ʏ) j ", r" \1 "],
        [r" (ɯ|u|ʊ) w ", r" \1 "],
        [r" j (i|y|ɨ|ʏ) ", r" \1 "],
        [r" w (ɯ|u|ʊ) ", r" \1 "],
        # aspiration
        [r" (p|t|k) h ", r" \1ʰ "],
        # intervocalic /j/ to /ʒ/
        [
            r" (i|y|ɨ|ʉ|ɯ|u|ɪ|ʏ|ʊ|e|o|ɛ|ɜ|ʌ|ɔ|æ|ɐ|a|ɑ|ɒ) j (i|y|ɨ|ʉ|ɯ|u|ɪ|ʏ|ʊ|e|o|ɛ|ɜ|ʌ|ɔ|æ|ɐ|a|ɑ|ɒ) ",
            r" \1 ʒ \2 ",
        ],
        # double j/w still left
        [r" j j ", r" j "],
        [r" w w ", r" w "],
        # fix vowel length problems
        [r" (.)ː \1ː ", r" \1ː "],
        [r" (.) \1ː ", r" \1ː "],
        [r" (.)ː \1 ", r" \1ː "],
        [r" (.) \1 ", r" \1ː "],
        # problems with glides at borders
        [r" # w j ", r" # u j "],
        [r" # j w ", r" # i w "],
        [r" w j # ", r" w i # "],
        [r" j w # ", r" j u # "],
    ]

    # add boundaries for manipulation
    word = " # %s # " % word

    # apply regexes
    for rule in rules:
        word = re.sub(rule[0], rule[1], word)

    # remove boundaries, strip, and return
    word = word.replace("#", "").strip()

    return word


# TODO: implement properly
def single_random_word(seed=None):
    _np_seed(seed)
    return random_words(1, {})[0]
