import argparse


def parser():
    p = argparse.ArgumentParser(description='Tools for books.')
    p.add_argument('--completed', '-c', action='store', type=str)
    p.add_argument('--overall', '-o', action='store', type=str)
    p.add_argument('--pages', '-p', action='store', type=int)
    return p
