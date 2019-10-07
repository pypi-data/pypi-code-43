#  Copyright 2014 Michael Medin
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from google.protobuf.descriptor import FieldDescriptor
import re, sys
from jinja2 import Template, Environment
import hashlib

FIELD_LABEL_MAP = {
    FieldDescriptor.LABEL_OPTIONAL: 'optional',
    FieldDescriptor.LABEL_REQUIRED: 'required',
    FieldDescriptor.LABEL_REPEATED: 'repeated'
}

FIELD_TYPE_MAP = {
    FieldDescriptor.TYPE_DOUBLE: 'double',
    FieldDescriptor.TYPE_FLOAT: 'float',
    FieldDescriptor.TYPE_INT64: 'int64',
    FieldDescriptor.TYPE_UINT64: 'uint64',
    FieldDescriptor.TYPE_INT32: 'int32',
    FieldDescriptor.TYPE_FIXED64: 'fixed64',
    FieldDescriptor.TYPE_FIXED32: 'fixed32',
    FieldDescriptor.TYPE_BOOL: 'bool',
    FieldDescriptor.TYPE_STRING: 'string',
    FieldDescriptor.TYPE_GROUP: 'group',
    FieldDescriptor.TYPE_MESSAGE: 'message',
    FieldDescriptor.TYPE_BYTES: 'bytes',
    FieldDescriptor.TYPE_UINT32: 'uint32',
    FieldDescriptor.TYPE_ENUM: 'enum',
    FieldDescriptor.TYPE_SFIXED32: 'sfixed32',
    FieldDescriptor.TYPE_SFIXED64: 'sfixed64',
    FieldDescriptor.TYPE_SINT32: 'sint32',
    FieldDescriptor.TYPE_SINT64: 'sint64',
}


def make_title(prefix, text, suffix):
    text = text.strip()
    ret = ''
    if prefix:
        ret = len(text)*prefix + '\n'
    ret += text + '\n'
    ret += len(text)*suffix + '\n'
    return ret

def remove_prefix(string):
    return string.split(".")[-1]

def md_pad(string, count):
    s = '%s'%string
    return s.ljust(count)

def format_comment(string):
    return '\n'.join(map(lambda x:x.strip().lstrip('*'), string.split('\n')))

def first_line(string):
    return string.split('\n')[0]
    
def make_table(hdr, list):
    sz = []
    for h in hdr:
        sz.append(len(h))
    for l in list:
        for idx, val in enumerate(l):
            sz[idx] = max(sz[idx], len(val))
    ret = ""
    for idx, val in enumerate(hdr):
        if idx > 0:ret += " | "
        ret += val.ljust(sz[idx])
    ret += "\n"
    for idx, val in enumerate(hdr):
        if idx > 0:ret += " | "
        ret += ''.ljust(sz[idx], '-')
    ret += "\n"
    for l in list:
        for idx, val in enumerate(l):
            if idx > 0:ret += " | "
            ret += val.ljust(sz[idx])
        ret += "\n"
    return ret

def format_const_list(fd, path):
    global comments
    list = []
    for idx, value in enumerate(fd):
        spath = '4,0,' + path + ',2,%d'%idx
        comment = first_line(format_comment(comments[spath])) if spath in comments else ''
        list.append([value.name, '%d'%value.number, comment])
    return make_table(['Possible values', 'Value', 'Description'], list)

def format_field_descriptor(fd, path):
    global comments
    if not fd:
        return ''
    list = []
    for idx, value in enumerate(fd):
        spath = path + ',2,%d'%idx
        type = value.type_name.split(".")[-1] if value.type_name else FIELD_TYPE_MAP[value.type]
        comment = first_line(format_comment(comments[spath])) if spath in comments else ''
        list.append([FIELD_LABEL_MAP[value.label], type, value.name, comment])
    return make_table(['Modifier', 'Type', 'Key', 'Description'], list)

HEADER_TPL = """{% macro gen_message(desc, level, path, trail) -%}
{% set trail = trail + '.' + desc.name -%}
<a name=".{{trail}}"></a>
{{ '#'*level }} {{trail|remove_prefix}}

`{{trail}}` {% if COMMENTS[path] -%}{{COMMENTS[path]|format_comment}}{% endif %}

{% for field_descriptor in desc.enum_type -%}{% set spath = path + ',4,%d'%loop.index0 -%}
### {{field_descriptor.name}}

{% if COMMENTS[spath] -%}{{COMMENTS[spath]|format_comment}}
{% endif %}
{{field_descriptor.value|format_const_list(path)}}

{% endfor -%}
{{desc.field|format_field_descriptor(path)}}
{% for sdesc in desc.nested_type -%}{{ gen_message(sdesc, level+1, "%s,3,%d"%(path, loop.index0), trail) }}{% endfor %}
{%- endmacro %}
# API Reference

{% for sdesc in desc.message_type %}
{{ gen_message(sdesc, 2, "4,%d"%loop.index0, desc.package) }}
{% endfor %}
"""

def make_paths(source_code):
    locations = {}
    for l in source_code.location:
        if hasattr(l, 'leading_comments') and l.leading_comments:
            locations[','.join(map(lambda x:'%s'%x, l.path))] = l.leading_comments.strip()
    return locations

def document_file(file_descriptor):
    global comments
    env = Environment()
    env.filters['remove_prefix'] = remove_prefix
    env.filters['md_pad'] = md_pad
    env.filters['format_comment'] = format_comment
    env.filters['first_line'] = first_line
    env.filters['format_const_list'] = format_const_list
    env.filters['format_field_descriptor'] = format_field_descriptor
    
    comments = make_paths(file_descriptor.source_code_info)
    template = env.from_string(HEADER_TPL)
    data ={
        'desc':file_descriptor, 
        'COMMENTS':comments}
    return template.render(data)
