import json
import csv
import pickle
import os
import pandas as pd
from path import Path
import typing
from typing import List, Any
import re
from smart_open import open

from utils.utils import new_file_name


def json2text(path_str_input_json: str, extension=".txt", json_item_text: str = "text"):
    """
    Extract the text from the tweets stored in json and create a text file with the texts
    """
    path_input_json = Path(path_str_input_json)
    path_output_txt = new_file_name(path_input_json, extension)

    with open(path_input_json, mode="r", encoding="utf-8") as json_file:
        with open(path_output_txt, mode="w+", encoding="utf-8") as txt_file:
            tweets: Any = json.load(json_file)
            for tweet in tweets:
                txt_file.write(tweet[json_item_text].replace("\n", "\\n") + "\n")


def make_json(path_input: str) -> None:
    path: Path = Path(path_input)
    with open(path, "r", encoding="utf-8") as file_input:
        liste: List[str] = list()
        with open(
            "/home/julien/Documents/crimea_unrest/resample.json", "w+", encoding="utf-8"
        ) as file:
            for line in file_input:
                result = re.sub(r"'", '"', line)
                result = re.sub(r"(None),", "null,", result)
                result = re.sub(r"(False),", "false,", result)
                result = re.sub(r"(True),", "true,", result)
                result = re.sub(r"u\"", '"', result)
                result = re.sub(r"(href=)(\")([\w./:]+)(\")", doublequoterepl, result)
                result = re.sub(r"(rel=)(\")([\w./:]+)(\")", doublequoterepl, result)
                liste.append(result)
            json.dump(liste, file, ensure_ascii=False, indent=4)


def doublequoterepl(matchobj):
    if matchobj.group(2, 4) == ('"', '"'):
        return matchobj.group(1) + '\\"' + matchobj.group(3) + '\\"'


def csv2pickle(path_input_csv, path_output_pkl):
    with open(path_input_csv, "r") as csv_file:
        with open(path_output_pkl + "text.pkl", "ab") as txt_file:
            next(csv_file)
            reader = csv.reader(csv_file)
            for line in reader:
                pickle.dump((line[1] + "\n").rstrip().split(" "), txt_file)


def csv2txt(path_input_csv, path_output_txt):
    with open(path_input_csv, "r") as csv_file:
        with open(path_output_txt, "w") as txt_file:
            next(csv_file)
            reader = csv.reader(csv_file)
            for line in reader:
                txt_file.write(line[1] + "\n")


def csv2json(path_input_csv, path_output_json):
    with open(
        "/home/julien/Doctorat/Code/Proto/data/CrisisLexT26/2013_Savar_building_collapse/2013_Savar_building_collapse-tweets_labeled.csv",
        "r",
    ) as csv_file:
        with open(
            "/home/julien/Doctorat/Code/Proto/data/CrisisLexT26/2013_Savar_building_collapse/2013_Savar_building_collapse-tweets_labeled.json",
            "w",
        ) as json_file:
            fieldnames = (
                "Tweet ID",
                "Tweet Text",
                "Information Source",
                "Information Type",
                "Informativeness",
            )
            reader = csv.DictReader(csv_file, fieldnames)
            json_file.write("[\n")
            for i, row in enumerate(reader):
                if i != len(reader):
                    json.dump(row, json_file)
                    json_file.write(",\n")
                else:
                    json.dump(row, json_file)
            json_file.write("]")


def csv2json_pd_T26(path_input_csv, path_output_json):
    """
    Convert the csv data from the T26 datasets to a json object.
    ! Use only on small files, because it uses dataframe to convert the data.
    Todo: Create json objects close to those outputed by the twitter API.
    """
    if isinstance(path_input_csv, Path) or isinstance(path_output_json, Path):
        path_csv = str(path_input_csv)
        path_json = str(path_output_json)
    else:
        path_csv = path_input_csv
        path_json = path_output_json

    df = pd.read_csv(
        path_csv,
        header=0,
        names=["ID", "Text", "Source", "Type", "Informativeness"],
        index_col="ID",
    )

    df.to_json(path_json, orient="index")


def csv2json_pd_T6(path_input_csv, path_output_json):
    """
    Convert the csv data from the T6 datasets to a json object.
    ! Use only on small files, because it uses dataframe to convert the data.
    Todo: Create json objects close to those outputed by the twitter API.
    """
    if isinstance(path_input_csv, Path) or isinstance(path_output_json, Path):
        path_csv = str(path_input_csv)
        path_json = str(path_output_json)
    else:
        path_csv = path_input_csv
        path_json = path_output_json

    df = pd.read_csv(
        path_csv, header=0, names=["ID", "Text", "Informativeness"], index_col="ID"
    )
    df[~df.index.duplicated(keep="first")]
    df.to_json(path_json, orient="index")


def unpickle_iter(file):
    try:
        while True:
            yield pickle.load(file)
    except EOFError:
        raise StopIteration


def helper():
    with open("./data/CrisisLexT26/2013_Singapore_haze/text.txt", "rb") as f:
        for item in unpickle_iter(f):
            print(item)


#  Todo: Create a apply to all method
def scroll_through_dirs(path_root_dir, extension=".json"):
    # "/home/julien/Doctorat/Code/Proto/data/CrisisLexT26"
    d = Path(path_root_dir)
    for dir_curr in d.walkdirs():
        dir_name = dir_curr.basename()
        json_file = Path(dir_curr / dir_name + extension)
        csv_file = Path(dir_curr / dir_name + ".txt")
        json2text(json_file, csv_file)


def scroll_csv2json(
    path_root_dir, glob_input="*labeled.csv", ext_output="_tweets_labeled.json"
):
    # "/home/julien/Doctorat/Code/Proto/data/CrisisLexT26"
    path = Path(path_root_dir)
    for dir_curr in path.walkdirs():
        csv_file = dir_curr.files(glob_input)[0]
        dir_name = dir_curr.basename()
        json_file = Path(dir_curr / dir_name + ext_output)
        csv2json_pd_T6(csv_file, json_file)
