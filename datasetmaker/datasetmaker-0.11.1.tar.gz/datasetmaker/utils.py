import os
from typing import Iterable, List, Union, Generator
from pathlib import Path
import io
import zipfile
import gzip
from collections import defaultdict
import boto3
import botocore
import requests
import re
import datetime
import xml.etree.ElementTree as ET
import pandas as pd
from unidecode import unidecode


def read_private_github_file(url: str) -> requests.models.Response:
    return requests.get(url, headers={
        'Authorization': f'token {os.environ.get("github_access_token")}',
        'Accept': 'application/vnd.github.v3.raw'
    })


def wiki_birthday(person: str, lang: str = 'en') -> Union[datetime.date, None]:
    """return the birthday of a person according to wikipedia

    Parameters
    ----------
    person: str, the name of the person of interest, if necessary, with the
    profession or other distinction in parentheses (see examples)

    lang: str, the two letter language string, as of now, only 'en' works

    Return value
    ------------
    a tuple of length 3 of the form (yyyy, mm, dd) or None, if the date of birth
    was not found.

    Side Effects
    ------------
    Will raise an exception if the wikipedia API returns an error

    Examples
    --------
    >>> wiki_birthday('Bert Sakmann')
    datetime.date(1942, 6, 12)
    >>> wiki_birthday('George Bush (racing driver)')
    datetime.date(1911, 1, 29)
    """

    url = f'https://{lang}.wikipedia.org/w/api.php'

    # set params
    params = {}
    params['action'] = 'parse'
    params['format'] = 'json'
    params['page'] = person

    # Call API
    result = requests.get(url, params=params).json()

    if 'error' in result:
        raise Exception(result['error'])
    if 'warnings' in result:
        pass
        # logging.warning(result['warnings'])

    match = re.search(r'<span class=\"bday\">(\d{4})-(\d{2})-(\d{2})</span>',
                      result['parse']['text']['*'])

    if match is None:
        return None

    birthday = tuple(int(s) for s in match.groups())
    return datetime.date(*birthday)


def etree_to_dict(t: ET.Element) -> dict:
    """
    Parse XML data and return a dict

    Parameters
    ----------
    elem : xml.etree.ElementTree.Element
        The XML data as returned from xml.etree.ElementTree.fromstring.

    Examples
    --------
    >>> etree_to_dict(ET.fromstring('<a>b</a>'))
    {'a': 'b'}
    """
    d: dict = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd: defaultdict = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def nice_string(s: str,
                case: Union[str, None] = "lower",
                replace_accents: bool = True,
                replace_special: Union[str, None] = '') -> str:
    """
    Return a nice version of the input string.

    Parameters
    ----------
    case : {'lower', 'upper', 'title', 'capitalize'}
        How to change case.
    unidecode : bool
        Whether to get rid of accented letters using unidecode.
    replace_special : Union(str, None)
        Whether and with what to replace non-alphanumeric characters.
        None for no replacement, string for replacement string.

    TODO: Which exact characters need to be replaced?
    As of now, spaces, hyphens and underscores are allowed.

    Examples
    --------
    >>> nice_string('åáaà ãäâȧ āąạ@ əæéẽ èêëě ėęẹœ íïĩì îıįī ịĭ ǫøȯọ')
    'aaaa aaaa aaa aeee eeee eeeoe iiii iiii ii oooo'

    >>> nice_string('óöòô ōõǒ üũúû ùǔūų ụ čçċ ñṅņ łŋþð ß¢€µ @©®')
    'oooo ooo uuuu uuuu u ccc nnn lNGthd ssCEURu cr'

    Returns
    -------
    str
        The formatted string.
    """
    if case == 'lower':
        s = s.lower()
    elif case == 'upper':
        s = s.upper()
    elif case == 'title':
        s = s.title()
    elif case == 'capitalize':
        s = s.capitalize()

    if replace_accents:
        s = unidecode(s)
    if replace_special is not None:
        s = re.sub(r'[^\w -]', replace_special, s)

    return s


def get_remote_zip(url: str) -> dict:
    """
    Download a zipfile and load the contents into memory.

    Parameters
    ----------
    url : str
        URL to resource.

    Returns
    -------
    dict
        Dictionary with data keyed by filename.
    """
    if str(url).startswith('http'):
        content = requests.get(url).content
    else:
        with open(url, 'rb') as f:
            content = f.read()
    z = zipfile.ZipFile(io.BytesIO(content))
    return {name: z.read(name) for name in z.namelist()}


def pluck(seq: Iterable, name: str) -> List[str]:
    """
    Extract a list of property values from list of dicts

    Parameters
    ----------
    seq : sequence, sequence to pluck values from.
    name : str, key name to pluck.

    Examples
    --------
    >>> data = [{'name': 'usa', 'region': 'America'}, {'name': 'ita', 'region': 'Europe'}]
    >>> pluck(data, 'name')
    ['usa', 'ita']
    """
    return [x[name] for x in seq]


def flatten(seq: Iterable) -> list:
    """
    Perform shallow flattening operation (one level) of seq

    Parameters
    ----------
    items : sequence, the sequence to flatten.

    Examples
    --------
    >>> data = [[1, 2, 3], [4, 5, 6]]
    >>> flatten(data)
    [1, 2, 3, 4, 5, 6]
    """
    out = []
    for item in seq:
        for subitem in item:
            out.append(subitem)
    return out


def stretch(df: pd.DataFrame,
            index_col: Union[str, int, list],
            value_col: Union[str, int],
            sep: str = ';') -> pd.DataFrame:
    """
    Take a dataframe column with delimited values,
    and split the values into new rows.

    Parameters
    ----------
    df, dataframe to perform to operation on.
    index_col: str, identifying column.
    value_col: str, column with delimited values.
    sep: str, delimiting character.

    Examples
    --------
    >>> df = pd.DataFrame([['A;B', 1], ['C;D', 2]])
    >>> df
         0  1
    0  A;B  1
    1  C;D  2

    >>> stretch(df, index_col=1, value_col=0)
       1  0
    0  1  A
    1  1  B
    2  2  C
    3  2  D
    """
    return (df
            .set_index(index_col, append=True)
            .dropna(subset=[value_col])
            .loc[:, [value_col]]
            .stack()
            .str.split(sep, expand=True)
            .stack()
            .unstack(-2)
            .reset_index((0, -1), drop=True)
            .reset_index())


class S3DataStore:
    """
    Wrapper around boto3 for simple access to raw data on S3.
    """
    _bucket_name = 'datastory'
    _folder_name = 'client-data-store'

    def __init__(self) -> None:
        self.s3 = boto3.resource('s3')
        self.bucket = self.s3.Bucket(self._bucket_name)

    def get_object(self, key: str) -> dict:
        if not key.startswith(self._folder_name):
            key = f'{self._folder_name}/{key}'
        return self.s3.Object(self._bucket_name, key).get()

    def list_folders(self) -> Generator:
        for obj in self.bucket.objects.filter(Prefix=self._folder_name):
            path = Path(obj.key)
            if str(path.parent) == self._folder_name:
                yield obj.key

    def list_files_in_folder(self, folder: str, suffix: Union[str, None] = None) -> Generator:
        for obj in self.bucket.objects.filter(Prefix=f'{self._folder_name}/{folder}'):
            path = Path(obj.key)
            if str(path.parent) == self._folder_name:
                continue
            if not suffix:
                yield obj.key
            elif suffix and path.suffix[1:] == suffix:
                yield obj.key

    def read_csv(self, key: str) -> pd.DataFrame:
        obj = self.get_object(key)
        text = io.BytesIO(obj['Body'].read())
        if 'gzip' in obj.get('ContentEncoding', ''):
            return pd.read_csv(text, compression='gzip')
        else:
            return pd.read_csv(text)

    def write_csv(self, frame: pd.DataFrame, key: str) -> None:
        if not key.startswith(self._folder_name):
            key = f'{self._folder_name}/{key}'
        csv_buffer = io.BytesIO()
        with gzip.GzipFile(mode='w', fileobj=csv_buffer) as gz_file:
            frame.to_csv(io.TextIOWrapper(gz_file, 'utf8'), index=False)  # type: ignore
        obj = self.s3.Object(self._bucket_name, key)
        obj.put(Body=csv_buffer.getvalue(), ContentEncoding='gzip', ContentType='text/csv')

    def obj_exists(self, key: str) -> bool:
        if not key.startswith(self._folder_name):
            key = f'{self._folder_name}/{key}'
        try:
            self.s3.Object(self._bucket_name, key).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise
        return True


class SDMXHandler:
    """
    Requesting and transforming SDMX-json data.

    Parameters
    ----------
    dataset : str
        dataset identifier
    loc : list
        list of countries
    subject : list
        list of subjects
    """

    # TODO: URL should not be hardcoded
    base_url = "https://stats.oecd.org/sdmx-json/data"

    def __init__(self, dataset: str,
                 loc: list = [],
                 subject: list = [],
                 **kwargs: str):
        loc = "+".join(loc)  # type: ignore
        subject = "+".join(subject)  # type: ignore
        filters = f"/{subject}.{loc}" if loc or subject else ''
        url = f"{self.base_url}/{dataset}{filters}/all"
        r = requests.get(url, params=kwargs)
        self.resp = r.json()

    def _map_dataset_key(self, key: str) -> dict:
        key = [int(x) for x in key.split(":")]  # type: ignore
        return {y["name"]: y["values"][x]["id"] for
                x, y in zip(key, self.dimensions)}

    def _map_attributes(self, attrs: list) -> dict:
        attrs = [x for x in attrs if x is not None]
        return {y["name"]: y["values"][x]["id"] for
                x, y in zip(attrs, self.attributes)}

    @property
    def periods(self) -> dict:
        return self.resp["structure"]["dimensions"]["observation"][0]

    @property
    def dimensions(self) -> list:
        return self.resp["structure"]["dimensions"]["series"]

    @property
    def attributes(self) -> list:
        return self.resp["structure"]["attributes"]["series"]

    @property
    def data(self) -> list:
        observations = []
        for key, unit in self.resp["dataSets"][0]["series"].items():
            dimensions = self._map_dataset_key(key)
            attributes = self._map_attributes(unit["attributes"])
            z = zip(self.periods["values"], unit["observations"].items())
            for period, (_, observation) in z:
                data = {"Value": observation[0]}
                data[self.periods["name"]] = period["id"]
                data.update(dimensions)
                data.update(attributes)
                observations.append(data)
        return observations
