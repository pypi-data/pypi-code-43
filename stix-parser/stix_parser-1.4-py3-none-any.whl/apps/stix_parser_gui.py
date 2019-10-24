#!/usr/bin/python3 
import sys
import os
sys.path.append(os.path.abspath(__file__ + "/../../"))

from ui import parser_gui

def main():
    parser_gui.main()


if __name__ == '__main__':
    main()
