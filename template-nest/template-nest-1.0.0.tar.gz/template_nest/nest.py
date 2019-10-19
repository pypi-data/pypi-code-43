import re


class Nest:

    def __init__(self, args):

        # defaults
        self.opt = {
            'template_ext': '.html',
            'template_dir': '.',
            'views_module': '',
            'token_delims': [ '<%','%>' ],
            'comment_delims': [ '<!--','-->' ],
            'template_label': 'TEMPLATE',
            'view_label': 'VIEW',
            'show_labels': False,
            'defaults': {},
            'defaults_namespace_char': '.',
            'fixed_indent': False,
            'error_on_bad_params': True,
            'escape_char': '\\'
        }

        if args is not None:
            for key in args:
                setattr(self,key,args[key])

    @property
    def template_dir(self):
        return self.opt['template_dir']

    @template_dir.setter
    def template_dir(self,template_dir):
        self.opt['template_dir'] = template_dir

    @property
    def views_module(self):
        return self.opt['views_module']

    @views_module.setter
    def views_module(self,views_module):
        self.opt['views_module'] = views_module

    @property
    def template_ext(self):
        return self.opt['template_ext']

    @template_ext.setter
    def template_ext(self,template_ext):
        self.opt['template_ext'] = template_ext

    @property
    def token_delims(self):
        return self.opt['token_delims']

    @token_delims.setter
    def token_delims(self,token_delims):
        if not isinstance( token_delims, list ):
            raise ValueError("'token_delims' should be a list. Instead got a %s with value %s" \
                % ( type( token_delims ), token_delims ) )
        if len( token_delims ) != 2:
            raise ValueError("'token_delims' should be a 2 element list. Instead got a list with %s elements" \
                % len( token_delims ) )
        if not isinstance( token_delims[0], str ):
            raise ValueError("First 'token_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( token_delims[0] ), token_delims[0] ) )
        if not isinstance( token_delims[1], str ):
            raise ValueError("Second 'token_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( token_delims[1] ), token_delims[1] ) )
        if len( token_delims[0] ) < 1:
            raise ValueError("First token_delim cannot be an empty string")
        if len( token_delims[1] ) < 1:
            raise ValueError("Second token_delim cannot be an empty string")


        self.opt['token_delims'] = token_delims


    @property
    def comment_delims(self):
        return self.opt['comment_delims']

    @comment_delims.setter
    def comment_delims(self,comment_delims):
        if not isinstance( comment_delims, list ):
            raise ValueError("'comment_delims' should be a list. Instead got a %s with value %s" \
                % ( type( comment_delims ), comment_delims ) )
        if len( comment_delims ) != 2:
            raise ValueError("'token_delims' should be a 2 element list. Instead got a list with %s elements" \
                % len( comment_delims ) )
        if not isinstance( comment_delims[0], str ):
            raise ValueError("First 'comment_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( comment_delims[0] ), comment_delims[0] ) )
        if not isinstance( comment_delims[1], str ):
            raise ValueError("Second 'comment_delim' should be of type 'str' instead got '%s' with value %s " \
                % ( type( comment_delims[1] ), comment_delims[1] ) )
        if len( comment_delims[0] ) < 1:
            raise ValueError("First comment_delim cannot be an empty string")
        self.opt['comment_delims'] = comment_delims


    @property
    def template_label(self):
        return self.opt['template_label']

    @template_label.setter
    def template_label(self,template_label):
        self.opt['template_label'] = template_label

    @property
    def show_labels(self):
        return self.opt['show_labels']

    @show_labels.setter
    def show_labels(self,show_labels):
        if ( not isinstance( show_labels, bool ) ):
            raise ValueError("'show_labels' expects a boolean, instead got a %s with value %s" \
                % ( type(show_labels), show_labels ))
        self.opt['show_labels'] = show_labels

    @property
    def defaults(self):
        return self.opt['defaults']

    @defaults.setter
    def defaults(self,defaults):
        self.opt['defaults'] = defaults

    @property
    def defaults_namespace_char(self):
        return self.opt['defaults_namespace_char']

    @defaults_namespace_char.setter
    def defaults_namespace_char(self,defaults_namespace_char):
        if not isinstance( defaults_namespace_char, str ):
            raise ValueError("'defaults_namespace_char' expects a single char, instead got a %s with value %s" \
                % ( type( defaults_namespace_char ), defaults_namespace_char ) )
        if len(defaults_namespace_char) != 1:
            raise ValueError("'defaults_namespace_char' expects a single char, instead got string '%s' of length %s" \
                % ( defaults_namespace_char, len(defaults_namespace_char) ) )
        self.opt['defaults_namespace_char'] = defaults_namespace_char

    @property
    def fixed_indent(self):
        return self.opt['fixed_indent']

    @fixed_indent.setter
    def fixed_indent(self,fixed_indent):
        if ( not isinstance( fixed_indent, bool ) ):
            raise ValueError("'fixed_indent' expects a boolean, instead got a %s with value %s" \
                % ( type(fixed_indent), fixed_indent ))
        self.opt['fixed_indent'] = fixed_indent

    @property
    def error_on_bad_params(self):
        return self.opt['error_on_bad_params']

    @error_on_bad_params.setter
    def error_on_bad_params(self,error_on_bad_params):
        if ( not isinstance( error_on_bad_params, bool ) ):
            raise ValueError("'show_labels' expects a boolean, instead got a %s with value %s" \
                % ( type(error_on_bad_params), error_on_bad_params ))
        self.opt['error_on_bad_params'] = error_on_bad_params

    @property
    def escape_char(self):
        return self.opt['escape_char']

    @escape_char.setter
    def escape_char(self,escape_char):
        if not isinstance( escape_char, str ):
            raise ValueError("'escape_char' expects a single char, instead got a %s with value %s" \
                % ( type( escape_char ), escape_char ) )
        if len(escape_char) > 1:
            raise ValueError("'escape_char' expects a single char, instead got string '%s' of length %s" \
                % ( escape_char, len(escape_char) ) )
        self.opt['escape_char'] = escape_char
    

    def render(self,comp):

        if ( isinstance( comp, list ) ):
            result = self._render_list( comp )
        elif ( isinstance( comp, dict ) ):
            result = self._render_dict( comp )
        else:
            result = comp

        return result


    def _render_list(self,comp):

        result = ''
        for item in comp:
            result += self.render( item )
        return result

    def _render_dict(self,comp):

        if self.opt['template_label'] in comp:
            return self._render_template( comp )
        else:
            import json
            raise NameError("Encountered dict with no view or template label: "+json.dumps( comp, indent=4 ))

    def _render_template(self,comp):

        template_name = comp[ self.opt['template_label'] ]
        if template_name == None:
            raise NameError("Encountered dict with no name label")

        param = {}

        for key in comp:
            if key == self.template_label:
                continue
            param[key] = self.render( comp[key] )

        template = self._get_template( template_name )

        result = self._fill_in( template_name, template, param )

        if ( self.show_labels ):
            ca = self.opt['comment_delims'][0]
            cb = self.opt['comment_delims'][1]

            result = ca + " BEGIN " + template_name + cb + "\n" + result + \
                "\n" + ca + " END " + template_name + cb + "\n"

        return result

    def _get_template(self,name):

        import os
        path = os.path.join(self.opt['template_dir'],name + self.opt['template_ext'])
        f = open(path,"r")
        text = f.read().rstrip()
        f.close()
        #raise Exception("text: "+text)
        return text

    def _params_in( self, text ):

        esc = self.opt['escape_char']
        tda = self.token_delims[0]
        tdb = self.token_delims[1]

        if esc:
            rem = re.findall( '(?<!' + re.escape( esc ) + ')' + tda + \
                '\s+(.*?)\s+' +tdb, text)
        else:
            rem = re.findall( tda + '\s+(.*?)\s+' + tdb, text )

        remd = {}
        for name in rem:
            remd[name] = 1

        return remd.keys()


    def params(self,template_name):

        esc = self.opt['escape_char']
        template = self._get_template( template_name )
        frags = re.split( re.escape( esc + esc ), template )

        rem = {}
        for frag in frags:
            params = self._params_in( frag )
            for param in params:
                rem[ param ] = 1

        return sorted( rem.keys() )


    def _token_regex(self,param_name):

        esc = self.opt['escape_char']
        tda = self.token_delims[0]
        tdb = self.token_delims[1]

        if param_name == None:
            param_name = r'.*?'

        token_regex = tda+r'\s+'+param_name+r'\s+'+ tdb
        if esc:
            token_regex = '(?<!'+ re.escape( esc ) + ')('+ token_regex+')'

        return token_regex


    def _fill_in(self,template_name,template,params):

        esc = self.opt['escape_char']
        frags = [ template ]
        if ( esc ):
            frags = re.split( re.escape( esc + esc ), template )


        for param_name in params:
            param_val = params[ param_name ]
            replaced = 0

            if self.fixed_indent:
                for i,frag in enumerate( frags ):
                    spaces_repl = re.findall( r'([^\S\r\n]*)'+self._token_regex( param_name ), frags[i] )

                while spaces_repl:
                    sr = spaces_repl.pop(0)
                    sp = sr[0]
                    repl = sr[1]
                    param_out = re.sub( '\n', '\n'+sp, str(param_val) )

                    if esc:
                        s = re.subn( '(?<!'+re.escape( esc ) + ')' + repl, param_out, frags[i] )
                    else:
                        s = re.subn( repl, param_out, frags[i] )

                    frags[i] = s[0]
                    if s[1] > 0:
                        replaced = 1

            else:
                for i,frag in enumerate( frags ):
                    s = re.subn( self._token_regex( param_name ), str(param_val), frags[i] )
                    frags[i] = s[0]
                    if s[1] > 0:
                        replaced = 1

            if self.error_on_bad_params and replaced == 0:
                raise NameError( '%s does not exist in template %s' % ( param_name, template_name ) )

        for i,frag in enumerate( frags ):

            if self.defaults:
                remd = self._params_in( frag )

                for name in remd:
                    parts = [ name ]
                    if self.defaults_namespace_char != None:
                        parts = re.split( re.escape( self.defaults_namespace_char ), name ) 
                    val = self._get_default_val( self.defaults, parts )
                    frags[i] = re.sub( self._token_regex( name ), val, frags[i] )

            frags[i] = re.sub( self._token_regex( None ), '', frags[i] )


        if esc:
            for i,frag in enumerate( frags ):
                if esc == '\\':
                    frags[i] = frag.replace( '\\','')
                else: 
                    frags[i] = frag.replace( re.escape( esc ), '' )

        text = esc.join( frags ) if esc else frags[0]
        return text




    def _get_default_val(self,ref,parts):
        if len(parts) == 1:
            if parts[0] in ref:
                return ref[ parts[0] ]
            else:
                return ''
        else:
            ref_name = parts.pop(0)
            if ref_name not in ref:
                return ''

            return self._get_default_val( ref[ ref_name ], parts )

