import yaml
import os
from arms.yapi.util import parse_comment, list_find, is_comment_format


def java_type_of(pytype):
    typename_map = {
        'int': 'Integer',
        'long': 'Long',
        'bool': 'Boolean',
        'float': 'Double',
        'str': 'String',
        'text': 'String',
        'datetime': 'LocalDateTime',
        'date': 'LocalDate',
        'time': 'LocalTime',
        'json': 'String',
    }
    if pytype.startswith('+'):
        return '+' + java_type_of(pytype[1:])
    if pytype.startswith('str('):
        return 'String'
    return typename_map.get(pytype, None)


def split_jclass(jclass_text):
    lines = jclass_text.splitlines()
    p = list_find(lines, lambda x: ' class ' in x)
    q = list_find(lines, lambda x: x.strip() == '}')
    assert p >= 0
    return '\n'.join(lines[:p+1]), '\n'.join(lines[p+1:q]), '\n'.join(lines[q:])


def diff_jcode(old_jcode, new_jcode, filename):
    def parse(jcode):
        ret = set()
        for line in jcode.splitlines():
            line = line.strip()
            if not line or line.startswith('@') or line.startswith('//'): continue
            if '{' in line: break
            ret.add(line)
        return ret

    exit_code = 0
    old_keys = parse(old_jcode)
    new_keys = parse(new_jcode)
    for key in old_keys:
        if key not in new_keys:
            print('Need deleting: %s  (%s)' % (key, filename))
            exit_code = 1
        else:
            new_keys.remove(key)

    for key in new_keys:
        print('Need inserting: %s  (%s)' % (key, filename))
        exit_code = 1

    return exit_code


jline_tpl = '{local_head}{sql_head}{jtype} {name};  //{comment}'

jclass_tpl = """package {javaroot}.entity;
import com.parsec.universal.dao.annot.*;
import com.parsec.universal.dao.model.BaseModel;
import lombok.Data;
import org.springframework.format.annotation.DateTimeFormat;
import java.time.*;

{sql_head}
@Data
//{model_comment}
public class {model_name} extends BaseModel <(
{jcode}
)>
"""


def jcode_of(model_name, model_dict):
    jlines = []
    is_table = False
    model_comment = ''
    for name, value in model_dict.items():
        if name == '//':
            model_comment = value
            continue
        assert is_comment_format(value), "invalid value: " + str(value)
        pytype, realvalue, comment, _ = parse_comment(value)
        jtype = java_type_of(pytype)
        assert jtype is not None, "invalid type: " + value
        local_head = sql_head = ''
        if name.lower() == model_name.lower() + 'id':
            is_table = True
            assert not jtype.startswith('+'), "invalid private key: " + value
            sql_head = '@ParsecPrimaryKey\n'
        elif jtype.startswith('+'):
            jtype, sql_head = jtype[1:], '@ParsecNotDBColumn\n'

        if jtype == 'LocalDateTime':
            local_head = '@DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")\n'
        elif jtype == 'LocalDate':
            local_head = '@DateTimeFormat(pattern = "yyyy-MM-dd")\n'
        elif jtype == 'LocalTime':
            local_head = '@DateTimeFormat(pattern = "HH:mm:ss")\n'

        jline = jline_tpl.format(local_head=local_head, sql_head=sql_head, jtype=jtype, name=name, comment=comment)
        jlines.extend(jline.splitlines())

    jcode = '\n'.join('    ' + jline for jline in jlines)
    return dict(jcode=jcode, model_comment=model_comment, is_table=is_table)


def jcontent_of(model_name, model_dict, javaroot):
    """
    >>> output_dict = {'//': 'comment', 'aa': '+bool=1//', 'bb': 'datetime="true"//n#abc', 'cc': 'long=22 //hehe'}
    >>> print(jcontent_of('User', output_dict, 'com.corp.proj'))
    @ParsecNotDBColumn
    Boolean aa;  //
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    LocalDateTime bb;  //n
    Long cc;  //hehe
    """
    jcode_ret = jcode_of(model_name, model_dict)
    jcode = jcode_ret['jcode']
    is_table = jcode_ret['is_table']
    model_comment = jcode_ret['model_comment']
    sql_head = '@ParsecTable("Tbl{}")'.format(model_name) if is_table else ''
    return jclass_tpl.format(javaroot=javaroot, sql_head=sql_head, model_name=model_name, jcode=jcode, model_comment=model_comment
                             ).replace('<(', '{').replace(')>', '}')


def process(infile, outpath, javaroot, checkonly):
    model_data = yaml.load(open(infile).read())
    for model_name, model_dict in model_data.items():
        filename = os.path.join(outpath, model_name + '.java')
        new_jcode = jcode_of(model_name, model_dict)['jcode']
        if not checkonly:
            if os.path.isfile(filename):
                head, jcode, tail = split_jclass(open(filename).read())
                with open(filename, 'w') as f:
                    f.write('{head}\n{jcode}\n{tail}\n'
                            .format(head=head, tail=tail, jcode=new_jcode))
            else:
                with open(filename, 'w') as f:
                    f.write(jcontent_of(model_name, model_dict, javaroot))
        else:
            if os.path.isfile(filename):
                head, jcode, tail = split_jclass(open(filename).read())
                exit_code = diff_jcode(jcode, new_jcode, model_name + '.java')
            else:
                print('Need Model File: ' + filename)
                exit_code = 1
            if exit_code:
                exit(exit_code)

