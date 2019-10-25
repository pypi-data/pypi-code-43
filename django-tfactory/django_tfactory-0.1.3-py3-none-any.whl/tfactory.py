import sys,os
import argparse
from bs4 import BeautifulSoup
from termcolor import colored, cprint

def main():
    parser = argparse.ArgumentParser(prog='tfactory',description='Django template factory package.')

    parser.add_argument('-all', action='store_const', const=True, dest='all', default=False,
                        help="outlets all files.")

    parser.add_argument('-p', action="store", dest="path",  default=False ,
                        help="path of your template file.")

    args = parser.parse_args()

    if args.path:
        path = args.path
        build(path)

    cprint("done...".format(path), 'green')



def build(path):
    #c_path = os.path.split(os.path.abspath(os.path.realpath(sys.argv[0])))[0] + '/' + path
    html_doc = open(path)
    soup = BeautifulSoup(html_doc, 'html.parser')
    tags = [
        {'name': 'link', 'attr': 'href'},
        {'name': 'script', 'attr': 'src'},
        {'name': 'img', 'attr': 'src'},
    ]
    count = 0
    for tag in tags:
        for line in soup.find_all(tag['name']):
            if line.has_attr(tag['attr']):
               if not line[tag['attr']].startswith('https://'):
                  if not line[tag['attr']].startswith('http://'):
                      line[tag['attr']] = "{{% static '{}' %}}".format(line[tag['attr']])
                      cprint("Replaced- {}".format(line[tag['attr']]), 'yellow')
                      count = count + 1


    data = "{{% load static %}}\n{}".format(soup.prettify())

    file = open("tfactory_{}".format(path), "w+")
    file.write(data)
    file.close()

    cprint("Exported tfactory_{}...".format(path), 'green')



