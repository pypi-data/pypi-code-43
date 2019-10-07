# mostly copies the code in the datasets module of the fastai v1 library (as of early Oct. 2019)

import os
import requests
import hashlib
import tarfile
from pathlib import Path
from fastprogress.fastprogress import progress_bar

Path.ls = lambda x: list(x.iterdir())

MODEL_URL = 'http://files.fast.ai/models/'
URL = 'http://files.fast.ai/data/examples/'

class URLs():
    "Global constants for dataset and model URLs."
    LOCAL_PATH = os.getcwd()
    S3 = 'https://s3.amazonaws.com/fast-ai-'

    S3_IMAGE    = f'{S3}imageclas/'
    S3_NLP      = f'{S3}nlp/'
    S3_MODEL    = f'{S3}modelzoo/'

    # main datasets
    HUMAN_NUMBERS       = f'{URL}human_numbers'
    IMDB                = f'{S3_NLP}imdb'
    IMDB_SAMPLE         = f'{URL}imdb_sample'
    ML_SAMPLE           = f'{URL}movie_lens_sample'
    MNIST_SAMPLE        = f'{URL}mnist_sample'
    MNIST_TINY          = f'{URL}mnist_tiny'
    MNIST_VAR_SIZE_TINY = f'{S3_IMAGE}mnist_var_size_tiny'

    # image classification datasets
    MNIST        = f'{S3_IMAGE}mnist_png'

    # NLP datasets
    AG_NEWS                 = f'{S3_NLP}ag_news_csv'
    AMAZON_REVIEWS          = f'{S3_NLP}amazon_review_full_csv'
    AMAZON_REVIEWS_POLARITY = f'{S3_NLP}amazon_review_polarity_csv'
    DBPEDIA                 = f'{S3_NLP}dbpedia_csv'
    MT_ENG_FRA              = f'{S3_NLP}giga-fren'
    SOGOU_NEWS              = f'{S3_NLP}sogou_news_csv'
    WIKITEXT                = f'{S3_NLP}wikitext-103'
    WIKITEXT_TINY           = f'{S3_NLP}wikitext-2'
    YAHOO_ANSWERS           = f'{S3_NLP}yahoo_answers_csv'
    YELP_REVIEWS            = f'{S3_NLP}yelp_review_full_csv'
    YELP_REVIEWS_POLARITY   = f'{S3_NLP}yelp_review_polarity_csv'

    #Pretrained models
    OPENAI_TRANSFORMER = f'{S3_MODEL}transformer'
    WT103_FWD          = f'{S3_MODEL}wt103-fwd'
    WT103_BWD          = f'{S3_MODEL}wt103-bwd'

_checks = {
    URLs.AG_NEWS:(11784419, 'b86f328f4dbd072486591cb7a5644dcd'),
    URLs.AMAZON_REVIEWS_POLARITY:(688339454, '676f7e5208ec343c8274b4bb085bc938'),
    URLs.AMAZON_REVIEWS:(643695014, '4a1196cf0adaea22f4bc3f592cddde90'),
    URLs.DBPEDIA:(68341743, '239c7837b9e79db34486f3de6a00e38e'),
    URLs.HUMAN_NUMBERS:(30252, '8a19c3bfa2bcb08cd787e741261f3ea2'),
    URLs.IMDB:(144440600, '90f9b1c4ff43a90d67553c9240dc0249'),
    URLs.IMDB_SAMPLE:(571827, '0842e61a9867caa2e6fbdb14fa703d61'),
    URLs.ML_SAMPLE:(51790, '10961384dfe7c5181460390a460c1f77'),
    URLs.MNIST:(15683414, '03639f83c4e3d19e0a3a53a8a997c487'),
    URLs.MNIST_SAMPLE:(3214948, '2dbc7ec6f9259b583af0072c55816a88'),
    URLs.MNIST_TINY:(342207, '56143e8f24db90d925d82a5a74141875'),
    URLs.MNIST_VAR_SIZE_TINY:(565372, 'b71a930f4eb744a4a143a6c7ff7ed67f'),
    URLs.MT_ENG_FRA:(2598183296, '69573f58e2c850b90f2f954077041d8c'),
    URLs.OPENAI_TRANSFORMER:(432848315, '024b0d2203ebb0cd1fc64b27cf8af18e'),
    URLs.SOGOU_NEWS:(384269937, '950f1366d33be52f5b944f8a8b680902'),
    URLs.WIKITEXT:(190200704, '2dd8cf8693b3d27e9c8f0a7df054b2c7'),
    URLs.WIKITEXT_TINY:(4070055, '2a82d47a7b85c8b6a8e068dc4c1d37e7'),
    URLs.WT103_FWD:(105067061, '7d1114cd9684bf9d1ca3c9f6a54da6f9'),
    URLs.WT103_BWD:(105205312, '20b06f5830fd5a891d21044c28d3097f'),
    URLs.YAHOO_ANSWERS:(319476345, '0632a0d236ef3a529c0fa4429b339f68'),
    URLs.YELP_REVIEWS_POLARITY:(166373201, '48c8451c1ad30472334d856b5d294807'),
    URLs.YELP_REVIEWS:(196146755, '1efd84215ea3e30d90e4c33764b889db'),
}

def _expand_path(fpath): return Path(fpath).expanduser()
def url2name(url): return url.split('/')[-1]

def ifnone(a, b):
    "`a` if `a` is not None, otherwise `b`."
    return b if a is None else a

def download_url(url, dest, overwrite=False, pbar=None,
        show_progress=True, chunk_size=1024*1024, timeout=4, retries=5):
    "Download `url` to `dest` unless it exists and not `overwrite`."
    if os.path.exists(dest) and not overwrite: return

    s = requests.Session()
    s.mount('http://',requests.adapters.HTTPAdapter(max_retries=retries))
    u = s.get(url, stream=True, timeout=timeout)
    try: file_size = int(u.headers["Content-Length"])
    except: show_progress = False

    with open(dest, 'wb') as f:
        nbytes = 0
        if show_progress: pbar = progress_bar(range(file_size), auto_update=False, leave=False, parent=pbar)
        try:
            for chunk in u.iter_content(chunk_size=chunk_size):
                nbytes += len(chunk)
                if show_progress: pbar.update(nbytes)
                f.write(chunk)
        except requests.exceptions.ConnectionError as e:
            fname = url.split('/')[-1]
            from fastai.datasets import Config
            data_dir = Config().data_path()
            timeout_txt =(f'\n Download of {url} has failed after {retries} retries\n'
                          f' Fix the download manually:\n'
                          f'$ mkdir -p {data_dir}\n'
                          f'$ cd {data_dir}\n'
                          f'$ wget -c {url}\n'
                          f'$ tar -zxvf {fname}\n\n'
                          f'And re-run your code once the download is successful\n')
            print(timeout_txt)
            import sys;sys.exit(1)


def url2path(url, data=True, ext='.tgz'):
    "Change `url` to a path."
    name = url2name(url)
    return datapath4file(name, ext=ext, archive=False) if data else modelpath4file(name, ext=ext)

def _url2tgz(url, data=True, ext='.tgz'):
    return datapath4file(f'{url2name(url)}{ext}', ext=ext) if data else modelpath4file(f'{url2name(url)}{ext}', ext=ext)

def modelpath4file(filename, ext='.tgz'):
    "Return model path to `filename`, checking locally first then in the config file."
    local_path = Path(URLs.LOCAL_PATH)/'models'/filename
    return local_path

def datapath4file(filename, ext='.tgz', archive=True):
    "Return data path to `filename`, checking locally first then in the config file."
    local_path = Path(URLs.LOCAL_PATH)/'data'/filename
    return local_path

def download_data(url, fname=None, data=True, ext='.tgz'):
    "Download `url` to destination `fname`."
    fname = Path(ifnone(fname, _url2tgz(url, data, ext=ext)))
    os.makedirs(fname.parent, exist_ok=True)
    if not fname.exists():
        print(f'Downloading {url}')
        download_url(f'{url}{ext}', fname)
    return fname

def _check_file(fname):
    size = os.path.getsize(fname)
    with open(fname, "rb") as f:
        hash_nb = hashlib.md5(f.read(2**20)).hexdigest()
    return size,hash_nb

def untar_data(url, fname=None, dest=None, data=True, force_download=False):
    "Download `url` to `fname` if `dest` doesn't exist, and un-tgz to folder `dest`."
    dest = url2path(url, data) if dest is None else Path(dest)/url2name(url)
    fname = Path(ifnone(fname, _url2tgz(url, data)))
    if force_download or (fname.exists() and url in _checks and _check_file(fname) != _checks[url]):
        print(f"A new version of the {'dataset' if data else 'model'} is available.")
        if fname.exists(): os.remove(fname)
        if dest.exists(): shutil.rmtree(dest)
    if not dest.exists():
        fname = download_data(url, fname=fname, data=data)
        if url in _checks:
            assert _check_file(fname) == _checks[url], f"Downloaded file {fname} does not match checksum expected! Remove that file from {Config().data_archive_path()} and try your code again."
        tarfile.open(fname, 'r:gz').extractall(dest.parent)
    return dest
