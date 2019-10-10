from shutil import which, make_archive
def check_shcommand_exist(command_name):
    return which(command_name) is not None

import coloredlogs, logging
def create_logger():
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG')
    coloredlogs.install(level='DEBUG', logger=logger)
    coloredlogs.install(fmt='%(levelname)s %(message)s')
    return logger

import shlex, subprocess, shutil, os
def run_command(command_line):
    args = shlex.split(command_line)
    subprocess.Popen(args).wait()


def archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s' % (name, format), destination)


import http.server
import socketserver
import os
import threading

httpd = None
def serve_in_background():
    global httpd
    if httpd:
        print("serve at port", port)
        httpd.serve_forever()


def http_server(root_path, port):
    os.chdir(root_path)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    httpd.serve_forever()
    print("serving at port", port)


import socket
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


import qrcode
def make_qrcode(text):
    img = qrcode.make(text)
    img.show()