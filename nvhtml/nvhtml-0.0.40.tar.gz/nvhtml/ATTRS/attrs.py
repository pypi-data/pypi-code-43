from nvhtml.ATTRS.attrsrch import *

def href(root,*args,**kwargs):
    hrefs = srcha4attribs(root,"href",*args,**kwargs)
    return(hrefs)

def src(root,*args,**kwargs):
    srcs = srcha4attribs(root,"src",*args,**kwargs)
    return(srcs)



