from . import Config, Logger, Utils
import requests

if Utils.amIdjango(__name__):
    from core.library import hackingtools as ht
else:
    import hackingtools as ht

config = Config.getConfig(parentKey='core', key='Repositories')

servers = ['127.0.0.1:5555']

def getServers():
    for serv in servers:
        r = requests.post('http://{ip}/'.format(ip=serv))
        if r.ok:
            print(r.json()['status'])

getServers()