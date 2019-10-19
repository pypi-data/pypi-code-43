from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pipemaker.master.config import config, creds
import multiprocess as mp

def start():
    p = mp.Process(target=ftp_process)
    p.start()

def ftp_process():
    """ ftp server background process """
    c = config
    authorizer = DummyAuthorizer()
    authorizer.add_user(creds.username, creds.password,
                        c.pathvars.datapath,
                        perm="elradfmw")
    handler = FTPHandler
    handler.authorizer = authorizer
    server = FTPServer((c.ftp_address, c.ftp_port), handler)
    server.serve_forever()