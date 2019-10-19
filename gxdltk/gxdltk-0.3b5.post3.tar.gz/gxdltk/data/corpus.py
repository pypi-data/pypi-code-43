"""
自然语言中数据预处理代码
"""
from gxdltk.data.header import *

__all__ = ["gen_vocab_file", "tokenized"]

def gen_vocab_file(text_data: str, key: str,
                   vocab_file: str = "vocab.txt",
                   spl="\t"):
    """
    TODO: Tokenized method
    TODO: Index by freq
    File Format
    First Line : vocab size
    Others: word spl id
    Parameters
    ----------
    vocab_file
    text_data: json format , json array of
    key: key of each data item
    spl: split in vocab.txt
    Returns
    -------

    """
    voc = set()
    with open(text_data) as textfp:
        text = json.load(textfp)
        for item in text:
            # item is dict type
            if isinstance(item, dict) and key in item.keys():
                text_item = item[key]
                text_item = text_item.split()
                voc = voc | set(text_item)

    with open(vocab_file, 'w') as voc_fp:
        print(f"{len(voc)}")
        for index, word in enumerate(voc):
            print(f"{word}{spl}{index}", file=voc_fp)

def tokenized(sent: str) -> list:
    raise NotImplementedError
