#
# Copyright (c) 2010, 2013, 2015, 2017, 2018, 2019
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import base64
from datetime import datetime
from xml.sax.saxutils import unescape, escape
from lxml import etree


class StandardXML(object):

    @staticmethod
    def Create_Date_Value(date_string, in_format='%Y-%m-%d %H:%M:%S'):
        return datetime.strptime(date_string.strip(), in_format)

    @staticmethod
    def Format_Date_Value(date_value, out_format='%Y-%m-%d %H:%M:%S'):
        return date_value.strftime(out_format)

    @staticmethod
    def Reformat_Date_String(date_string, in_format, out_format):
        return StandardXML.\
            Create_Date_Value(date_string, in_format).\
            strftime(out_format)

    @staticmethod
    def Convert_Field_To_Value(field, fallback_to_text=False):
        is_null = field.attrib.get('isNull', 'false').lower()
        if is_null == 'true':
            return None
        else:
            value = field.text
            data_type = field.attrib.get('dataType', 'string').lower()
            if data_type in ('string', 'char', 'varchar', ):
                if value is not None:
                    value = unescape(value)
            elif data_type in ('ifloat', 'float', 'decimal', ):
                value = float(value)
            elif data_type in ('integer', 'serial', 'smallint', ):
                value = int(float(value))
            elif data_type in ('date', ):
                value = datetime.strptime(value, '%Y-%m-%d')
            elif data_type in ['datetime', ]:
                value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            elif data_type in ['time', ]:
                if len(value) > 4:
                    value = datetime.strptime(value, '%H:%M:%S')
                else:
                    value = datetime.strptime(value, '%H:%M')
            else:
                if fallback_to_text:
                    if value is not None:
                        value = unescape(value)
                    return value
                raise Exception(
                    'Unexpected dataType "{0}" encountered.'.
                    format(data_type, )
                )
            return value

    @staticmethod
    def Parse_Row(row, keys=[]):
        fields = {}
        keys = {}
        for field in row.iterchildren():
            name = field.tag.lower()
            # Determine if value is primary key
            if field.attrib.get('discard', 'false').lower() == 'true':
                continue
            is_key = field.attrib.get('isPrimaryKey', 'false').lower()
            if (name in keys) or (is_key == 'true'):
                is_key = 'true'
            # Process field value
            value = StandardXML.Convert_Field_To_Value(field)
            # Set as key or value
            if (is_key == 'true'):
                keys[name] = value
            else:
                fields[name] = value
        return keys, fields

    @staticmethod
    def Write_Row(wfile, keys, fields, type_map, row_id=None):
        # TODO: support for row:operation and row:recordType

        def prepare_value(value, kind=None):
            # no NULL value should ever visit this function
            is_b64 = False
            text = None
            try:
                text = unicode(value)
                if kind == 'date':
                    """
                    Drop the " 00:00:00" if the type is "date" as the
                    internally used type is "datetime"/"UTCDateTime"
                    """
                    text = text.split()[0]
            except UnicodeDecodeError:
                is_b64 = True
                text = base64.encodestring(value).strip()
            return is_b64, escape(text)

        if row_id is not None:
            wfile.write('<row id="{0}">'.format(row_id, ))
        else:
            wfile.write('<row>')
        for key, value in keys.items():
            if value is not None:
                is_b64, value = prepare_value(value, kind=type_map.get(key), )
                wfile.write(
                    '<{0} dataType="{1}" isPrimaryKey="true"{2}>{3}</{0}>'  # noqa
                    .format(
                        key,
                        type_map.get(key),
                        ' isBase64="true"' if is_b64 else '',
                        value,
                    )
                )
            else:
                wfile.write(
                    '<{0} dataType="{1}" isPrimaryKey="true" isNull="true"/>'  # noqa
                    .format(
                        key, type_map.get(key),
                    )
                )
        for key, value in fields.items():
            if value is not None:
                is_b64, value = prepare_value(value, kind=type_map.get(key), )
                wfile.write(
                    '<{0} dataType="{1}"{2}>{3}</{0}>'  # noqa
                    .format(
                        key,
                        type_map.get(key),
                        ' isBase64="true"' if is_b64 else '',
                        value,
                    )
                )
            else:
                wfile.write(
                    '<{0} dataType="{1}" isNull="true"/>'  # noqa
                    .format(
                        key, type_map.get(key),
                    )
                )
        wfile.write('</row>')

    @staticmethod
    def Read_ResultSet_Metadata(handle):
        handle.seek(0)
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse(handle, events=("start", "end")):
            if (event == 'start' and element.tag == 'ResultSet'):
                table_name = element.attrib.get('tableName')
                format_name = element.attrib.get('formatName')
                format_class = element.attrib.get('className')
                break
        return table_name, format_name, format_class

    @staticmethod
    def Read_Rows(
        handle, pkeys=[],
        for_operation=None,
        fallback_to_text=False,
        for_record_type=None,
        with_metadata=False,
    ):
        '''
        TODO: Only process rows between Result tags?
        TODO: Directory specified keys via pkeys= paramater should be mandatory
        '''
        handle.seek(0)
        if not for_operation:
            for_operation = 'any'
        for event, element in etree.iterparse(handle, events=("start", "end")):
            if (event == 'start') and (element.tag == 'row'):
                if with_metadata:
                    type_map = {}
                else:
                    type_map = None
                keys = {}
                fields = {}
                row_operation = element.attrib.get('operation', 'any')
                record_type = element.attrib.get('recordType', None)
            elif (event == 'end') and (element.tag == 'row'):
                element.clear()
                # for-operation filter
                if (
                    (
                        (for_operation == 'any') or
                        (row_operation == 'any') or
                        (for_operation == row_operation)
                    ) and (
                        (for_record_type is None) or
                        (for_record_type == record_type)
                    )
                ):
                    if type_map is None:
                        yield keys, fields
                    else:
                        yield keys, fields, (
                            row_operation, record_type, type_map,
                        )
            elif (event == 'end') and (element.tag.lower() == 'resultset'):
                return
            elif (event == 'end'):
                '''
                We are assuming "row" element???? Why??? Should we not
                verify that this is the case?
                '''
                if element.attrib.get('discard', 'false').lower() == 'true':
                    continue
                is_key = element.attrib.get('isPrimaryKey', 'false').lower()
                if (element.tag in pkeys) or (is_key == 'true'):
                    is_key = 'true'
                value = StandardXML.Convert_Field_To_Value(
                    element, fallback_to_text=fallback_to_text,
                )
                if (is_key == 'true'):
                    keys[element.tag] = value
                else:
                    fields[element.tag] = value
                if type_map is not None:
                    type_map[element.tag] = element.attrib.get(
                        'dataType', 'string'
                    ).lower()
        return

    @staticmethod
    def Filter_Rows(rfile, wfile, callback=None):
        wfile.seek(0)
        rfile.seek(0)
        table_name = None
        format_name = None
        format_class = None
        for event, element in etree.iterparse(rfile, events=("start",)):
            if (event == 'start' and element.tag == 'ResultSet'):
                table_name = element.attrib.get('tableName')
                format_name = element.attrib.get('formatName')
                format_class = element.attrib.get('className')
                element.clear()
                break
        wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        wfile.write(
            u'<ResultSet formatName="{0}" className="{1}" tableName="{2}">'.
            format(format_name, format_class, table_name)
        )
        rfile.seek(0)
        for event, element in etree.iterparse(rfile, events=("end",)):
            if (event == 'end') and (element.tag == 'row'):
                if (callback is not None):
                    if (callback(element)):
                        wfile.write(etree.tostring(element))
                else:
                    wfile.write(etree.tostring(element))
                element.clear()
            elif (event == 'end') and (element.tag == 'ResultSet'):
                wfile.write(u'</ResultSet>')
                break
