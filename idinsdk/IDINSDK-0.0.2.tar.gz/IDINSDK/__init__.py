import ecdsa, requests, base64, gzip, json, hashlib, time, pprint

class IDINVerifier:
    def __init__(self, public_key=None, key_format='pem'):
        if not public_key:
            raise Exception('Please specify public key data')
        if key_format == 'pem':
            self.public_key = ecdsa.VerifyingKey.from_pem(public_key)
        elif key_format == 'hex':
            self.public_key = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key[2:]), curve=ecdsa.NIST256p)
        else:
            raise Exception('Invalid key format specified')

    def to_hex(self):
        return '04' + self.public_key.to_string().hex()

    def to_pem(self):
        return self.public_key.to_pem().decode()

    def verify(self, signature, data):
        try:
            payload = data.encode()
        except:
            payload = data

        try:
            self.public_key.verify(bytes.fromhex(signature), payload, hashfunc=hashlib.sha256)
            valid = True
        except:
            valid = False

        return valid



class IDINSigner:
    def __init__(self, private_key=None, key_format='pem'):
        if private_key:
            if key_format == 'pem':
                self.private_key = ecdsa.SigningKey.from_pem(private_key)
            else:
                raise Exception('Invalid key format specified')
        else:
            self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)

        self.public_key = IDINVerifier(self.private_key.get_verifying_key().to_pem(), key_format='pem')

    def sign(self, data):
        try:
            payload = data.encode()
        except:
            payload = data
        return self.private_key.sign(payload, hashfunc=hashlib.sha256).hex()

    def to_pem(self):
        return self.private_key.to_pem().decode()

    def to_hex(self):
        return self.private_key.to_string().hex()

    def get_verifier(self):
        return self.public_key




class IDINAPI:
    def __init__(self, host='https://testnet.finema.co', debug=False):
        self.host = host
        self.debug = debug
        self._check_api_health()


    def _check_api_health(self):
        req = requests.get(self.host + '/health')
        if req.status_code != 200:
            raise Exception('Cannot connect to IDIN API endpoint')


    def _get_did_nonce(self, did_address):
        req = requests.get(self.host + '/abci_query?data="{}"&path="DID_INFO"'.format(did_address))

        try:
            nonce = int(json.loads(base64.b64decode(req.json()['result']['response']['value']))['nonce'])
        except:
            raise Exception('Could not get nonce for DID {}'.format(did_address))

        return nonce


    def _build_tx(self, signer, tx_body, tx_did, tx_op):
        if tx_did:
            nonce = self._get_did_nonce(tx_did)
        else:
            nonce = 1

        data = {
            'body': tx_body,
            'header': {
                'addr': tx_did,
                'nonce': nonce,
                'op': tx_op,
                'ver': '0.1'
            }
        }

        if self.debug:
            print('[+] _build_tx(): tx data body')
            pprint.pprint(data)
            print()

        data_json = json.dumps(data).encode()

        signature = signer.sign(data_json)

        tx = {
            "data": data_json.hex(),
            "signature": signature,
            "publicKey": signer.get_verifier().to_hex(),
            "encoding": "BASE64/JSON",
            "keyType": "IDINSecp256r12019",
        }

        json_tx = json.dumps(tx).encode()
        json_tx_gzipped = gzip.compress(json_tx, compresslevel=1)
        tx_encoded = base64.b64encode(json_tx_gzipped).decode()

        if self.debug:
            print('[+] _build_tx(): tx data encoded')
            pprint.pprint(tx_encoded)
            print()

        return tx_encoded
        

    def _send_tx(self, tx, async_tx=True):
        if async_tx:
            req = requests.get(self.host + '/broadcast_tx_async?tx="{}"'.format(tx))
        else:
            req = requests.get(self.host + '/broadcast_tx_sync?tx="{}"'.format(tx))

        if req.status_code != 200:
            raise Exception('Invalid blockchain status code while submitting transaction')

        try:
            result = req.json()
        except:
            raise Exception('Invalid blockchain response while submitting transaction')

        if self.debug:
            print('[+] _send_tx(): result')
            pprint.pprint(result)
            print()

        if 'result' not in result or 'error' in result:
            raise Exception('IDIN blockchain error: ' + result['error']['data'])

        tx_hash = result['result']['hash']

        return tx_hash


    def did_create(self, signer, async_tx=False):
        tx_body = ''
        tx_did = ''
        tx_op = 'did:hello'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)

        while True:
            req = requests.get(self.host + '/tx?hash=0x{}'.format(tx_hash))
            result = req.json()
            if 'result' in result:
                break
            else:
                time.sleep(0.5)
        
        results = req.json()['result']['tx_result']['tags']
        for result in results:
            if result['key'] == 'YWRkcmVzcw==':
                did_address = base64.b64decode(result['value']).decode()
                break
        return did_address


    def did_add_public_key_sign(self, did_address, signer):
        nonce = self._get_did_nonce(did_address)
        public_key = signer.get_verifier().to_hex()
        tx_op = 'did:add'
        payload = '{}:{}:{}:{}'.format(tx_op, did_address, public_key, nonce)
        if self.debug:
            print('[+] did_add_public_key_sign(): payload')
            pprint.pprint(payload)
            print()
        return signer.sign(payload)
        

    def did_add_public_key(self, did_address, signer, public_key_to_add, signature_of_public_key_to_add, async_tx=True):
        tx_body = json.dumps({
            'publicKey': public_key_to_add,
            'signature': signature_of_public_key_to_add,
            'type': 'IDINSecp256r12019',
        }).encode().hex()
        tx_did = did_address
        tx_op = 'did:add'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)
        return tx_hash
        

    def did_list_public_keys(self, did_address):
        req = requests.get('{}/abci_query?data="{},1,20"&path="DID_KEYS"'.format(self.host, did_address))
        result = req.json()
        if 'result' not in result:
            raise Exception('Invalid DID')
        else:
            return json.loads(base64.b64decode(result['result']['response']['value']))['data']


    def did_get_public_key_detail(self, did_address, public_key_hex):
        req = requests.get('{}/abci_query?data="{},{}"&path="DID_KEY"'.format(self.host, did_address, public_key_hex))
        result = req.json()
        if 'result' not in result or 'value' not in result['result']['response']:
            raise Exception('Invalid DID or public key')
        else:
            return json.loads(base64.b64decode(result['result']['response']['value']))


    def did_remove_public_key(self, did_address, signer, public_key_to_remove, async_tx=True):
        tx_body = public_key_to_remove
        tx_did = did_address
        tx_op = 'did:revoke:key'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)
        return tx_hash


    def did_recovery_register_sign(self, signer_did, signer, did_to_recover):
        nonce = self._get_did_nonce(did_to_recover)
        tx_op = 'did:recovery:hello'
        payload = '{}:{}:{}:{}'.format(tx_op, did_to_recover, signer_did, nonce)
        tx_body = {
            'publicKey': signer.get_verifier().to_hex(),
            'signature': signer.sign(payload),
            'type': 'IDINSecp256r12019',
            'byAddr': signer_did,
        }
        if self.debug:
            print('[+] did_recovery_register_sign(): tx_body')
            pprint.pprint(tx_body)
            print()
        return tx_body


    def did_recovery_register(self, did_address, signer, recovery_list, async_tx=True):
        tx_body = json.dumps(recovery_list).encode().hex()
        tx_did = did_address
        tx_op = 'did:recovery:hello'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)
        return tx_hash
        

    def did_recovery_sign(self, new_public_key, signer, signer_did, did_to_recover):
        nonce = self._get_did_nonce(did_to_recover)
        tx_op = 'did:recovery'
        payload = '{}:{}:{}:{}'.format(tx_op, did_to_recover, new_public_key, nonce)
        tx_body = {
            'publicKey': signer.get_verifier().to_hex(),
            'signature': signer.sign(payload),
            'type': 'IDINSecp256r12019',
            'byAddr': signer_did,
        }
        if self.debug:
            print('[+] did_recovery_sign(): tx_body')
            pprint.pprint(tx_body)
            print()
        return tx_body


    def did_recovery(self, did_address, signer, recovery_list, async_tx=True):
        tx_body = json.dumps(recovery_list).encode().hex()
        tx_did = did_address
        tx_op = 'did:recovery'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)
        return tx_hash


    def vc_register(self, did_address, signer, vc_hash, async_tx=True):
        tx_body = vc_hash
        tx_did = did_address
        tx_op = 'cdt:hello'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)
        return tx_hash


    def vc_revoke(self, did_address, signer, vc_hash, async_tx=True):
        tx_body = vc_hash
        tx_did = did_address
        tx_op = 'cdt:revoke'
        tx = self._build_tx(signer, tx_body, tx_did, tx_op)
        tx_hash = self._send_tx(tx, async_tx=async_tx)
        return tx_hash


    def vc_verify(self, vc):
        try:
            vc = json.loads(vc)
        except:
            raise Exception('Invalid credential data')

        data = vc['data']
        signature = vc['proof']['signature']
        signer_did = vc['proof']['verificationMethod'].split(':')[-1]
        did_keys = self.did_list_public_keys(signer_did)

        valid = False
        if not did_keys:
            raise Exception('Cannot find issuer DID information on blockchain')

        for key in did_keys:
            public_key = IDINVerifier(key['member'], key_format='hex')
            if public_key.verify(signature, data):
                valid = True
                break

        data = base64.b64decode(data)
        req = requests.get('{}/abci_query?data="{},{}"&path="CDT_INFO"'.format(self.host, did_address, data['id']))
        result = req.json()
        if 'result' not in result:
            raise Exception('Cannot find credential information on blockchain')
        
        revoked = json.loads(base64.b64decode(result['result']['response']['value']))['revoked']['status']

        if valid and not revoked:
            return True
        else:
            return False


        
