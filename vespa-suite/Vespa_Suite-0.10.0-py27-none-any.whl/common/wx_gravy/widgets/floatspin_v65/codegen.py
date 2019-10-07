from __future__ import division

import common


class PythonCodeGenerator(object):
    def __init__(self):
        self.pygen = common.code_writers['python']
    
    def __get_import_modules(self):
        
        s = """
import vespa.common.wx_gravy.util
if vespa.common.wx_gravy.util.is_wx_floatspin_ok():
    from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY
else:
    from vespa.common.wx_gravy.widgets.floatspin.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY
"""
        return [s]

    import_modules = property(__get_import_modules)

    def cn(self, class_name):
        if class_name[:2] == 'wx': 
            return 'wx.' + class_name[2:]
        elif (class_name[:4] == 'EVT_') and (class_name != "EVT_FLOATSPIN"):
            return 'wx.' + class_name
        return class_name

    def cn_f(self, flags):
        return "|".join([self.cn(f) for f in str(flags).split('|')])

    def get_code(self, obj):
        prop = obj.properties
        id_name, id = self.pygen.generate_code_id(obj)
        if not obj.parent.is_toplevel: parent = 'self.%s' % obj.parent.name
        else: parent = 'self'

        init = []
        if id_name: init.append(id_name)
        klass = obj.klass
        if klass == obj.base: klass = self.cn(klass)

        floatSpinCtorParams = ""

        value = prop.get("value")
        if value:
            floatSpinCtorParams += ", value=%s"%value 

        increment = prop.get("increment")
        if increment:
            floatSpinCtorParams += ", increment=%s"%increment

        digits = prop.get("digits")
        if digits:
            floatSpinCtorParams += ", digits=%s"%digits

        range_ = prop.get("range")
        if range_:
            min_, max_ = range_.split(',')
            floatSpinCtorParams += ", min_val=%s, max_val=%s" % (min_, max_)

        # style is a special property, because it is set in the constructor
        style = prop.get("style")
        if style:
            style = ", style=%s" % self.cn_f(style)
        else:
            style = ""


        # extrastyle is a special property, because it is set in the constructor
        extrastyle = prop.get("extrastyle")
        if extrastyle:
            extrastyle = ", agwStyle=%s" % self.cn_f(extrastyle)
        else:
            extrastyle = ""
        
        
        init.append('self.%s = %s(%s, %s%s%s%s)\n' % (obj.name, klass, parent, id, floatSpinCtorParams, style, extrastyle))

        

        # properties...
        props_buf = self.pygen.generate_common_properties(obj)
        # borders
        borders = prop.get('borders')
        if borders:
            props_buf.append('self.%s.SetBorders(%s)\n' % (obj.name, borders))
        # url
        url = prop.get('url')
        if url:
            url = self.pygen.quote_str(url)
            props_buf.append('self.%s.LoadPage(%s)\n' % (obj.name, url))
        # html code
        html_code = prop.get('html_code')
        if html_code:
            html_code = self.pygen.quote_str(html_code)
            props_buf.append('self.%s.SetPage(%s)\n' % (obj.name, html_code))
            
        return init, props_buf, []

# end of class PythonCodeGenerator




def initialize():
    #common.class_names['EditHtmlWindow'] = 'wxHtmlWindow'
    common.class_names['EditFloatSpin'] = 'FloatSpin'

    # python code generation functions
    pygen = common.code_writers.get("python")
    if pygen:
        pygen.add_widget_handler('FloatSpin', PythonCodeGenerator())


