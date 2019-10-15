#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
name = "whomst"
"""
~$ whomst .
~$ whomst <path>
~$ whomst . > requirements.txt && pip install -r requirements.txt
"""
def look(path):
    """
    param: path: relative or absolute path to top-level directory
    param: exclude: set of dirs to omit when found in path

    - create cursor
    - walk tree with generator loop
    - append to cursor in loop
    - clean all at once
    - omit standard library
    """
    exclude = set([
        "__pycache__",
        "lib",
        "env",
        "ENV",
        "venv",
        "VENV",
        "site-packages",
        "*.egg-info",
    ])
    cursor = set()
    for full_name in walk_files(path, exclude):
        imports = read_imports(full_name)
        cursor = cursor.union(imports)
    clean = clean_lines(cursor)
    ready = ignore_included(clean)
    return sorted(ready)


def between(s, start, end):
    return (s.split(start))[1].split(end)[0].strip()


def walk_files(path, exclude):
    for root, dirs, files in os.walk(path):
        if any(excl in root for excl in exclude):
            continue
        files[:] = [f for f in files if f.endswith(".py")]
        for file in files:
            yield os.path.join(root, file)


def read_imports(full_name):
    # IF LINE HAS `()` CAPTURE UNTIL IT CLOSES
    cursor = set()
    with open(full_name) as f:
        file_data = f.read()
        for line in file_data.splitlines():
            # if ("import" in line) and ("()" in line):
                # capture all till closed
            if "import" in line and line.startswith(("import", "from")):
                cursor.add(line)
    return cursor


def clean_lines(cursor):
    result = set()
    for line in cursor:
        if line.startswith("import"):
            ln = line.replace("import", "").split(",")
            ln = list(map(str.strip, ln))
            for l in ln:
                if " as " in l:
                    l = l.split(" as ")[0].strip()
                    result.add(l)
                elif "." in l:
                    result.add(l.split(".")[0])
                else:
                    result.add(l)
        elif line.startswith("from"):
            ln = between(line, "from", "import").split(".")[0].strip()
            result.add(ln)
    no_empties = filter(bool, result)
    return sorted(no_empties)


def ignore_included(result):
    answer = list()
    builtins = built_in_modules()
    for package in result:
        if package in builtins:
            pass
        else:
            answer.append(package)
    return sorted(answer)


def built_in_modules(return_type="set"):
    # collection included modules within Python 3.7
    built_in_modules = {"__future__":"","__main__":"","_dummy_thread":"","_thread":"","abc":"","aifc":"","argparse":"","array":"","ast":"","asynchat":"","asyncio":"","asyncore":"","atexit":"","audioop":"","base64":"","bdb":"","binascii":"","binhex":"","bisect":"","builtins":"","bz2":"","calendar":"","cgi":"","cgitb":"","chunk":"","cmath":"","cmd":"","code":"","codecs":"","codeop":"","collections":"","colorsys":"","compileall":"","concurrent":"","configparser":"","contextlib":"","contextvars":"","copy":"","copyreg":"","cProfile":"","crypt":"","csv":"","ctypes":"","curses":"","dataclasses":"","datetime":"","dbm":"","decimal":"","difflib":"","dis":"","distutils":"","doctest":"","dummy_threading":"","email":"","encodings":"","ensurepip":"","enum":"","errno":"","faulthandler":"","fcntl":"","filecmp":"","fileinput":"","fnmatch":"","formatter":"","fractions":"","ftplib":"","functools":"","gc":"","getopt":"","getpass":"","gettext":"","glob":"","grp":"","gzip":"","hashlib":"","heapq":"","hmac":"","html":"","http":"","imaplib":"","imghdr":"","imp":"","importlib":"","inspect":"","io":"","ipaddress":"","itertools":"","json":"","keyword":"","lib2to3":"","linecache":"","locale":"","logging":"","lzma":"","macpath":"","mailbox":"","mailcap":"","marshal":"","math":"","mimetypes":"","mmap":"","modulefinder":"","msilib":"","msvcrt":"","multiprocessing":"","netrc":"","nis":"","nntplib":"","numbers":"","operator":"","optparse":"","os":"","ossaudiodev":"","parser":"","pathlib":"","pdb":"","pickle":"","pickletools":"","pipes":"","pkgutil":"","platform":"","plistlib":"","poplib":"","posix":"","pprint":"","profile":"","pstats":"","pty":"","pwd":"","py_compile":"","pyclbr":"","pydoc":"","queue":"","quopri":"","random":"","re":"","readline":"","reprlib":"","resource":"","rlcompleter":"","runpy":"","sched":"","secrets":"","select":"","selectors":"","shelve":"","shlex":"","shutil":"","setuptools":"","signal":"","site":"","smtpd":"","smtplib":"","sndhdr":"","socket":"","socketserver":"","spwd":"","sqlite3":"","ssl":"","stat":"","statistics":"","string":"","stringprep":"","struct":"","subprocess":"","sunau":"","symbol":"","symtable":"","sys":"","sysconfig":"","syslog":"","tabnanny":"","tarfile":"","telnetlib":"","tempfile":"","termios":"","test":"","textwrap":"","threading":"","time":"","timeit":"","tkinter":"","token":"","tokenize":"","trace":"","traceback":"","tracemalloc":"","tty":"","turtle":"","turtledemo":"","types":"","typing":"","unicodedata":"","unittest":"","urllib":"","uu":"","uuid":"","venv":"","warnings":"","wave":"","weakref":"","webbrowser":"","winreg":"","winsound":"","wsgiref":"","xdrlib":"","xml":"","xmlrpc":"","zipapp":"","zipfile":"","zipimport":"","zlib":""}
    if return_type == "set":      return set(built_in_modules)
    elif return_type == "list":   return list(built_in_modules.keys())
    elif return_type == "dict":   return built_in_modules


def terminal(*args):
    for _, arg in enumerate(args):
        print("%s" % arg)


# ----------------------- -----------------------
def cli(arg):
    import argparse
    parser = argparse.ArgumentParser(description='Detect external package dependencies')
    parser.add_argument('path', help='path of top-level directory, use `.` for cwd')
    parsed = parser.parse_args(arg)
    path = parsed.path
    if os.path.exists(path) or os.path.isdir(path):
        return path
    raise FileNotFoundError("[No such path] %s" % path)


# ----------------------- -----------------------
def main(arg=None):
    import sys
    if not arg:
        arg = sys.argv[1:]
    path = cli(arg)
    pkgs = look(path)
    terminal(*pkgs)


# ----------------------- -----------------------
if __name__ == "__main__":
    main()
