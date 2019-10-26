import mimetypes
import os

import pytesseract
from PIL import Image

from . import log

IMAGE_FORMATS = ["image/png", "image/jpeg"]
IMAGE_FORMAT_PREFIXES_MAP = {"image/png": ".png", "IMAGE/PNG": ".PNG", "image/jpeg": ".jpg", None: None}


def image_to_text_files(**kwargs):
    currdir = kwargs["path"]

    all_path_files = os.listdir(currdir) if os.path.isdir(currdir) else [currdir.split(os.sep)[-1]]
    if os.path.isfile(currdir):
        path_list = currdir.split(os.sep)
        all_path_files = [path_list.pop()]
        currdir = os.sep.join(path_list)

    for file in all_path_files:
        path = os.path.join(currdir, file)
        if not os.path.isdir(path):
            content_type, *_ = mimetypes.guess_type(file)
            content_type = content_type.upper() if file.endswith(".PNG") else content_type
            if content_type in IMAGE_FORMATS:
                text_filepath = path.replace(IMAGE_FORMAT_PREFIXES_MAP[content_type], '.txt')
                file_was_not_generated_before = not os.path.isfile(text_filepath)
                if file_was_not_generated_before:
                    log.debug(f"Generating new file,  {text_filepath}")
                    image = Image.open(path)
                    try:
                        image_to_text = pytesseract.image_to_string(image, lang="eng+rus")
                        with open(text_filepath, mode="w+") as f:
                            f.write(image_to_text)
                    except pytesseract.pytesseract.TesseractError as e:
                        log.error(f"{str(e)} \n")
                        log.error(f"Failed to process {path}")
        elif os.path.isdir(path) and kwargs.get("recursive"):
            image_to_text_files(path=path)
        else:
            log.debug("Done")
    log.debug("===Done===")
