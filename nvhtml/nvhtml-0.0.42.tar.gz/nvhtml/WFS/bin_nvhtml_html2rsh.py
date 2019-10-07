
from nvhtml import rshtml
import argparse
from efdir import fs
import os

parser = argparse.ArgumentParser()
parser.add_argument('-input','--input_html_file', default="",help="input html file name")
parser.add_argument('-codec','--input_codec', default="utf-8",help="input html file codec")
parser.add_argument('-wkdir','--work_dir', default=".",help="workdir")

args = parser.parse_args()



def main():
    html_str = fs.rfile(args.input_html_file)
    rsh = rshtml.html2rsh(html_str)
    wkdir = args.work_dir
    fn = os.path.join(wkdir,args.input_html_file+".rshtml")
    fs.wfile(fn,rsh) 
