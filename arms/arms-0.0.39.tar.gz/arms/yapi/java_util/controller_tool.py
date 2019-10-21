import os
from arms.yapi.model import Project


key_tpl = '@{method}Mapping("{path}")'

code_tpl = """
/**
{fulldoc}
 */
//{name}
{key}
public Result {tag}() <(
    return null;
)>
"""


def load_outpath(outpath, in_keys):
    exit_code = 0
    filenames = [name for name in os.listdir(outpath) if name.endswith('.java')]
    for filename in filenames:
        text = open(os.path.join(outpath, filename)).read()
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('@') and 'Mapping(' in line:
                if line not in in_keys:
                    print('Need deleting: %s  (%s)' % (line, filename))
                    exit_code = 1
                else:
                    del in_keys[line]
    return exit_code


def process(inpath, outpath, javaroot, checkonly):
    filenames = [name for name in os.listdir(inpath) if name.endswith('.md')]
    in_keys = {}
    for filename in filenames:
        text = open(os.path.join(inpath, filename)).read()
        project = Project.loads(text)
        for item in project['list']:
            for subitem in item['list']:
                assert subitem.get('tag'), 'tag(函数名称)不能为空: ' + subitem['name']
                in_key = key_tpl.format(method=subitem['method'].capitalize(), path=subitem['path'])
                code = code_tpl.format(
                    name=subitem['name'], key=in_key, tag=subitem['tag'], fulldoc=subitem['fulldoc'].strip(),
                ).replace('<(', '{').replace(')>', '}')
                in_keys[in_key] = code

    exit_code = load_outpath(outpath, in_keys)
    if in_keys:
        exit_code = 1
        if checkonly:
            for key in in_keys:
                print('Need inserting: %s' % key)
        else:
            with open(os.path.join(outpath, 'OtherController.java'), 'w') as f:
                f.write('package %s.controller;\n\nimport com.parsec.universal.utils.Result;\n'
                        'import org.springframework.web.bind.annotation.*;\n\n@RestController\n'
                        'public class OtherController {\n' % javaroot)
                for code in in_keys.values():
                    f.write(code + '\n')
                f.write('}\n')

    exit(exit_code)

