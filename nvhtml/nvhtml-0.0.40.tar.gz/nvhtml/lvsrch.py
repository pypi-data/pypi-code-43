import elist.elist as elel
from nvhtml import engine
from nvhtml import utils


def arguments(**kwargs):
    '''
    '''
    if("source" in kwargs):
        source = kwargs['source']
    else:
        source = True
    if("which" in kwargs):
        which = kwargs['which']
    else:
        which = None
    if("show" in kwargs):
        show = kwargs['show']
    else:
        show = True
    return((source,which,show))


def srch(tag,root,*args,**kwargs):
    '''
    '''
    source,which,show = arguments(**kwargs)
    args=list(args)
    lngth = args.__len__()
    if(lngth == 0):
        eles = engine.xpath_levels(root,"//"+tag)
    elif(lngth == 1):
        eles = engine.xpath_levels(root,"//"+tag,args[0],args[0]+1)
    else:
        eles = engine.xpath_levels(root,"//"+tag,args[0],args[1])
    if(source):
        eles = elel.mapv(eles,engine.beautify,[])
    else:
        pass
    if(which==None):
        if(show):
            utils.parr(eles)
        else:
            pass
        return(eles)
    else:
        if(show):
            print(eles[which])
        else:
            pass
        return(eles[which])

def a(root,*args,**kwargs):
    '''
        | Search tag a of a lxml.etree._Element root
        
        :param  lxml.etree._Element root: 
            lxml-etree-element
        :param  bool source: 
            default True,return the source-text(outter-html-text) or not
        :param  int start": 
            default 0, start-level-depth(depth = pathlist-lngth - 1)
        :param  int end: 
            default to-the-last,start-level-depth(depth = pathlist-lngth - 1)
        :param  bool show: 
            default True,display the result or not
        :param  int which: 
            default None, return only one lxml.etree._Element, the index of the founded list-of-lxml.etree._Elements
        :return obj:
            lxml.etree._Element or list-of-lxml.etree._Elements or outer-html-txt of lxml.etree._Elemens
        
        ::
        
            html_str = fs.rfile("./test.html")
            root = LXHTML(html_str)
            eles = lvsrch.a(root,7,8,show=False)
            #only level-depth = 7 (root level-depth is 0 )
            print(eles[0])
            >>>
            <a href="/tags/index.asp" title="HTML 4.01 / XHTML 1.0 参考手册">
                标签列表（字母排序）
            </a>
            print(eles[5])
            >>>
            <a href="/tags/html_ref_canvas.asp" title="HTML Canvas 参考手册">
                HTML 画布
            </a>
            >>>
            eles = lvsrch.a(root,7,8,which=0)
            >>>
            <a href="/tags/index.asp" title="HTML 4.01 / XHTML 1.0 参考手册">
                标签列表（字母排序）
            </a>
            >>>
            eles = lvsrch.a(root,7,8,which=0,source=False)
            >>>
            <Element a at 0x155fef19848>
            >>>
    '''
    return(srch("a",root,*args,**kwargs))

def abbr(root,*args,**kwargs):
    return(srch("abbr",root,*args,**kwargs))

def acronym(root,*args,**kwargs):
    return(srch("acronym",root,*args,**kwargs))

def address(root,*args,**kwargs):
    return(srch("address",root,*args,**kwargs))

def applet(root,*args,**kwargs):
    return(srch("applet",root,*args,**kwargs))

def area(root,*args,**kwargs):
    return(srch("area",root,*args,**kwargs))

def article(root,*args,**kwargs):
    return(srch("article",root,*args,**kwargs))

def aside(root,*args,**kwargs):
    return(srch("aside",root,*args,**kwargs))

def audio(root,*args,**kwargs):
    return(srch("audio",root,*args,**kwargs))

def b(root,*args,**kwargs):
    return(srch("b",root,*args,**kwargs))

def base(root,*args,**kwargs):
    return(srch("base",root,*args,**kwargs))

def basefont(root,*args,**kwargs):
    return(srch("basefont",root,*args,**kwargs))

def bdi(root,*args,**kwargs):
    return(srch("bdi",root,*args,**kwargs))

def bdo(root,*args,**kwargs):
    return(srch("bdo",root,*args,**kwargs))

def big(root,*args,**kwargs):
    return(srch("big",root,*args,**kwargs))

def blockquote(root,*args,**kwargs):
    return(srch("blockquote",root,*args,**kwargs))

def body(root,*args,**kwargs):
    return(srch("body",root,*args,**kwargs))

def br(root,*args,**kwargs):
    return(srch("br",root,*args,**kwargs))

def button(root,*args,**kwargs):
    return(srch("button",root,*args,**kwargs))

def canvas(root,*args,**kwargs):
    return(srch("canvas",root,*args,**kwargs))

def caption(root,*args,**kwargs):
    return(srch("caption",root,*args,**kwargs))

def center(root,*args,**kwargs):
    return(srch("center",root,*args,**kwargs))

def cite(root,*args,**kwargs):
    return(srch("cite",root,*args,**kwargs))

def code(root,*args,**kwargs):
    return(srch("code",root,*args,**kwargs))

def col(root,*args,**kwargs):
    return(srch("col",root,*args,**kwargs))

def colgroup(root,*args,**kwargs):
    return(srch("colgroup",root,*args,**kwargs))

def command(root,*args,**kwargs):
    return(srch("command",root,*args,**kwargs))

def datalist(root,*args,**kwargs):
    return(srch("datalist",root,*args,**kwargs))

def dd(root,*args,**kwargs):
    return(srch("dd",root,*args,**kwargs))

def del_(root,*args,**kwargs):
    return(srch("del",root,*args,**kwargs))

def details(root,*args,**kwargs):
    return(srch("details",root,*args,**kwargs))

def dir(root,*args,**kwargs):
    return(srch("dir",root,*args,**kwargs))

def div(root,*args,**kwargs):
    return(srch("div",root,*args,**kwargs))

def dfn(root,*args,**kwargs):
    return(srch("dfn",root,*args,**kwargs))

def dialog(root,*args,**kwargs):
    return(srch("dialog",root,*args,**kwargs))

def dl(root,*args,**kwargs):
    return(srch("dl",root,*args,**kwargs))

def dt(root,*args,**kwargs):
    return(srch("dt",root,*args,**kwargs))

def em(root,*args,**kwargs):
    return(srch("em",root,*args,**kwargs))

def embed(root,*args,**kwargs):
    return(srch("embed",root,*args,**kwargs))

def fieldset(root,*args,**kwargs):
    return(srch("fieldset",root,*args,**kwargs))

def figcaption(root,*args,**kwargs):
    return(srch("figcaption",root,*args,**kwargs))

def figure(root,*args,**kwargs):
    return(srch("figure",root,*args,**kwargs))

def font(root,*args,**kwargs):
    return(srch("font",root,*args,**kwargs))

def footer(root,*args,**kwargs):
    return(srch("footer",root,*args,**kwargs))

def form(root,*args,**kwargs):
    return(srch("form",root,*args,**kwargs))

def frame(root,*args,**kwargs):
    return(srch("frame",root,*args,**kwargs))

def frameset(root,*args,**kwargs):
    return(srch("frameset",root,*args,**kwargs))

def h1(root,*args,**kwargs):
    return(srch("h1",root,*args,**kwargs))

def h2(root,*args,**kwargs):
    return(srch("h2",root,*args,**kwargs))

def h3(root,*args,**kwargs):
    return(srch("h3",root,*args,**kwargs))

def h4(root,*args,**kwargs):
    return(srch("h4",root,*args,**kwargs))

def h5(root,*args,**kwargs):
    return(srch("h5",root,*args,**kwargs))

def h6(root,*args,**kwargs):
    return(srch("h6",root,*args,**kwargs))

def head(root,*args,**kwargs):
    return(srch("head",root,*args,**kwargs))

def header(root,*args,**kwargs):
    return(srch("header",root,*args,**kwargs))

def hr(root,*args,**kwargs):
    return(srch("hr",root,*args,**kwargs))

def html(root,*args,**kwargs):
    return(srch("html",root,*args,**kwargs))

def i(root,*args,**kwargs):
    return(srch("i",root,*args,**kwargs))

def iframe(root,*args,**kwargs):
    return(srch("iframe",root,*args,**kwargs))

def img(root,*args,**kwargs):
    return(srch("img",root,*args,**kwargs))

def input(root,*args,**kwargs):
    return(srch("input",root,*args,**kwargs))

def ins(root,*args,**kwargs):
    return(srch("ins",root,*args,**kwargs))

def isindex(root,*args,**kwargs):
    return(srch("isindex",root,*args,**kwargs))

def kbd(root,*args,**kwargs):
    return(srch("kbd",root,*args,**kwargs))

def keygen(root,*args,**kwargs):
    return(srch("keygen",root,*args,**kwargs))

def label(root,*args,**kwargs):
    return(srch("label",root,*args,**kwargs))

def legend(root,*args,**kwargs):
    return(srch("legend",root,*args,**kwargs))

def li(root,*args,**kwargs):
    return(srch("li",root,*args,**kwargs))

def link(root,*args,**kwargs):
    return(srch("link",root,*args,**kwargs))

def map(root,*args,**kwargs):
    return(srch("map",root,*args,**kwargs))

def mark(root,*args,**kwargs):
    return(srch("mark",root,*args,**kwargs))

def menu(root,*args,**kwargs):
    return(srch("menu",root,*args,**kwargs))

def menuitem(root,*args,**kwargs):
    return(srch("menuitem",root,*args,**kwargs))

def meta(root,*args,**kwargs):
    return(srch("meta",root,*args,**kwargs))

def meter(root,*args,**kwargs):
    return(srch("meter",root,*args,**kwargs))

def nav(root,*args,**kwargs):
    return(srch("nav",root,*args,**kwargs))

def noframes(root,*args,**kwargs):
    return(srch("noframes",root,*args,**kwargs))

def noscript(root,*args,**kwargs):
    return(srch("noscript",root,*args,**kwargs))

def object(root,*args,**kwargs):
    return(srch("object",root,*args,**kwargs))

def ol(root,*args,**kwargs):
    return(srch("ol",root,*args,**kwargs))

def optgroup(root,*args,**kwargs):
    return(srch("optgroup",root,*args,**kwargs))

def option(root,*args,**kwargs):
    return(srch("option",root,*args,**kwargs))

def output(root,*args,**kwargs):
    return(srch("output",root,*args,**kwargs))

def p(root,*args,**kwargs):
    return(srch("p",root,*args,**kwargs))

def param(root,*args,**kwargs):
    return(srch("param",root,*args,**kwargs))

def pre(root,*args,**kwargs):
    return(srch("pre",root,*args,**kwargs))

def progress(root,*args,**kwargs):
    return(srch("progress",root,*args,**kwargs))

def q(root,*args,**kwargs):
    return(srch("q",root,*args,**kwargs))

def rp(root,*args,**kwargs):
    return(srch("rp",root,*args,**kwargs))

def rt(root,*args,**kwargs):
    return(srch("rt",root,*args,**kwargs))

def ruby(root,*args,**kwargs):
    return(srch("ruby",root,*args,**kwargs))

def s(root,*args,**kwargs):
    return(srch("s",root,*args,**kwargs))

def samp(root,*args,**kwargs):
    return(srch("samp",root,*args,**kwargs))

def script(root,*args,**kwargs):
    return(srch("script",root,*args,**kwargs))

def section(root,*args,**kwargs):
    return(srch("section",root,*args,**kwargs))

def select(root,*args,**kwargs):
    return(srch("select",root,*args,**kwargs))

def small(root,*args,**kwargs):
    return(srch("small",root,*args,**kwargs))

def source(root,*args,**kwargs):
    return(srch("source",root,*args,**kwargs))

def span(root,*args,**kwargs):
    return(srch("span",root,*args,**kwargs))

def strike(root,*args,**kwargs):
    return(srch("strike",root,*args,**kwargs))

def strong(root,*args,**kwargs):
    return(srch("strong",root,*args,**kwargs))

def style(root,*args,**kwargs):
    return(srch("style",root,*args,**kwargs))

def sub(root,*args,**kwargs):
    return(srch("sub",root,*args,**kwargs))

def summary(root,*args,**kwargs):
    return(srch("summary",root,*args,**kwargs))

def sup(root,*args,**kwargs):
    return(srch("sup",root,*args,**kwargs))

def table(root,*args,**kwargs):
    return(srch("table",root,*args,**kwargs))

def tbody(root,*args,**kwargs):
    return(srch("tbody",root,*args,**kwargs))

def td(root,*args,**kwargs):
    return(srch("td",root,*args,**kwargs))

def textarea(root,*args,**kwargs):
    return(srch("textarea",root,*args,**kwargs))

def tfoot(root,*args,**kwargs):
    return(srch("tfoot",root,*args,**kwargs))

def th(root,*args,**kwargs):
    return(srch("th",root,*args,**kwargs))

def thead(root,*args,**kwargs):
    return(srch("thead",root,*args,**kwargs))

def time(root,*args,**kwargs):
    return(srch("time",root,*args,**kwargs))

def title(root,*args,**kwargs):
    return(srch("title",root,*args,**kwargs))

def tr(root,*args,**kwargs):
    return(srch("tr",root,*args,**kwargs))

def track(root,*args,**kwargs):
    return(srch("track",root,*args,**kwargs))

def tt(root,*args,**kwargs):
    return(srch("tt",root,*args,**kwargs))

def u(root,*args,**kwargs):
    return(srch("u",root,*args,**kwargs))

def ul(root,*args,**kwargs):
    return(srch("ul",root,*args,**kwargs))

def var(root,*args,**kwargs):
    return(srch("var",root,*args,**kwargs))

def video(root,*args,**kwargs):
    return(srch("video",root,*args,**kwargs))

def wbr(root,*args,**kwargs):
    return(srch("wbr",root,*args,**kwargs))

def xmp(root,*args,**kwargs):
    return(srch("xmp",root,*args,**kwargs))

