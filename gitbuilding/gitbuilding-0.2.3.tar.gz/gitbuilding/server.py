
import os
import socket
import flask
from flask import request, jsonify
import codecs
import yaml
from markdown import markdown
import gitbuilding as gb
import datetime
import requests
import shutil
from warnings import warn
import re
from copy import deepcopy

class GBServer(flask.Flask):
    """
    GBServer is the Git Building server it uses Flask to render documentation
    """
    def __init__(self,conf,dev=False):

        self.homepath = '.server_output'
        shutil.rmtree(self.homepath)
        self.doc = gb.Documentation(conf,self.homepath)
        self.doc.buildall()
        self.dev = dev

        self.homepage = os.path.join(self.homepath,self.doc.overview)
        self.gbpath = os.path.dirname(gb.__file__)
        
        self.read_project_data()
        self.onePage = self.project_data['OnePage']

        super(GBServer, self).__init__(__name__)

        # allow hot-reloading of live-editor in development mode
        if dev:
            self.add_url_rule('/static/live-editor/<path:subpath>', 'dev_editor_static', self._dev_editor_static)
            self.add_url_rule('/static/<path:subpath>', 'dev_other_static', self._dev_other_static)
            self.add_url_rule('/sockjs-node/<path:subpath>', 'dev_editor_sockjs', self._dev_editor_sockjs)
            self.add_url_rule('/__webpack_dev_server__/<path:subpath>', 'dev_editor_webpack', self._dev_editor_webpack)

        # set page rendering
        self.add_url_rule('/', 'render', self._render_page)
        self.add_url_rule('/render_markdown', 'live_render', self._live_render,methods=['POST',])
        self.add_url_rule('/<path:subpath>', 'render', self._render_page)
        self.add_url_rule('/editor/', 'editor', self._edit_page)
        self.add_url_rule('/editor/save', 'save', self._save_edit, methods=['POST',])
        self.add_url_rule('/editor/raw', 'raw', self._raw_md)
        self.add_url_rule('/editor/<path:subpath>', 'editor_redirect', self._editor_redirect)
        self.add_url_rule('/<path:subpath>/editor/', 'editor', self._edit_page)
        self.add_url_rule('/<path:subpath>/editor/raw', 'raw', self._raw_md)
        self.add_url_rule('/<path:subpath>/editor/save', 'save', self._save_edit,methods=['POST',])
        self.add_url_rule('/<path:subpath>/editor/dropped-file', 'droppedfile', self._dropped_file,methods=['POST',])
        self.add_url_rule('/<path:otherpath>/editor/<path:subpath>', 'editor_redirect', self._editor_redirect)
        self.renderer = GBRenderer(self.project_data)
        self.live_renderer = GBRenderer(deepcopy(self.project_data))
    
    def read_project_data(self):
        with open(os.path.join(self.homepath,'_data','project.yaml'), 'r') as stream:
            self.project_data = yaml.load(stream, Loader=yaml.SafeLoader)
    
    def _get_docpage(self,subpath):
        if len(subpath) ==0:
            return None
        ind = self.doc.pages.index(subpath)
        return self.doc.pages[ind]

    def _raw_md(self,subpath=None):
        if subpath is None and request.path == '/editor/raw':
            if self.onePage:
                md = self.doc.pages[0].raw()
            else:
                md = self.doc.get_overview_text()
            return jsonify({'md': md})
        elif subpath in self.doc.pages:
            page = self._get_docpage(subpath)
            if page is None:
                md = ''
            else:
                md = page.raw()
            return jsonify({'md': md,'page': subpath})
        else:
            return flask.abort('405')

    def _save_edit(self,subpath=None):
        content = request.get_json()
        for uploadedFile in content['uploadedFiles']:
            if uploadedFile in content['md']:
                if not os.path.isfile(uploadedFile):
                    shutil.copyfile(os.path.join(self.homepath,uploadedFile),uploadedFile)
                else:
                    warn(f"{uploadedFile} already exists perhaps an issue when editing two files at once.")
        if content['md'] is not None:
            if subpath is None:
                if self.onePage:
                    saved = self.doc.pages[0].save(content['md'])
                else:
                    self.doc.overview_text = content['md']
                    saved = self.doc.save_overview_text()
            else:
                page = self._get_docpage(subpath)
                saved = page.save(content['md'])
            if saved:
                self.doc.buildall(force=True)
                self.read_project_data()
                self.renderer.project_data=self.project_data
                return jsonify({'saved': True})
            else:
                return jsonify({'saved': False})
    
    def _dropped_file(self,subpath=None):
        files = request.files
        #loop through all but return after first image.
        for file in files:
            if files[file].mimetype.startswith('image'):
                fname = os.path.join('images',files[file].filename)
                fpath = os.path.join(self.homepath,fname)
                n=0
                while os.path.isfile(fpath):
                    if n==0:
                        fname_orig = fname
                    n=n+1
                    fname_only, fextension = os.path.splitext(fname_orig)
                    fname = fname_only+'--%03d'%n+fextension
                    fpath = os.path.join(self.homepath,fname)
                files[file].save(fpath)
                return jsonify({'received': True, 'filename': fname})
                
        #if not returned yet nothing was an image
        return flask.abort(405)
            
    
    def _live_render(self):
        content = request.get_json()
        if content['md'] is None:
            return jsonify({'html': ''})
        else:
            if not 'page' in content:
                if not self.onePage:
                    processed_text,title,pages = self.doc.build_overview(content['md'])
                    for p in pages:
                        self.live_renderer.project_data['PageList'].append(p.summary())
                else:
                    page = self.doc.pages[0]
                    page.replace_raw(content['md'])
                    processed_text = page.build(tofile=False)
                    title = page.title
                self.live_renderer.project_data['Title'] = title
            else:
                page = self._get_docpage(content['page'])
                if page is None:
                    return jsonify({'html': ''})
                page.replace_raw(content['md'])
                processed_text = page.build(tofile=False)
            html = self.live_renderer.render_md(processed_text,fullpage=False,nav=False)
            return jsonify({'html': html})


    def _edit_page(self,subpath=None):
        if (subpath is None and request.path == "/editor/") or (subpath.endswith('.md') and subpath in self.doc.pages):
            self.live_renderer.project_data = deepcopy(self.project_data)
            if self.dev: # for hot-reloading
                url = "http://localhost:8080/static/live-editor/"
                try:
                    r = requests.get(url)
                except requests.exceptions.RequestException as e:
                    msg = "ERROR: Could not connect to live-editor dev server on '{}', did you forget to start it?".format(
                        url
                    )
                    return flask.abort(flask.Response(msg, status=500))
                return r.text
            else:
                page = os.path.join(self.gbpath,'static','live-editor','index.html')
                return flask.send_file(page)
        else:
            html=self.renderer.render("<h1>Sorry. Cannot edit this file!</h1>")
        return html

    def _editor_redirect(self, subpath=None,otherpath=None):
        return flask.redirect(f'/{subpath}')

    def _render_page(self, subpath=None):
        # define special page for missing
        if subpath == 'missing':
            return self.renderer.missing_page()
        if subpath is None:
            page=self.homepage
        else:
            page = os.path.join(self.homepath,subpath)

        if os.path.isfile(page):
            if page.endswith('.md'):
                if (subpath is None) or subpath in self.doc.pages:
                    editorbutton=True
                else:
                    editorbutton=False
                return self.renderer.render_md_file(page,subpath,editorbutton=editorbutton)
            else:
                return flask.send_file(os.path.abspath(page))

        page = os.path.join(self.gbpath,subpath)
        if os.path.isfile(page):
            return flask.send_file(page)
        flask.abort(404)

    def run(self, host='localhost', port=6178, debug=None):
        # Run local server
        super(GBServer, self).run(host, port)

    def _dev_editor_static(self, subpath):
        url = "http://localhost:8080/static/live-editor/" + subpath
        try:
            r = requests.request(flask.request.method, url)
        except requests.exceptions.RequestException as e:
            msg = "ERROR: Could not connect to live-editor dev server for '{}', did you forget to start it?".format(
                url
            )
            return flask.abort(flask.Response(msg, status=500))
        return r.text

    def _dev_editor_sockjs(self, subpath):
        url = "http://localhost:8080/sockjs-node/" + subpath + flask.request.query_string.decode()
        try:
            r = requests.request(flask.request.method, url)
        except requests.exceptions.RequestException as e:
            msg = "ERROR: Could not connect to live-editor dev server for '{}', did you forget to start it?".format(
                url
            )
            return flask.abort(flask.Response(msg, status=500))
        return r.text

    def _dev_editor_webpack(self, subpath):
        url = "http://localhost:8080/__webpack_dev_server__/" + subpath + flask.request.query_string.decode()
        try:
            r = requests.request(flask.request.method, url)
        except requests.exceptions.RequestException as e:
            msg = "ERROR: Could not connect to live-editor dev server for '{}', did you forget to start it?".format(
                url
            )
            return flask.abort(flask.Response(msg, status=500))
        return r.text

    def _dev_other_static(self, subpath):
        return flask.send_from_directory('static', subpath)

def HTMLBuild(conf,build_dir=None):
    
    if build_dir is None:
        build_dir = 'Output'
    
    with open(conf, 'r') as stream:
        settings = yaml.load(stream, Loader=yaml.SafeLoader)
    
    if 'WebsiteRoot' in settings:
        root = settings['WebsiteRoot']
    else:
        root = '/'

    assert os.path.exists(os.path.join(build_dir,"_data","project.yaml")), "Build directory to be a Git Building output."
    with open(os.path.join(build_dir,'_data','project.yaml'), 'r') as stream:
        project_data = yaml.load(stream, Loader=yaml.SafeLoader)
    renderer = GBRenderer(project_data,root=root)
    
    # Dont make site dir setable unless we want to do checks that the directory is correct before removing the whole tree
    site_dir = '_site'
    if os.path.exists (site_dir):
        shutil.rmtree(site_dir)
    os.mkdir(site_dir)
    with open(os.path.join(site_dir,'missing.html'),'w') as html_file:
        html_file.write(renderer.missing_page())
    for filename in project_data['FileList']:
        build_file = os.path.join(build_dir,filename)
        link, fextension = os.path.splitext(filename)
        out_dir = os.path.join(site_dir,os.path.dirname(filename))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if fextension == '.md':
            if filename == project_data['Homepage']:
                out_file = os.path.join(site_dir,'index.html')
            else:
                out_file = os.path.join(site_dir,link+'.html')
            with open(out_file,'w') as html_file:
                html_file.write( fix_md_links( renderer.render_md_file(build_file,filename,editorbutton=False) ) )
        else:
            out_file = os.path.join(site_dir,filename)
            shutil.copy(build_file,out_file)
    
    gbpath = os.path.dirname(gb.__file__)
    static_dir = os.path.join(gbpath,'static')
    for root, dirs, files in os.walk(static_dir):
        for filename in files:
            if not 'live-editor' in root:
                filepath = os.path.join(root,filename)
                out_file = os.path.join(site_dir, os.path.relpath(filepath,gbpath))
                out_dir = os.path.dirname(out_file)
                if not os.path.exists(out_dir):
                    os.makedirs(out_dir)
                shutil.copy(filepath,out_file)

def fix_md_links(html):
    links = re.findall('((href="[^"]*?)(\.md)("\>))',html,re.MULTILINE)
    for link in links:
        html = html.replace(link[0],link[1]+link[3])
    return html

class GBRenderer():

    def __init__(self,project_data,root='/'):
        self.gbpath = os.path.dirname(gb.__file__)
        self.project_data = project_data
        self.root = root

    def header(self,fullpage=True,nav=True,link=None,editorbutton=False):
        nav= nav and not self.project_data['OnePage']
        if link is None:
            edlink='editor'
        else:
            edlink=f'{link}/editor'
        if fullpage:
            output = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.project_data['Title']}</title>
    <link rel="shortcut icon" href="{self.root}static/Logo/favicon.ico" />
    <link rel="icon" type="image/png" href="{self.root}static/Logo/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="{self.root}static/Logo/favicon-16x16.png" sizes="16x16" />
    <link href="{self.root}static/style.css" rel="stylesheet">
    <script type="text/javascript" src="{self.root}static/3d-viewer.js"></script>
</head>
<body>"""
        else:
            output = ''
        output+=f"""<header class="site-header">
<div class="wrapper">
{self.project_header()}"""
        if editorbutton:
            output+=f"""<div class=header-buttons><button onclick="window.location.href = '{edlink}';">Edit</button></div>"""
        output+=f"""</div>
</header>
<div class="page-content">"""
        if nav:
            output+=f"""
            <div>
<nav class="sidebar">
    <a href="#" class="menu-icon">
    <svg viewBox="0 0 18 15">
        <path fill="#424242" d="M18,1.484c0,0.82-0.665,1.484-1.484,1.484H1.484C0.665,2.969,0,2.304,0,1.484l0,0C0,0.665,0.665,0,1.484,0 h15.031C17.335,0,18,0.665,18,1.484L18,1.484z"/>
        <path fill="#424242" d="M18,7.516C18,8.335,17.335,9,16.516,9H1.484C0.665,9,0,8.335,0,7.516l0,0c0-0.82,0.665-1.484,1.484-1.484 h15.031C17.335,6.031,18,6.696,18,7.516L18,7.516z"/>
        <path fill="#424242" d="M18,13.516C18,14.335,17.335,15,16.516,15H1.484C0.665,15,0,14.335,0,13.516l0,0 c0-0.82,0.665-1.484,1.484-1.484h15.031C17.335,12.031,18,12.696,18,13.516L18,13.516z"/>
    </svg>
    </a>
    <div class="trigger">
    {self.page_links(link=link)}
    </div>
</nav></div>"""
        output+=f"""
<div class="wrapper">
"""
        return output

    def page_links(self,link=None):
        html=f'<a class="navhome" href="{self.root}">{self.project_data["Title"]}</a>'
        for page in self.project_data['PageList']:
            if page["Link"] == link:
                class_txt = 'class="active" '
            else:
                class_txt = ''
            html+=f'<a {class_txt}href="{self.root}{page["Link"]}">{page["Title"]}</a>'
        return html


    def authorlist(self):
        text = ''
        for i,author in enumerate(self.project_data['Authors']):
            if i==0:
                pass
            elif i==Nauth-1:
                text+=', and '
            else:
                text+=', '
            text+=f'{author}'
        return text

    def project_header(self):
        html = '<div class=header-text>'
        if self.project_data['Title'] is not None:
            html+=f'<a class="site-title" href="{self.root}">{self.project_data["Title"]}</a>'
        if self.project_data['Authors'] is not None:
            html+='<p class="author">by '
            Nauth = len(self.project_data['Authors'])
            html+=self.authorlist()
            html+='</p>'
        if self.project_data['Affiliation'] is not None:
            html+=f'<p class="affiliation">{self.project_data["Affiliation"]}</p>'
        html+='</div>'
        return html

    def footer(self,fullpage=True):
        output = f"""</div>
</div>
<footer class="site-footer">
<div class="wrapper">
<span class="icon">{codecs.open(os.path.join(self.gbpath,'static','Logo','GitBuilding.svg'), mode="r", encoding="utf-8").read()}</span>
<span class="info">Documentation powered by Git Building</span>
{self.project_footer()}
</div>
</footer>"""
        if fullpage:
            output += """</body>
</html>"""
        return output

    def project_footer(self):
        html=''
        if self.project_data['Authors'] is not None:
            html+='<p class="author">© '
            Nauth = len(self.project_data['Authors'])
            html+=self.authorlist()
            html+=f' {datetime.datetime.now().year}</p>'
        if self.project_data['Email'] is not None:
            html+=f'<p class="email">Contact: <a href="mailto:{self.project_data["Email"]}">{self.project_data["Email"]}</a></p>'
        if self.project_data['License'] is not None:
            html+=f'<p class="license">{self.project_data["Title"]} is released under {self.project_data["License"]}</p>'
        return html

    def render_md_file(self,page,link,editorbutton=False):
        return self.render_md(codecs.open(page, mode="r", encoding="utf-8").read(),link=link,editorbutton=editorbutton)

    def render_md(self,md, link=None,fullpage=True,nav=True,editorbutton=False):
        if self.project_data['OnePage']:
            if (link is None) or (link == self.project_data['Homepage']):
                match = re.search('(^#[ \t]*\S.*\n)([\s\S\n]*)',md,re.MULTILINE)
                md = md.replace(match.group(1),'')
        stls = re.findall('(^(\[[^\]]*\])\((.+?\.stl)\))',md,re.MULTILINE)
        for stl in stls:
            md = md.replace(stl[0],f'{stl[1]}({stl[2]})\n<stl-part-viewer src="{stl[2]}" width="500" height="500" floorcolor="0xf1f1f1"></stl-part-viewer>')
        
        return self.render(markdown(md,extensions=['tables']),link=link,fullpage=fullpage,nav=nav,editorbutton=editorbutton)

    def render(self,html,link=None,fullpage=True,nav=True,editorbutton=False):
        output = self.header(fullpage=fullpage,nav=nav,link=link,editorbutton=editorbutton)
        output+=html
        output+=self.footer(fullpage=fullpage)
        return output

    def missing_page(self):
        return self.render('<h1>Git Building Missing Part</h1>')
