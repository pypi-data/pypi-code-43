from .photo_dl import requests
from .config import headers


def download(img_url):
    img = requests.get(url=img_url, headers=headers)
    return img
