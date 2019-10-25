import argparse
from bs4 import BeautifulSoup

def main():
    parser = argparse.ArgumentParser(prog='tfactory',description='Django template factory package.')

    parser.add_argument('-all', action='store_const', const=True, dest='all', default=False,
                        help="outlets all files.")

    parser.add_argument('-p', action="store", dest="path",  default=False ,
                        help="path of your template file.")

    args = parser.parse_args()

    if args.path:
        html_doc = open(args.path)
        soup = BeautifulSoup(html_doc, 'html.parser')
        #prettify = soup.prettify().encode('utf-8')
        for line in soup.find_all('a'):
            link = line.get('href')
            print(link)





    print('tfactory closed...')