
from __future__ import print_function
import sys
from generateds_definedsimpletypes import Defined_simple_type_table

from generateDS import AnyTypeIdentifier, mapName, cleanupName


#
# Globals

# This variable enables users (modules) that use this module to
# check to make sure that they have imported the correct version
# of generatedssuper.py.
Generate_DS_Super_Marker_ = None

# Tables of builtin types
Simple_type_table = {
    'string': 'String',
    'normalizedString': 'String',
    'token': 'String',
    'base64Binary': 'Text',
    'hexBinary': 'Text',
    'integer': 'Integer',
    'positiveInteger': 'Integer',
    'negativeInteger': 'Integer',
    'nonNegativeInteger': 'Integer',
    'nonPositiveInteger': 'Integer',
    'long': 'BigInteger',
    'unsignedLong': 'BigInteger',
    'int': 'Integer',
    'unsignedInt': 'Integer',
    'short': 'SmallInteger',
    'unsignedShort': 'Integer',
    'byte': 'SmallInteger',
    'unsignedByte': 'Integer',
    'decimal': 'Numeric',
    'float': 'Float',
    'double': 'Float',
    'boolean': 'Boolean',
    'duration': 'Float',
    'dateTime': 'DateTime',
    'date': 'Date',
    'time': 'Time',
    'gYear': 'Integer',
    'gYearMonth': 'Integer',
    'gMonth': 'Integer',
    'gMonthDay': 'Integer',
    'gDay': 'Integer',
    'Name': 'String',
    'QName': 'String',
    'NCName': 'String',
    'anyURI': 'String',
    'language': 'String',
    'ID': 'String',
    'IDREF': 'String',
    'IDREFS': 'String',
    'ENTITY': 'String',
    'ENTITIES': 'String',
    'NOTATION': 'String',
    'NMTOKEN': 'String',
    'NMTOKENS': 'String',
}
Integer_type_table = {
    'integer': None,
    'positiveInteger': None,
    'negativeInteger': None,
    'nonNegativeInteger': None,
    'nonPositiveInteger': None,
    'long': None,
    'unsignedLong': None,
    'int': None,
    'unsignedInt': None,
    'short': None,
    'unsignedShort': None,
}
Float_type_table = {
    'decimal': None,
    'float': None,
    'double': None,
}
String_type_table = {
    'string': None,
    'normalizedString': None,
    'token': None,
    'NCName': None,
    'ID': None,
    'IDREF': None,
    'IDREFS': None,
    'ENTITY': None,
    'ENTITIES': None,
    'NOTATION': None,
    'NMTOKEN': None,
    'NMTOKENS': None,
    'QName': None,
    'anyURI': None,
    'base64Binary': None,
    'hexBinary': None,
    'duration': None,
    'Name': None,
    'language': None,
}
Date_type_table = {
    'date': None,
    'gYear': None,
    'gYearMonth': None,
    'gMonth': None,
    'gMonthDay': None,
    'gDay': None,
}
DateTime_type_table = {
    'dateTime': None,
}
Time_type_table = {
    'time': None,
}
Boolean_type_table = {
    'boolean': None,
}


#
# Classes

class MdlWriter:
    def __init__(self):
        self.table_content = ''
        self.class_content = ''

    def wrt_table(self, content):
        self.table_content += content

    def wrt_class(self, content):
        self.class_content += content

    def wrt_table_nl(self, content):
        self.table_content += content + '\n'

    def wrt_class_nl(self, content):
        self.class_content += content + '\n'


class GeneratedsSuper(object):
    def gds_format_string(self, input_data, input_name=''):
        return input_data

    def gds_format_integer(self, input_data, input_name=''):
        return '%d' % input_data

    def gds_format_float(self, input_data, input_name=''):
        return '%f' % input_data

    def gds_format_double(self, input_data, input_name=''):
        return '%e' % input_data

    def gds_format_boolean(self, input_data, input_name=''):
        return '%s' % input_data

    def gds_str_lower(self, instring):
        return instring.lower()

    @classmethod
    def get_prefix_name(cls, tag):
        prefix = ''
        name = ''
        items = tag.split(':')
        if len(items) == 2:
            prefix = items[0]
            name = items[1]
        elif len(items) == 1:
            name = items[0]
        return prefix, name

    @classmethod
    def generate_sa_model_(
            cls, wrtmodels, unique_name_map, class_suffixes):
        mdlwriter = MdlWriter()
        wrttn = mdlwriter.wrt_table_nl
        wrtcn = mdlwriter.wrt_class_nl
        if class_suffixes:
            model_suffix = '_model'
        else:
            model_suffix = ''
        class_name = unique_name_map.get(cls.__name__)
        wrtcn('\nclass %s%s(Base):\n' % (class_name, model_suffix, ))
        wrtcn('    __tablename__ = "%s"\n' % (class_name, ))
        wrtcn('    id = Column(Integer, primary_key=True, '
              'autoincrement=True)\n')
        if cls.superclass is not None:
            wrtcn('    %s_id = Column(Integer, '
                  'ForeignKey("%s%s.id"))' % (
                      cls.superclass.__name__,
                      cls.superclass.__name__, ''))
        for spec in cls.member_data_items_:
            name = spec.get_name()
            prefix, name = cls.get_prefix_name(name)
            data_type = spec.get_data_type()
            is_optional = spec.get_optional()
            prefix, data_type = cls.get_prefix_name(data_type)
            if data_type in Defined_simple_type_table:
                data_type = Defined_simple_type_table[data_type]
                prefix, data_type = cls.get_prefix_name(data_type.type_name)
            name = mapName(cleanupName(name))
            if name == 'id':
                name += 'x'
            elif name.endswith('_') and not name == AnyTypeIdentifier:
                name += 'x'
            clean_data_type = mapName(cleanupName(data_type))
            if data_type == AnyTypeIdentifier:
                data_type = 'string'
            if data_type in Simple_type_table:
                if is_optional:
                    options = 'nullable=True, '
                else:
                    options = ''
                if data_type in Integer_type_table:
                    if spec.container:
                        wrtcn('    %s = Column(String(1000), %s)' % (
                            name, options, ))
                    else:
                        wrtcn('    %s = Column(Integer, %s)' % (
                            name, options, ))
                elif data_type in Float_type_table:
                    if spec.container:
                        wrtcn('    %s = Column(String(1000), %s)' % (
                            name, options, ))
                    else:
                        wrtcn('    %s = Column(Float, %s)' % (
                            name, options, ))
                elif data_type in Date_type_table:
                    #wrtcn('    %s = Column(Date, %s)' % (
                    wrtcn('    %s = Column(String(32), %s)' % (
                        name, options, ))
                elif data_type in DateTime_type_table:
                    #wrtcn('    %s = Column(DateTime, %s)' % (
                    wrtcn('    %s = Column(String(32), %s)' % (
                        name, options, ))
                elif data_type in Time_type_table:
                    #wrtcn('    %s = Column(Time, %s)' % (
                    wrtcn('    %s = Column(String(32), %s)' % (
                        name, options, ))
                elif data_type in Boolean_type_table:
                    wrtcn('    %s = Column(Boolean, %s)' % (
                        name, options, ))
                elif data_type in String_type_table:
                    wrtcn(
                        '    %s = Column(String(1000), %s)' % (
                            name, options, ))
                else:
                    sys.stderr.write('Unhandled simple type: %s %s\n' % (
                        name, data_type, ))
            else:
                mapped_type = unique_name_map.get(clean_data_type)
                clean_data_type = class_name
                child_data_type = mapped_type
                child_name = name
                #
                # Generate Table for relationships to complex types if
                # it is a container, i.e. maxOccurs > 1.
                if True:
                    wrttn("%s_%s_%s_table = Table(" % (
                          clean_data_type, child_data_type, name, ))
                    wrttn("    '%s_%s_%s'," % (
                          clean_data_type, child_data_type, name, ))
                    wrttn("    Base.metadata,")
                    wrttn("    Column('%s_id', ForeignKey('%s.id'))," % (
                          clean_data_type, clean_data_type, ))
                    wrttn("    Column('%s_id', ForeignKey('%s.id'))," % (
                          child_data_type, child_data_type, ))
                    wrttn(")")
                    wrttn("")
                #
                # Generate the field in the class for relatinships to
                # complex types.
                wrtcn("    %s = relationship(" % (name, ))
                wrtcn("        '%s_model'," % (child_data_type, ))
                wrtcn("        secondary=%s_%s_%s_table," % (
                      clean_data_type, child_data_type, child_name))
                if not spec.container:
                    wrtcn("        uselist=False,")
                wrtcn("    )")
        wrtcn("")
        wrtcn("    def __repr__(self):")
        wrtcn("        return '<%s id: %%s>' %% (self.id, )" % (class_name, ))
        wrtcn("")
        wrtmodels(mdlwriter.table_content)
        wrtmodels(mdlwriter.class_content)


#
# Local functions
