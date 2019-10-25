from pyats.easypy import run
import os

def main():

    run(os.path.join(os.path.dirname(__file__), 'script.py'))