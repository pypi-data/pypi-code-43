import argparse


def main():
    parser = argparse.ArgumentParser(prog='tfactory',description='Django template factory package.')

    parser.add_argument('-all', action='store_const', const=True, dest='all', default=False,
                        help="outlets all files.")

    parser.add_argument('-p', action="store", dest="path",  default=False ,
                        help="path of your template file.")

    args = parser.parse_args()

    if args.path:
        print('your path'+args.path)


    print('tfactory closed...')