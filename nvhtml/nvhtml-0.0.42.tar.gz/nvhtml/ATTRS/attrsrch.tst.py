from efdir import fs
from nvhtml.ATTRS import txts
from nvhtml.ATTRS import attrs
from nvhtml.ATTRS import eles
from lxml.etree import HTML as LXHTML


html_str = fs.rfile("./about.html")
root = LXHTML(html_str)
txts.cls(root)
attrs.src(root)
