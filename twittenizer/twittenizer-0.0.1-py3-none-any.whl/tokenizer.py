import json
import re
import typing
from os import listdir
from typing import List

from nltk.tokenize.casual import TweetTokenizer
from path import Path

WHITESPACE = re.compile("[\s\u0020\u00a0\u1680\u180e\u202f\u205f\u3000\u2000-\u200a]+")

PUNCTCHARS = r"['\"“”‘’.?!…,:;-]"

PUNCTSEQ = r"['\"“”‘’]{2,}|[.?!,…]{2,}|[:;]{2,}"

ENTITY = r"&(?:amp|lt|gt|quot);"

URL = (
    r"(?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:[a-z]{2,13})/)"
    + r"(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+"
    + r"(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'.,<>?«»“”‘’])|"
    + r"(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.]"
    + r"(?:com|org|edu|gov|net|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|pro"
    + r"|tel|travel|xxxac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf"
    + r"|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs"
    + r"|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb"
    + r"|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in"
    + r"|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt"
    + r"|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne"
    + r"|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs"
    + r"|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th"
    + r"|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|a|vc|ve|vg|vi|vn|vu|wf|ws|ye|"
    + r"yt|za|zm|zw)\b/?(?!@))"
)

HEART = re.compile(r"""(<3)""")

# TODO: Update with http://en.wikipedia.org/wiki/List_of_emoticons
# TODO: Classify emoticons according to what they express

EMOTICONS = r"""
    (
      [<>]?
      [:;=8]                     # eyes
      [\-o\*\']?                 # optional nose
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      |
      [\)\]\(\[dDpP/\:\}\{@\|\\] # mouth
      [\-o\*\']?                 # optional nose
      [:;=8]                     # eyes
      [<>]?
    )"""

CONTRACTIONS = re.compile(
    "(?i)(\w+)(n['’′]t|['’′]ve|['’′]ll|['’′]d|['’′]re|['’′]s|['’′]m)"
)

ASCII_ARROWS = r"""[\-]+>|<[\-]+"""

MENTION = r"""(@[\w_]+)"""

HASH = r"""(\#+[\w_]+[\w\'_\-]*[\w_]+)"""

HTML_TAGS = r"""<[^>\s]+>"""

EMAIL = (r"""[\w.+-]+@[\w-]+\.([\w-]\.?)+[\w-]""",)

# TODO: Tag capitalized words


class Tokenizer(TweetTokenizer):
    def __init__(self):
        super().__init__()

    def tokenize(self, text: str) -> List[str]:
        res = re.sub(URL, "<URL>", text)
        res = re.sub(MENTION, "<USER>", res)
        res = CONTRACTIONS.sub(r"\1 \2", res)
        res = re.sub(r"/", " / ", res)
        res = re.sub(r"RT", "<RT>", res)
        res = re.sub(HASH, "<HASH>", res)
        # # res = re.sub(EMAIL, "<EMAIL>", res)
        res = re.sub(EMOTICONS, "<EMOTICONS>", res)
        res = re.sub(r"<3", "<HEART>", res)
        res = re.sub(r"[-+]?[.\d]*[\d]+[:,.\d]*", "<NUM>", res)
        res = re.sub(PUNCTCHARS, "", res)

        tokens = super().tokenize(res)

        return tokens


def to_json(path_read_file, path_write_file):
    with open(path_read_file, "r") as read_file:
        with open(path_write_file, "a") as written_file:
            for line in read_file:
                written_file.write(json.dumps(line))


# Preprocessing from the GloVe algo


def new_file_name(input_path: Path, extension: str) -> Path:
    """Provide the path of a new file using the parent dir name.
    
    Arguments:
        input_path {Path} -- The path of a file contained in the targeted dir
        extension {str} -- The extension of the new file
    
    Returns:
        output_path {Path} -- The new path generated
    """
    if "." not in extension:
        raise SyntaxError("Missing '.' character in the extension name")
    output_path: Path = Path(
        Path.joinpath(*input_path.splitall()[:-1])
    ) / input_path.dirname().basename() + extension
    return output_path
