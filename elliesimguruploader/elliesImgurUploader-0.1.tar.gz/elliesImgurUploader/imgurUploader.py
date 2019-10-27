#!/bin/python3 

import argparse
import base64
import os
import requests
from tqdm import tqdm

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--files', '-f', nargs='+')
    p.add_argument('--title', '-t', nargs='?', default="Choke Me Daddy")
    p.add_argument('-c', action='store_true')
    return p.parse_args()

def create_album(album_title : str, auth : dict) -> tuple:
    api_endpoint = 'https://api.imgur.com/3/album'
    body = {"title"  : album_title}
    r = requests.post(api_endpoint, data=body, headers=auth)
    raw = r.json()
    os.write(2, bytes(
        f'Created Album {album_title}\nid : {raw["data"]["id"]}\ndeletehash : {raw["data"]["deletehash"]}', 'utf-8'
            ))
    return (f"{raw['data']['id']}", f"{raw['data']['deletehash']}")

def upload_image(path_to_image : str, auth : dict, album_hash : str) -> tuple:
    api_endpoint = "https://api.imgur.com/3/upload"
    with open(path_to_image, 'rb') as f:
        base64Image = base64.b64encode(f.read())
    body = {"image" : base64Image,
            "album" : album_hash}
    r = requests.post(api_endpoint, data=body, headers=auth)
    raw = r.json()
    return (path_to_image, raw['data']['id'], raw['data']['deletehash'], raw['data']['link'])

def handle_rate_limit(images : list, message : str):
    print(message)
    with open("/home/ellie/bin/imgurlog.txt", 'w') as f:
        for j in [ i.__str__() for i in images ]:
            f.write(f'{j}\n')
    exit(1)

def get_album_info(album_hash : str, auth : dict) -> str:
    endpoint = f'https://api.imgur.com/3/album/{album_hash}'
    r = requests.get(endpoint, headers=auth)
    raw = r.json()['data']
    os.write(2, bytes(f'Got link {{{raw["link"]}}} for {raw["title"]}\n', 'utf-8'))
    return raw['link']

def main(files : list, title : str) -> str:
    image_extensions = [ "jpeg", "png", "jpg", "gif" ]
    files = list(filter(lambda x : x.split('.')[-1] in image_extensions, files))
    images = []
    auth_headers = {"Authorization" : "Client-ID 6c45adac556176f"}
    album_id, album_hash = create_album(title, auth_headers)
    pbar =  tqdm(range(len(files)))
    for i in pbar:
        pbar.set_description(f'{i}/{len(files)}')
        images.append(upload_image(files[i], auth_headers, album_hash))
    info = get_album_info(album_id, auth_headers)
    return (title, info)

if __name__ == '__main__':
    a = get_args()
    print(main(a.files, a.title))


