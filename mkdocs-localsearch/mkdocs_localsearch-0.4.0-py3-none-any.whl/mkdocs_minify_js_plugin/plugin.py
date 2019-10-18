import fnmatch
import os
import sys
import mkdocs
import mkdocs.plugins
import mkdocs.structure.files
from jsmin import jsmin

class MinifyJSPlugin(mkdocs.plugins.BasePlugin):

    config_scheme = (
        ('js_files', mkdocs.config.config_options.Type((str, list), default=None)),
    )

    def on_pre_build(self, config):
        jsfiles = self.config['js_files'] or []
        if not isinstance(jsfiles, list):
            jsfiles = [jsfiles]
        for jsfile in jsfiles:
            name = config['docs_dir'] + '/' + jsfile
            if os.sep != '/':
                name = name.replace(os.sep, '/')
            output_name = name.replace('.js', '.min.js')
            minified = ''
            with open(name) as f:
                minified = jsmin(f.read())
            with open(output_name, 'w') as of:
                of.write(minified)
        return config

    def on_files(self, files, config):
        jsfiles = self.config['js_files'] or []
        if not isinstance(jsfiles, list):
            jsfiles = [jsfiles]
        out = []

        def include(name):
            for jsfile in jsfiles:
                if fnmatch.fnmatchcase(name, jsfile):
                    return False
            return True
        
        for i in files:
            name = i.src_path
            if not include(name):
                continue
            if os.sep != '/':
                namefix = name.replace(os.sep, '/')
                if not include(namefix):
                    continue
            out.append(i)
        return mkdocs.structure.files.Files(out)