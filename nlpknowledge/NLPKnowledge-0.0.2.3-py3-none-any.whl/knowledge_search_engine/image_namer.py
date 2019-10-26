import mimetypes
import os

import pytesseract
from PIL import Image
from spacy.lang.en import English
from spacy.pipeline import Sentencizer
from summa import keywords
from summa.summarizer import summarize

from . import log

IMAGE_FORMATS = ["image/png", "image/jpeg"]
IMAGE_FORMAT_PREFIXES_MAP = {"image/png": ".png", "IMAGE/PNG": ".PNG", "image/jpeg": ".jpg", None: None}

nlp = English()
sentenizer = Sentencizer(punct_chars=['.', '!', '?', '...'])
nlp.add_pipe(sentenizer)


def _image_text_is_valid(cleaned_image_to_text):
    nlp_obj = nlp(cleaned_image_to_text)
    num_sentences = len(list(nlp_obj.sents))
    if num_sentences > 1:
        return True
    return False


def get_text_from_image(img_path):
    try:
        image = Image.open(img_path)
        image_to_text = pytesseract.image_to_string(image, lang="eng+rus")
    except pytesseract.pytesseract.TesseractError as e:
        log.error("Pytesseract failed to process: %s", img_path)
        log.error(str(e))
        return None
    else:
        return image_to_text


def get_summary(**kwargs):
    cleaned_image_to_text = kwargs["cleaned_image_to_text"]
    image_to_text = kwargs["image_to_text"]
    img_path = kwargs["img_path"]

    summary = summarize(cleaned_image_to_text, ratio=0.2, words=20)
    if not summary:
        log.debug("Extracting dirty summary: %s", img_path)
        summary = summarize(image_to_text, ratio=0.2, words=20)
        if not summary:
            log.warning("No summary found for: %s", img_path)
            return ''
    return summary


def rename_file(**kwargs):
    summary = kwargs["summary"]
    key_words = kwargs["key_words"]
    content_type = kwargs["content_type"]
    cur_dir = kwargs["cur_dir"]
    img_path = kwargs["img_path"]
    new_file_name = "{_summary};keywords-{_keywords}{_content_type}"
    new_file_name = new_file_name.format(_summary=summary, _keywords=f"{key_words}", _content_type=content_type)
    renamed_file = os.path.join(cur_dir, new_file_name)
    try:
        os.rename(img_path, renamed_file)
    except OSError:
        log.warning("File name is to long: %s", img_path)


def clean_summary(summary):
    summary = summary.replace("\n", " ").replace(":", "").replace("/", "")
    summary = ' '.join(filter(None, summary.split(' ')))
    return summary


def raw_screenshots_namer(path=None, ignore_named=False):
    all_path_files = os.listdir(path) if os.path.isdir(path) else [path.split(os.sep)[-1]]
    if os.path.isfile(path):
        path_list = path.split(os.sep)
        all_path_files = [path_list.pop()]
        path = os.sep.join(path_list)

    for file_path in all_path_files:
        img_path = os.path.join(path, file_path)
        image_is_named = "Снимок экрана" not in img_path and "UNADJUSTEDNONRAW_thumb" not in img_path
        if ignore_named and image_is_named:
            log.debug("Screen already has name, ignore")
            continue
        file_content_type, *_ = mimetypes.guess_type(img_path)
        if file_content_type in IMAGE_FORMATS:
            content_type = file_content_type.upper() if img_path.endswith(".PNG") else file_content_type
            content_type = IMAGE_FORMAT_PREFIXES_MAP[content_type]
            image_to_text = get_text_from_image(img_path)
            if not image_to_text:
                continue
            cleaned_image_to_text = image_to_text.replace("\n", " ")
            if _image_text_is_valid(cleaned_image_to_text):
                summary = get_summary(image_to_text=image_to_text, cleaned_image_to_text=cleaned_image_to_text,
                                      img_path=img_path)
                if not summary:
                    rename_file(summary="no summary file", content_type=content_type, cur_dir=path, img_path=img_path)
                    continue
                summary = clean_summary(summary)
                key_words = keywords.keywords(image_to_text, words=3)
                key_words = key_words.replace("\n", "-")
                rename_file(summary=summary, key_words=key_words, content_type=content_type, cur_dir=path,
                            img_path=img_path)
            else:
                log.warning("Not valid image: %s", img_path)
    log.debug("Done")
