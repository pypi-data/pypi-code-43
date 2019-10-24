#!/usr/bin/python3 
import sys
import os
sys.path.append(os.path.abspath(__file__ + "/../../"))
from analysis import  quicklook
def main():
    quicklook.main()


if __name__ == '__main__':
    main()
