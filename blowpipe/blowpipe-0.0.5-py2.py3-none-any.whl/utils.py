import sys
import concurrent.futures
from blowpipe.logger import Logger
from blowpipe import config
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler


class IniFile(object):
    def __init__(self, filename=None):
        self.data = {}
        if filename is not None:
            self.filename = filename
            basename = filename.split("/")[-1]
            self.filename = filename
            self.root_dir = self.filename[0:len(filename)-len(basename)]
            if os.path.isfile(filename):
                self.load()

    def load(self):
        f = open(self.filename, 'r')
        for line in f:
            line = line.strip()
            whitespace = False
            comment = False
            header = False
            key = False
            if line == "":
                whitespace = True
            elif line.find("#") == 0:
                comment = True
            elif line.startswith("[") and line.endswith("]"):
                header = True
            elif line.find("=") > -1:
                key = True

            if whitespace or comment:
                continue
            elif header:
                # a new header
                current_header = {}
                header_key = line.strip("[]")
                if self.data.get(header_key) is None:
                    # saves against multiple declarations of the header
                    self.data[header_key] = {}
            elif key:
                key_name, value = line.split("=", 1)
                self.data[header_key][key_name] = value
        f.close()

    def save(self):
        f = open(self.filename, 'w')
        for header_key in self.get_headers():
            line = "[" + header_key + "]"
            f.write(line)
            f.write("\n")
            for value_key in self.get_header_keys(header_key):
                line = value_key + "=" + self.get(header_key, value_key)
                f.write(line)
                f.write("\n")
            f.write("\n")
        f.close()

    def get(self, header, key, default_value=None):
        keys = self.data.get(header) or {}
        return keys.get(key) or default_value

    def set(self, header, key, value):
        keys = self.data.get(header) or {}
        self.data[header] = keys
        keys[key] = str(value)

    def get_headers(self):
        return self.data.keys()

    def get_header_keys(self, header):
        entry = self.data.get(header) or {}
        return entry.keys()

    def get_root_dir(self):
        return self.root_dir


class CLI:
    def __init__(self, argv=sys.argv):
        self.argv = argv

    def get_command(self):
        if len(self.argv) > 1:
            return self.argv[1]
        else:
            return None

    @staticmethod
    def read(prompt):
        return input(prompt)

    def index_of(self, key):
        index = 0
        while index < len(self.argv):
            if self.argv[index] == key:
                return index
            index += 1
        return -1

    def contains(self, key):
        return self.index_of(key) > -1

    def get_or_die(self, key, error_message=None):
        v = self.get_or_default(key, None)
        if v is None:
            if error_message is None:
                print("Error, '" + key + "' is required.")
            else:
                print(error_message)

            sys.exit(1)
        else:
            return v

    def get_or_default(self, key, default_value):
        index = self.index_of(key)
        if index == -1:
            return default_value
        else:
            if index + 1 < len(self.argv):
                return self.argv[index + 1]
            else:
                # means we have the key (e.g -f) but not hte value (e.g. -f filename)
                #  (missing filename)
                return default_value

    def get_existing_filename_or_die(self, key):
        """
        returns the filename specified by the key, or dies
        """
        filename = self.get_or_default(key, None)
        if filename is None:
            print("Error, '" + key + "' is required.")
            sys.exit(1)
        elif not os.path.isfile(filename):
            print("'" + str(filename) + "' is not a file.")
            sys.exit(1)
        else:
            return filename


class ThreadPool(object):
    def __init__(self):
        self.workers = []
        self.futures = []
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.logger = Logger("ThreadPool")

    def add(self, worker):
        pool = self.pool

        self.workers.append(worker)
        self.futures.append(pool.submit(worker.execute))

    def is_running(self):
        for f in self.futures:
            if f.running():
                return True
        return False

    def quit(self):
        self.logger.debug(".quit()")
        for worker in self.workers:
            worker.quit()

        self.pool.shutdown(wait=True)

        for worker in self.workers:
            worker.on_quit()

        self.logger.debug(".quit() complete.")


def resolve_file(candidate):
    return candidate.replace("~", os.getenv("HOME"))


def split_file(candidate):
    """
    returns the directory path and the filename with no path information
    :param candidate:
    :return:
    """
    abs_file = resolve_file(candidate)
    filename = abs_file.split("/")[-1]
    index = len(filename)+1
    dirname = abs_file[0:-index]
    return dirname, filename


def print_logo():
    import pyfiglet
    print(pyfiglet.figlet_format("blowpipe"))


class StdOutTrapper:
    def __init__(self):
        self.messages = []

    def clear(self):
        self.messages = []

    def write(self, msg):
        self.print(msg)

    def print(self, msg):
        self.messages.append(msg)
        self.messages.append("\n")

    def flush(self):
        pass

    def to_string(self):
        result = "".join(self.messages)
        self.clear()
        return result


class Webserver:

    def __init__(self, hostname="0.0.0.0", port=8000):
        self._hostname = hostname
        self._port = port
        self._is_running = False
        self._threadpool = None
        self._httpd = None
        self._quit = False

    def start(self):
        self._threadpool = ThreadPool()
        self._threadpool.add(self)

    def stop(self):
        self._threadpool.quit()

    def execute(self):
        try:
            import http.server
            import socketserver

            handler_fn = http.server.SimpleHTTPRequestHandler
            httpd = socketserver.TCPServer((self._hostname, self._port), handler_fn)
            self._httpd = httpd
            self._is_running = True
            while not self._quit:
                httpd.handle_request()
        except Exception as e:
            print(e)
        finally:
            self._is_running = False

    def on_quit(self):
        pass

    def quit(self):
        self._quit = True
        # because I block on a request, this allows me to shut it down
        import requests
        url = "http://localhost:" + str(self._port) + "/USER_GUIDE.md"
        result = requests.get(url)
        print(url)
        print(str(result))

    def is_running(self):
        return self._is_running


def simple_http_server(host='localhost', port=4001, path='.'):

    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.deamon = True

    cwd = os.getcwd()

    def start():
        os.chdir(path)
        thread.start()
        print('utils.simple_http_server() starting httpserver at "' + path + '" on port {}'.format(server.server_port))

    def stop():
        os.chdir(cwd)
        server.shutdown()
        server.socket.close()
        print('utils.simple_http_server() stopping http server on port {}'.format(server.server_port))

    return start, stop


def is_server_running(cfg: config.BlowpipeConfig) -> bool:
    if not is_port_available("0.0.0.0", cfg.get_grpc_port()):
        # looks like something is running on that port.
        # let's see if we can connect to it as the client; if we can
        # then we will be
        from blowpipe import client_cli
        client = client_cli.BlowpipeClient(cfg)
        result, _ = client.ping()
        if result:
            return True
        else:
            return False


def is_port_available(host: str, port: int) -> bool:
    import socket
    import sys

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        if result == 0:
            return False
        else:
            return True
    finally:
        if sock is not None:
            sock.close()


def autodiscover_server_config_file(cli_arg, env_var, filename):
    """
    finds the appropriate filename in the following order
    - cli -f argument
    - environment variable
    - current dir
    """
    cli = CLI(sys.argv)
    cfg_filename = cli.get_or_default(cli_arg, None)
    if cfg_filename is not None:
        return cfg_filename

    env_root_dir = os.getenv(env_var)
    if env_root_dir is not None and env_root_dir != "":
        env_file = resolve_file(env_root_dir + "/" + filename)
        return env_file

    # else go current dir
    filename = resolve_file(os.getcwd() + "/" + filename)
    return filename


class BlowpipeError(ValueError):
    def __init__(self, *args, **kwargs):  # real signature unknown
        pass
