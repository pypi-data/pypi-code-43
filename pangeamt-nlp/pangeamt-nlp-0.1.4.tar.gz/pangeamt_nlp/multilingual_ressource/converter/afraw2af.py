import operator
import os
from pangeamt_nlp.utils.lang_detector import LangDetector
import json


def afraw2af(
        raw,
        af=None,
        left_translator = None,
        left_translation_type= None,
        right_translator = None,
        right_translation_type=None,
        corpus_file=None,
        corpus_name=None,
        corpus_domain=None):

    if not os.path.isfile(raw):
        raise ValueError(f"Af file `{raw}` not found")

    if not af:
        filename, file_extension = os.path.splitext(raw)
        af = filename + '.af'
    else:
        filename, file_extension = os.path.splitext(af)
        if not file_extension:
            raise ValueError(f"Af file `{af}` extension should be .af")

    if os.path.isfile(af):
        raise ValueError(f'{af} file already exists')

    id_index, left_index, right_index, left_lang, right_lang = _afraw_info(raw)

    with open(af, 'w', encoding='utf-8') as af_f:
        header = {
            "left": {
                "lang": left_lang,
                "translator": left_translator,
                "translationType": left_translation_type
            },
            "right": {
                "lang": right_lang,
                "translator": right_translator,
                "translationType": right_translation_type
            },
            "corpus": {
                "file": corpus_file,
                "name": corpus_name,
                "domain": corpus_domain,
            }
        }
        header = json.dumps(header, ensure_ascii=False, indent=4) + "\n###\n"
        af_f.write(header)
        with open(raw, 'r', encoding='utf-8') as raw_f:
            for i, line in enumerate(raw_f):
                if id_index is None:
                    line = str(i) + '|||' + line
                af_f.write(line)


def _afraw_info(raw):
    sep= '|||'
    lang_detector = LangDetector()
    with open(raw, 'rb') as f:
        for i, bline in enumerate(f):
            try:
                line = bline.decode('utf-8')
            except Exception as e :
                raise ValueError(f'Encoding error at line {i+1}:' + str(e))

            line = line.strip()
            parts = line.split(sep)
            left_langs = {}
            right_langs = {}

            # Get format
            if i == 0:
                # Find the separator
                if sep not in line:
                    raise ValueError(f'Can not find sep {sep} in raw af file {raw}')

                # Find the separator
                l = len(parts)
                if l == 3:
                    id_index = 0
                    left_index = 1
                    right_index = 2
                elif l==2:
                    id_index = None
                    left_index = 0
                    right_index = 1
                else:
                    raise ValueError(f'Aligned format should have 2 or 3 parts')

            # get left and right
            left = parts[left_index]
            right = parts[right_index]

            # Get language
            if i<200:
                left_lang = lang_detector.detect(left)
                if left_lang not in left_langs:
                    left_langs[left_lang] = 0
                else:
                    left_langs[left_lang] += 1

                right_lang = lang_detector.detect(right)
                if right_lang not in right_langs:
                    right_langs[right_lang] = 0
                else:
                    right_langs[right_lang] += 1
            else:
                break

            error = False
            try:
                left_lang = max(left_langs.items(), key=operator.itemgetter(1))[0]
                right_lang = max(right_langs.items(), key=operator.itemgetter(1))[0]
            except:
                error = True

            if error or left_lang is None or right_lang is None:
                raise ValueError(f'Unable to detect language.\n Left langs: {left_langs} \n Right langs  {right_langs}')

            return id_index, left_index, right_index, left_lang, right_lang