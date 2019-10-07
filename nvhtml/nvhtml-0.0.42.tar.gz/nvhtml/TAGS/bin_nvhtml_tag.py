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

parser = argparse.ArgumentParser()
parser.add_argument('-input','--input_html_file', default="",help="input html file name")
#parser.add_argument('-output','--output_html_file', default="",help="output html file name")
parser.add_argument('-codec','--input_codec', default="utf-8",help="input html file codec")

parser.add_argument('-tag','--html_tag', default="img",help="html tag for search")

parser.add_argument('-which','--which_tag', default=None,help="sequence of tag-array")

parser.add_argument('-sdepth','--start_level_depth', default=None,help="start level depth")

parser.add_argument('-edepth','--end_level_depth', default=None,help="end level depth")


args = parser.parse_args()

levels = []
if(args.start_level_depth != None):
   levels.append(int(args.start_level_depth))
   if(args.end_level_depth != None):
       levels.append(int(args.end_level_depth))
   else:
       pass
else:
    pass




def main():
    html_str = fs.rfile(args.input_html_file,codec=args.input_codec)
    root = LXHTML(html_str)
    entries = lvsrch.srch(args.html_tag,root,*levels,which=args.which_tag)

#css selector
##apt install html-xml-utils
##cat opis.html.out.html | hxselect img
##go get github.com/ericchiang/pup

#xpath
##apt-get install xml-twig-tools



