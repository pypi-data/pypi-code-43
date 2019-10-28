from threading import Thread
import socket
import webbrowser

import click

from tshistory.util import find_dburi
from tshistory_editor.app import kickoff


@click.command()
@click.argument('db-uri')
def edit(db_uri):
    """edit time series through the web"""
    db_uri = find_dburi(db_uri)
    ipaddr = socket.gethostbyname(socket.gethostname())
    port = 5678
    server = Thread(name='tsedit.webapp', target=kickoff,
                    kwargs={'host': ipaddr, 'port': port, 'dburi': db_uri})
    server.daemon = True
    server.start()

    webbrowser.open('http://{ipaddr}:{port}/tseditor'.format(ipaddr=ipaddr, port=port))
    input()
