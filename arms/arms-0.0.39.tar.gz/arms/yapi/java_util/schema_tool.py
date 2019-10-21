import yaml
import os
from arms.yapi.util import parse_comment, is_comment_format


def is_utf8mb4(stype, text):
    """
    >>> is_utf8mb4('VARCHAR(100)', "重庆")
    True
    >>> is_utf8mb4('JSON', "chongqing")
    False
    """
    return (stype.startswith('VARCHAR(') or stype in ['TEXT', 'JSON']) \
           and any(ord(c) >= 256 for c in text)


def is_strtype(stype):
    return


def sql_type_of(pytype):
    typename_map = {
        'int': 'INT(11)',
        'long': 'BIGINT(20)',
        'bool': 'TINYINT(1)',
        'float': 'DOUBLE',
        'str': 'VARCHAR(200)',
        'text': 'TEXT',
        'datetime': 'DATETIME',
        'date': 'DATE',
        'time': 'TIME',
        'json': 'JSON',
    }
    if pytype.startswith('+'):
        return '+' + sql_type_of(pytype[1:])
    if pytype.startswith('str('):
        return 'VARCHAR(' + pytype[4:]
    return typename_map.get(pytype, None)


normal_sline_tpl = "  `{name}` {stype} DEFAULT NULL COMMENT '{comment}',"
primary_sline_tpl = "  `{name}` {stype} NOT NULL AUTO_INCREMENT COMMENT '{comment}',"
utf8_sline_tpl = "  `{name}` {stype} CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '{comment}',"

table_tpl = """
DROP TABLE IF EXISTS `{model_name}`;
CREATE TABLE `{model_name}` (
{scode}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def scode_of(model_name, model_dict):
    slines = []
    primary_key = ''
    for name, value in model_dict.items():
        if name == '//':
            continue
        assert is_comment_format(value), "invalid value: " + str(value)
        pytype, realvalue, comment, _ = parse_comment(value)
        stype = sql_type_of(pytype)
        assert stype is not None, "invalid type: " + value
        if name.lower() == model_name.lower() + 'id':
            primary_key = name
            assert not stype.startswith('+'), "invalid private key: " + value
            sline = primary_sline_tpl.format(stype=stype, name=name, comment=comment)
        elif stype.startswith('+'):
            continue
        elif isinstance(realvalue, str) and is_utf8mb4(stype, realvalue):
            sline = utf8_sline_tpl.format(stype=stype, name=name, comment=comment)
        else:
            sline = normal_sline_tpl.format(stype=stype, name=name, comment=comment)

        slines.append(sline)

    slines.append("  PRIMARY KEY (`%s`)" % primary_key)
    scode = '\n'.join(slines)
    return dict(scode=scode, primary_key=primary_key)


def scontent_of(model_name, model_dict):
    scode_ret = scode_of(model_name, model_dict)
    scode = scode_ret['scode']
    primary_key = scode_ret['primary_key']
    if not primary_key:
        return ''
    return table_tpl.format(model_name='Tbl'+model_name, scode=scode)


def diff_scode(scode, model_data):
    exit_code = 0
    cur_modelname = ''
    new_keys = set()
    for model_name, model_dict in model_data.items():
        for key, value in model_dict.items():
            if key == '//': continue
            pytype = parse_comment(value)[0]
            if pytype.startswith('+'): continue
            new_keys.add('%s.%s' % (model_name, key))
    for line in scode.splitlines():
        line = line.strip()
        if line.startswith('CREATE TABLE '):
            cur_modelname = line.split('`Tbl', 1)[-1].split('`')[0]
        elif cur_modelname and line.startswith(') ENGINE'):
            cur_modelname = ''
        elif line.startswith('`'):
            old_key = cur_modelname + '.' + line.split('`', 1)[-1].split('`')[0]
            if old_key not in new_keys:
                print('Need deleting: %s' % old_key)
                exit_code = 1
            else:
                new_keys.remove(old_key)

    for key in new_keys:
        print('Need inserting: %s' % key)
        exit_code = 1

    return exit_code


def process(infile, outfile, checkonly):
    scontents = []
    model_data = yaml.load(open(infile).read())
    if os.path.isfile(outfile) and checkonly:
        scode = open(outfile).read()
        exit_code = diff_scode(scode, model_data)
        exit(exit_code)
    else:
        for model_name, model_dict in model_data.items():
            scontents.append(scontent_of(model_name, model_dict))

        with open(outfile, 'w') as f:
            f.write('\n'.join(scontents))
