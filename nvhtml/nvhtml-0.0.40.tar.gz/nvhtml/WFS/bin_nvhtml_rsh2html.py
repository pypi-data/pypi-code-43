
from nvhtml import rshtml
import argparse
from efdir import fs
import os

parser = argparse.ArgumentParser()
parser.add_argument('-input','--input_rshtml_file', default="",help="input rshtml file name")
parser.add_argument('-codec','--input_codec', default="utf-8",help="input html file codec")
parser.add_argument('-wkdir','--work_dir', default=".",help="workdir")

args = parser.parse_args()



def main():
    rsh = fs.rfile(args.input_rshtml_file)
    html_str  = rshtml.rsh2html(rsh)
    wkdir = args.work_dir
    fn = os.path.join(wkdir,args.input_rshtml_file+".html")
    fs.wfile(fn,html_str) 
