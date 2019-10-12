import time
import subprocess
import sys
import shutil
import os
import glob

 
sys.path.append('D:\\work\\code\\stable_coin_python_sdk\\hdao')

from hx_wallet_api import HXWalletApi


HX_NODE_BIN = '.\\hx_node.exe --testnet --rpc-endpoint=127.0.0.1:18090'
HX_CLIENT_BIN = '.\\hx_client.exe --testnet --server-rpc-endpoint=ws://127.0.0.1:18090 --rpc-endpoint=127.0.0.1:18091'
HX_TESTNET_DATA = 'testnet'


def files(curr_dir = '.', ext = '*.exe'):
    for i in glob.glob(os.path.join(curr_dir, ext)):
        yield i
  
def remove_files(rootdir, ext):
    for i in files(rootdir, ext):
        os.unlink(i)


class HXTestnet():
    def start_testnet(self):
        if os.path.exists(HX_TESTNET_DATA):
            shutil.rmtree(HX_TESTNET_DATA)
        if os.path.exists("wallet_testnet.json"):
            os.unlink("wallet_testnet.json")
        remove_files(rootdir=".", ext="*.wallet")
        os.mkdir(HX_TESTNET_DATA)
        node_cmd = HX_NODE_BIN + " -d " + HX_TESTNET_DATA
        print(node_cmd)
        client_cmd = HX_CLIENT_BIN
        self.node = subprocess.Popen(node_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3)
        self.clilent = subprocess.Popen(client_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    def register_contract():
        pass


    def stop_testnet(self):
        self.node.terminate()
        self.clilent.terminate()
        time.sleep(3)
        shutil.rmtree(HX_TESTNET_DATA)


if __name__ == "__main__":
    testnet = HXTestnet()
    print("start node & client ...")
    testnet.start_testnet()
    api = HXWalletApi(name='testnet', rpc_url='http://127.0.0.1:18091/')
    # info = api.rpc_request('info', [])
    info = api.rpc_request('set_password', ["12345678"])
    info = api.rpc_request('unlock', ["12345678"])
    info = api.rpc_request('import_key', ["nathan", "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"])
    info = api.rpc_request('import_key', ["miner0", "5JZDdTiLcahFtZo7M95ybDjT5VufrsYWfxiaQfJoP1zfbw8PmRA"])
    info = api.rpc_request('import_key', ["miner1", "5K8mFWgAf2bd5AG8hKzjc9BgXKrnwqNT7PaUbJ7oWjHjQPwz8zF"])
    info = api.rpc_request('import_key', ["miner2", "5K4RZCLQ6kUFps1eUncFkAJ7iUEsRXm694aD2W6tMxhFqzmWdD3"])
    info = api.rpc_request('import_key', ["miner3", "5JiDkVAXi6vpE6aEiDRh7WAwcGwr1ivrsN8Yh7eDwFbmz5BFCTz"])
    info = api.rpc_request('import_key', ["miner4", "5J5uekBwLhENsKGNShqBDoJdbHDaZMMrStVimGTfJ9V2vbAKpo9"])
    # info = api.rpc_request('import_key', ["miner5", "5KCmKbz9mD8ndbA5UBLC6kUVENCDkmHf9dpZ7ExKnB8LFWWyTmw"])
    # info = api.rpc_request('import_key', ["miner6", "5JLvURaky1ryswgY785sQ4TiR3MrEon9ryKX71NatdJJ3AvtC2b"])
    # info = api.rpc_request('import_key', ["miner7", "5HvjWASwH2mYNodoMDdibW8tHW3u8HFQYS7vD3BtpeenCny1h2Q"])
    # info = api.rpc_request('import_key', ["miner8", "5JDkmfS8YMWapcSCntX7wygJZPtELATJHMpPCvidTA19SF8Xo5u"])
    # info = api.rpc_request('import_key', ["miner9", "5HzByVyqvtXWXb9HM3TFS8mvrCf3NaDM1GRZQHuaiDgJG739a83"])
    # info = api.rpc_request('import_key', ["miner10", "5KdAjgrJ7gwnbwQVK8vMXQJ5BW5PfMr5BtA5DpsQwCtCVGNqM8V"])
    # info = api.rpc_request('import_key', ["miner11", "5KbUi2Efd2bscQKtQ3a4RBvn4bVuaMfpCZwHpskWrUokRc3NXA1"])
    # info = api.rpc_request('import_key', ["miner12", "5K67sdMmoynLXK3Y3EiZ3Gfjw9Qn5UY9dQrGKed5V5DiZHzun7G"])
    # info = api.rpc_request('import_key', ["miner13", "5JCBhwpxBSo7ABJweuNamtGoWbnbVJvGf4KAyKCgFFWTKGWD1vD"])
    # info = api.rpc_request('import_key', ["miner14", "5JyKyz1JJZTzN1a4ruvbykLia1WMM46TEJShhgLzWfsGQJVcHSK"])
    # info = api.rpc_request('import_key', ["miner15", "5Hy5KPpkAoU2r9uaiqw4SECwNYyZMaR78BkuhbeLpw6tVBB66gn"])
    # info = api.rpc_request('import_key', ["miner16", "5JP1tX4BRrgZctxTmkAbam9m53DardLM6TrQtDS1EdgohGp6mtJ"])
    # info = api.rpc_request('import_key', ["miner17", "5KkHjoSC1u5GhBdaNbGmTptwEg22AqtEk4ECQ8XQXfMFqXhDnHk"])
    # info = api.rpc_request('import_key', ["miner18", "5KjdpdNzwcx9A5XZGNquHWzqVcPvMPF9EXsDkY2STsvDQeNroZn"])
    # info = api.rpc_request('import_key', ["miner19", "5KfshkiRmYvAvbf5rg8HXWZSifrTtR7htQyox7aVrCsw5t4Xgbk"])
    # info = api.rpc_request('import_key', ["miner20", "5JZ46AjQN7kCz7igUcQ3wGUFAviBDvBkxZ7xS6Pf5DHPQvFspwr"])
    # info = api.rpc_request('import_key', ["miner21", "5JHa4RNxzehYdCMtVoqh55a5vNzAmENXtoGwXFxmNwtvTrduGHy"])
    # info = api.rpc_request('import_key', ["miner22", "5J1HrKVzNQBwKXiTdMYaY6eVknm15mCeyV84Wt3TDMwwCLHxyWv"])
    # info = api.rpc_request('import_key', ["miner23", "5JtrnVGscfoYC8Hftk36hwXYUZjKBzL6fv8JBTeo6MbKgSL2vF1"])
    # info = api.rpc_request('import_key', ["miner24", "5J3oHnGEze3gwidWjoznyTGgyJqFm3h8cFWg2DZaP55Rd1tUXVr"])
    # info = api.rpc_request('import_key', ["guard0", "5JZe9Hv7twngWSEZzvvvDXP5RG1LJGixSz6WJ4D8te9x45kvDuG"])
    # info = api.rpc_request('import_key', ["guard1", "5JQT9vqrFW26817PELM7D3w6rqbZ5GDW43knB2bP5kBALQ2BRDi"])
    # info = api.rpc_request('import_key', ["guard2", "5Je6RMyd39B3W7QsC6XPHXFaTP31QmrtfiBxnmXDbeFz1pHE8CB"])
    # info = api.rpc_request('import_key', ["guard3", "5JhS8VntvNPKPU1ByiUMhUeu7HutUK9PfCyAUXGvqLB1dym7Hgt"])
    # info = api.rpc_request('import_key', ["guard4", "5JmaB7uQVGN6nKH1YyU4hSF6TmfCGJKoywimbJsRVkykF9swp1D"])
    # info = api.rpc_request('import_key', ["guard5", "5JPYHwjeHETE6xzMUo2TunSCpdfdAUjLBBUH2Jy2DuGQcdS2ism"])
    # info = api.rpc_request('import_key', ["guard6", "5KLAzVUNPPci2JhQUQRpy1zsbjvyHQaRTATfLYk6jMnjrKZhx8U"])
    # info = api.rpc_request('start_mining', ["miner0","miner1","miner2","miner3","miner4","miner5","miner6","miner7","miner8","miner9","miner10","miner11","miner12","miner13","miner14","miner15","miner16","miner17","miner18","miner19", "miner20","miner21","miner22","miner23", "miner24"])
    # info = api.rpc_request('start_mining', ["miner0","miner1","miner2","miner3"])
    # api.rpc_request('wallet_create_asset', ["guard0", "BTC", 8, 1000000000, 0, 'true'])
    # print(info)
    # info = api.rpc_request('import_key', ["miner0", "5JZDdTiLcahFtZo7M95ybDjT5VufrsYWfxiaQfJoP1zfbw8PmRA"])
    # print(info)
    time.sleep(20)
    print("stop node & client ...")
    testnet.stop_testnet()