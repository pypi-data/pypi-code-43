
from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj
from nvhtml import txt
from nvhtml import lvsrch
from nvhtml import fs
from nvhtml import engine
from nvhtml import utils
import lxml.sax
import argparse
from efdir import fs
import elist.elist as elel
import estring.estring as eses
import spaint.spaint as spaint



parser = argparse.ArgumentParser()
parser.add_argument('-input','--input_html_file', default="",help="input html file name")
parser.add_argument('-codec','--input_codec', default="utf-8",help="input html file codec")
parser.add_argument('-mode','--mode', default="list",help="generate width first search list json")


args = parser.parse_args()


def main():
    html_str = fs.rfile(args.input_html_file)
    root = LXHTML(html_str)
    wfs = engine.WFS(root)
    mat = wfs.mat
    if(args.mode == "mat"):
        fs.wjson(args.input_html_file+".list.json",mat)
    else:
        wfsl = elel.mat2wfs(wfs.mat)
        fs.wjson(args.input_html_file+".list.json",wfsl)

