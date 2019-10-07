
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
parser.add_argument('-loc','--mat_loc', default="0,0",help="depth,breadth")


args = parser.parse_args()


def main():
    html_str = fs.rfile(args.input_html_file)
    root = LXHTML(html_str)
    wfs = engine.WFS(root)
    mat = wfs.mat
    loc = args.mat_loc.strip().replace(" ","").split(",")
    breadth = int(loc[1])
    depth = int(loc[0])
    d = mat[depth][breadth]
    pl = d["pl"]
    tail = pl[-1]
    samepl_breadth = d['samepl_breadth']
    if(tail[0]=="<"):
        html_txt = d.text
    else:
        pth = elel.join(pl,"/")
        eles = engine.xpath(root,"/"+pth)
        ele = eles[samepl_breadth]
        html_txt = engine.beautify(ele)
    print("<------json-----")
    pobj(d)
    print("------json---->\n")
    print("<----------html--------------")
    print(html_txt)
    print("<----------html--------------\n")

