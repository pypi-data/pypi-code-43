import os
from nvhtml import rshtml
from lxml.etree import HTML as LXHTML
from lxml.etree import XML as LXML
from xdict.jprint import pdir,pobj
from nvhtml.struct_show import *




parser = argparse.ArgumentParser()
parser.add_argument('-input','--input_rshtml_file', default="",help="input rshtml file name")
parser.add_argument('-codec','--input_codec', default="utf-8",help="input html file codec")
parser.add_argument('-color','--enable_color', default="True",help="color tag")

args = parser.parse_args()


def main():
    rsh = fs.rfile(args.input_rshtml_file)
    html_str  = rshtml.rsh2html(rsh)
    root = LXHTML(html_str)
    wfs = engine.WFS(root)
    mat = wfs.mat
    mat = scan_s0(mat)
    disp_mat = creat_display_mat(mat)
    mat = elel.mat_mapv(mat,modi_width_s0)
    mat = scan_s1(mat)
    mat =  scan_s2(mat)
    mat =  scan_s3(mat)
    if((args.enable_color.lower() == "false") | (args.enable_color.lower() == "no")):
        color = False
    else:
        color = True
    #
    print("color: ",color)
    #
    disp_mat = scan_disp_mat_s0(disp_mat,mat,color_enable=color)
    show_tag_tb(disp_mat)
