import os
import sys
import argparse
from argparse import RawTextHelpFormatter

if __name__ == '__main__':

  parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
  parser.add_argument('-p', '--path', nargs='?')
  args = parser.parse_args()

  if not args.path:
      parser.print_help()
      sys.exit(0)

  path = int(args.path)

  print(path)
  print('exiting.....')
