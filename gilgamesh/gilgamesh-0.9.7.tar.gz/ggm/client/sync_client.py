import sys
import zlib
import json
import pickle
import asyncio
import zmq.auth
import time
import socket
from .sync_context import Kontext

from pathlib import Path
from datetime import datetime as dt

from pprint import pprint

import pandas as pd
from pandas.io.json import json_normalize

class GClient(object):
    def __init__(self, ggm_host='local',*args, **kwargs):
        """GILGAMESH™
        
        class GGM(ggm_host='local')
        
        ggm_host: sting found as key in config.json
        """
        cfg_file = Path.home()/'.gilgamesh'/'config'/'client_config.json'
        if not cfg_file.exists():
            raise FileNotFoundError(f'{cfg_file} does not exist.')
        
        with open(cfg_file, 'r') as raw:
            cfg = json.load(raw)
        
        if not ggm_host in cfg:
            raise ValueError(f'{ggm_host} not found in config.')

        cfg = cfg[ggm_host]
        
        self.ctx = Kontext()
        self.client = self.ctx.socket(zmq.DEALER)
        
        keys_path = Path.home()/'.gilgamesh'/'keys'
        client_secret_file = keys_path/'private_keys'/f'{cfg["client_key"]}.key_secret'
        server_public_file = keys_path/'public_keys'/f'{cfg["server_key"]}.key'
        
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
        server_public, _ = zmq.auth.load_certificate(server_public_file)
        
        self.client.curve_secretkey = client_secret
        self.client.curve_publickey = client_public
        self.client.curve_serverkey = server_public
        
        if not 'ip' in cfg:
            try:
                ip = socket.gethostbyname(cfg['hostname'])
                cfg['ip'] = ip
            except:
                raise ConnectionError(f'Could not resolve {hostname}')
        self.client.connect(f'tcp://{cfg["ip"]}:{cfg["port"]}')
        
        self.poller = zmq.Poller()
        self.poller.register(self.client, zmq.POLLIN)

        assert self.check_conn()
        
        self.client.psend(['info'])
        reply = self.client.precv()
        self.remote_dev_id = reply['dev_id']
        
    def show_devices(self):
        self.client.psend(['json', 'get', 'device_state_db', self.remote_dev_id, 'head'])
        reply = self.client.precv()
        devs = [d for d in reply['device_state_db'][self.remote_dev_id]['store'].keys()]
        devs.append(self.remote_dev_id)
        return devs

    def show_measurements(self, device):
        self.client.psend(['json', 'get', 'device_state_db', self.remote_dev_id, 'head'])
        reply = self.client.precv()
        if device == self.remote_dev_id:
            return [d for d in reply['device_state_db'][self.remote_dev_id]['inventory'].keys()]
        else:
            return [d for d in reply['device_state_db'][self.remote_dev_id]['store'][device].keys()]
    
    def show_store(self):
        self.client.psend(['json', 'get', 'device_state_db', self.remote_dev_id, 'head'])
        reply = self.client.precv()
        store = reply['device_state_db'][self.remote_dev_id]['store']
        store[self.remote_dev_id] = reply['device_state_db'][self.remote_dev_id]['inventory']
        return store

    def get_measurement(self, dev_id, measurement, start=None, stop=None, chunk_size=5000, cols=None, pipeline=3, compression=False, progress=True):
        segment = dict()
        if not start:
            return 'error: start must be given'
        else:
            segment['start'] = start

        segment['stop'] = stop or self.get_tmst_now()
        if cols:
            segment['cols'] = cols

        if progress:
            count_cmd = ['series', 'count', dev_id, measurement, segment]
            self.client.psend(count_cmd)
            raw = self.client.precv()
            count_all = raw.pop()
            total_chunks = int(count_all/chunk_size)

        cmd = ['series', 'chunk', dev_id, measurement]

        try:
            start = time.time()
            if progress:
                data = self.download_df(cmd, segment, chunk_size=chunk_size, pipeline=pipeline, compression=False, total_chunks=total_chunks)
            else:
                data = self.download_df(cmd, segment, chunk_size=chunk_size, pipeline=pipeline, compression=False)
            stop = time.time()
            print('\n')
            print(f'-- {dev_id} {measurement} --')
            print(f'{len(data)} records received.')
            print(f'Time elapsed: {round(stop-start, 2)} s')
            print('\n')
        except Exception as e:
            print(f'Error while downloading {dev_id} {measurement} ({e})')
            data = self.clean_pipeline()
        except KeyboardInterrupt:
            data = self.clean_pipeline()

        return data

    def get_tmst_now(self):
        return dt.utcnow().isoformat(sep=' ')

    def clean_pipeline(self):
        msg = []
        while len(dict(self.poller.poll(1000))) > 0:
            _, msg = self.client.drecv()
        if isinstance(msg, dict):
            if 'Reason' in msg.keys():
                pprint(msg['Reason'])
        return True

    def update_progress(self, chunk, total):
        sys.stdout.write(f'\rDownloading chunk {chunk}/{total}')
        sys.stdout.flush()

    def download_df(self, cmd, segment, chunk_size=5000, pipeline=3, compression=False, total_chunks=None):

        CHUNK_SIZE = chunk_size
        PIPELINE = pipeline

        credit = PIPELINE    # Up to PIPELINE chunks in transit
        total = 0            # Total records received
        chunks = 0           # Total chunks received
        offset = 0           # Offset of next chunk request
        thed = pd.DataFrame()# zis is ze data
        cmd.append(segment)

        while True:
            while credit:
                segment['offset'] = offset
                segment['limit']= CHUNK_SIZE
                cmd[-1] = segment
                self.client.dsend(cmd)
                offset += CHUNK_SIZE
                credit -= 1
            route, msg = self.client.drecv(compression)
            if len(msg) > 0:
                tmp_df = json_normalize(msg)
                tmp_df = tmp_df.set_index('time')
                tmp_df.index = pd.to_datetime(tmp_df.index)
                thed = thed.append(tmp_df)
            if total_chunks:
                self.update_progress(chunks, total_chunks)
            chunks += 1
            credit += 1
            size = len(msg)
            if size < CHUNK_SIZE:
                break

        # 'empty' pipeline
        while credit < PIPELINE:
            route, msg = self.client.drecv(compression)
            credit += 1
            if len(msg) > 0:
                tmp_df = json_normalize(msg)
                tmp_df = tmp_df.set_index('time')
                tmp_df.index = pd.to_datetime(tmp_df.index)
                thed = thed.append(tmp_df)
        #remove the prefix for the column names
        thed.rename(columns={k:k.replace('fields.','').replace('tags.','') for k in list(thed.keys())}, inplace=True)
        
        return thed

    def down_raw(self, dev_id, measurement, start=None, stop=None, chunk_size=5000, cols=None, pipeline=3, compression=False):
        segment = dict()
        if not start:
            return 'error: start must be given'
        else:
            segment['start'] = start

        segment['stop'] = stop or self.get_tmst_now()
        if cols:
            segment['cols'] = cols

        cmd = ['series', 'chunk', dev_id, measurement]
        CHUNK_SIZE = chunk_size
        PIPELINE = pipeline

        credit = PIPELINE    # Up to PIPELINE chunks in transit
        total = 0            # Total records received
        chunks = 0           # Total chunks received
        offset = 0           # Offset of next chunk request
        thed = []# zis is ze data
        cmd.append(segment)

        while True:
            while credit:
                segment['offset'] = offset
                segment['limit']= CHUNK_SIZE
                cmd[-1] = segment
                self.client.dsend(cmd)
                offset += CHUNK_SIZE
                credit -= 1
            route, msg = self.client.drecv(compression)
            if len(msg) > 0:
                thed.append(msg)
            chunks += 1
            credit += 1
            size = len(msg)
            if size < CHUNK_SIZE:
                break

        # 'empty' pipeline
        while credit < PIPELINE:
            route, msg = self.client.drecv(compression)
            credit += 1
            if len(msg) > 0:
                thed.append(msg)

        return thed.pop()

    def check_conn(self):        
        self.client.psend(['greetings'])
        while True:
            socks = dict(self.poller.poll(1000))
            if socks.get(self.client) == zmq.POLLIN:
                ret = self.client.precv()
                if ret == ['earthlings']:
                    print('Connecting to gilgamesh successful!')
                    return True
                elif not ret == ['earthlings']:
                    print(f'failed greeting(!) got: {ret}\nretrying...')
                    self.client.psend(['greetings'])
                    continue
            elif not socks.get(self.client):
                self.terminate()
                print(f'Failed connecting to server please check settings!\n')
                return False

    def terminate(self):
        self.client.set(zmq.LINGER, 0)
        self.client.close()
        self.ctx.term()
        print(f'Terminated gilgamesh Client')
