import os
import sys
import json
import datetime
import tempfile
import subprocess

import requests

from . import util

def get_latest_release():
    headers = {'Content-Type': 'application/json'}
    resp = requests.get('https://api.github.com/repos/obniz/obnizos-esp32w/releases', headers=headers)
    json_data = resp.json()
    json_data.sort(
        key=lambda x: datetime.datetime.fromisoformat(x['published_at'].replace('Z', '+00:00')),
        reverse=True)
    tag_name = json_data[0]['tag_name']
    return tag_name

def command(args):
    if args.port:
        selected_port = args.port
    else:
        selected_port = util.select_port()

    # obnizOSのクローンおよび更新
    print()
    latest_release = get_latest_release()
    ## 一時ファイルにobnizOSをクローンしてくる
    with tempfile.TemporaryDirectory() as dirname:
        filenames = ['bootloader.bin', 'obniz.bin', 'partitions.bin']
        for file in filenames:
            print("Downloading {}...".format(file))
            
            resp = requests.get("https://raw.github.com/obniz/obnizos-esp32w/{}/{}".format(latest_release, file))
            save_to = os.path.join(dirname, file)
            if resp.ok:
                with open(save_to, 'wb') as save_file:
                    save_file.write(resp.content)
            else:
                print("Error: failed to download {}.".format(file))
                sys.exit(1)
        # obnizOSの書き込み
        print()
        proc = subprocess.run(
            "esptool.py --port {} -b {} --after hard_reset write_flash 0x1000 bootloader.bin 0x10000 obniz.bin 0x8000 partitions.bin".format(selected_port, args.bps),
            shell=True,
            cwd=dirname
        )
        proc = subprocess.run(
                "python -m serial.tools.miniterm {} {}".format(selected_port, 115200),
            shell=True,
            cwd=dirname
        )
