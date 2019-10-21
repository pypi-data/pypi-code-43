import os


def make_directory_if_doesnt_exist(path):
    os.makedirs(path, exist_ok=True)
