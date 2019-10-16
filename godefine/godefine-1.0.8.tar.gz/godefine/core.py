#!/usr/bin/env python3

import re
import argparse
import os
import sys
import typing
import pathlib

try:
    import wcwidth  # use by tabulate
except ImportError:
    print('module: `wcwidth` not load, it can bring some problem unexpected with some language', end='\n\n',
          file=sys.stderr)

from tabulate import tabulate


# parse program startup args
def parse_args():
    #
    parser = argparse.ArgumentParser(description='godefine')
    #
    parser.add_argument('-v', '--version',
                        default=False,
                        action='store_true',
                        help='show godefine version')
    parser.add_argument('-t', '--template', type=str, help='template file')
    parser.add_argument('-o', '--output', type=str, help='output file name')
    parser.add_argument('-i', '--input', type=str, help='use var is specified file')
    parser.add_argument('--vars', type=str, help='use var in command line', nargs='+')
    parser.add_argument('--dryrun',
                        default=False,
                        action='store_true',
                        help='dry run, just print vars without generate output')
    #
    parser.add_argument('-f', '--force',
                        default=False,
                        action='store_true',
                        help='force generate code,skip any error')

    args = parser.parse_args()
    #
    if args.version:
        from .consts import name, version, description
        print('%s: %s\n%s' % (name, version, description))
        exit(0)
    #
    print('Environment:')
    print(tabulate([
        ('input var\'s file', args.input),
        ('var from command-line', '\n'.join(args.vars or [])),
        ('force execute?', args.force),
        ('template file', args.template),
        ('output file', args.output),
        ('dry-run? just print vars', args.dryrun),
    ], tablefmt='grid', missingval='❌'), end='\n\n')
    #
    if args.output is None or args.template is None:
        print('output and template both required!', file=sys.stderr)
        parser.print_help()
        exit(7)
    return args


def parse_tokens(regex_result: typing.Dict) -> typing.Dict:
    return {
        'var_name': regex_result.get('var_name2') or regex_result.get('var_name'),
        'comment': regex_result.get('comment2') or regex_result.get('comment'),
        'default': regex_result.get('default_val')
    }


_include_parser = re.compile(r'@include\((.*?)\)')


def grab_vars(input_file: typing.AnyStr, var_line: typing.Optional[typing.List]) -> typing.Dict:
    if var_line is None:
        var_line = {}
    out = {}
    save_cwd = os.getcwd()
    input_file_path = pathlib.Path(input_file)
    if not input_file_path.exists() or not input_file_path.is_file():
        raise FileNotFoundError('input file=%s not found or not a file!' % input_file)
    input_file_parent_path = input_file_path.absolute().parent.absolute()
    try:
        os.chdir(input_file_parent_path)
        with open(input_file_path.name) as var_file:
            for line in var_file.readlines():
                strip_n = line.rstrip('\n')
                include_ls = _include_parser.findall(strip_n)
                if len(include_ls) != 0:
                    for include_item in include_ls:
                        new_dict = grab_vars(include_item, None)
                        if len(new_dict) != 0:
                            out = dict(out, **new_dict)
                else:
                    args_line2dict(strip_n, out)
        for it in var_line:
            args_line2dict(it, out)
    except Exception as err:
        raise err
    finally:
        os.chdir(save_cwd)

    return out


def args_line2dict(argv: typing.AnyStr, output_dict: typing.Dict):
    r = argv.split('=', maxsplit=1)
    if len(r) != 2:
        return
    output_dict[r[0]] = r[1]


def generate_output(input_file: typing.AnyStr, output_file: typing.AnyStr, var_dict: typing.Dict):
    try:
        with open(input_file, 'r')as ifile:
            ifile_content = fread_all(ifile)
        if ifile_content is None:
            return
        for k, v in var_dict.items():
            ifile_content = re.sub(r'\${%s}' % k, v, ifile_content)
        with open(output_file, 'w') as ofile:
            ofile.write(ifile_content)
    except Exception as e:
        print('❗❗❗generate output failed:%s' % e)
        exit(2)


def wrap_blank(input_str: typing.AnyStr) -> typing.AnyStr:
    if input_str is None or len(input_str) == 0:
        return '''(blank string)'''
    return input_str


def fread_all(f: typing.TextIO) -> typing.AnyStr:
    f.seek(0, os.SEEK_END)
    flen = f.tell()
    f.seek(0, os.SEEK_SET)
    return f.read(flen)


def main():
    cmd_args = parse_args()
    user_specified_vars = {}
    try:
        user_specified_vars = grab_vars(cmd_args.input, cmd_args.vars)
    except Exception as err:
        print('❗❗❗grab vars err=%s' % err, file=sys.stderr)
        exit(5)

    regex = re.compile(
        r'''(?P<var_name>((?<={).*(?=}))).*(?<=//)\s?(?P<comment>(\b.*))(?=(@default=))\5(?P<default_val>(.*))(?=;)'''
        r'''|((?P<var_name2>((?<={).*(?=}))).*(?<=//)\s?(?P<comment2>(\b.*)))''')

    todo_list = []

    try:
        with open(cmd_args.template) as file:
            template_file_content = fread_all(file)
            match_iter = regex.finditer(template_file_content)
            for result in match_iter:
                if result:
                    result_dict = parse_tokens(result.groupdict())
                    todo_list.append(result_dict)
    except Exception as e:
        print('❗❗❗open file:%s filed, reason:%s' % (cmd_args.template, e))
        exit(3)

    vars_not_ready = []
    #
    table_header = ['var_name', 'comment', 'default', 'current', 'ready?']
    table_data = []
    # prepare table
    #
    for it in todo_list:
        var_name = it['var_name']
        default_val = it['default']
        comment = it['comment']
        #
        if default_val is not None and var_name not in user_specified_vars:
            user_specified_vars[var_name] = default_val
        #
        user_specified_val = user_specified_vars.get(var_name)
        #

        table_data.append((var_name,
                           wrap_blank(comment),
                           wrap_blank(default_val),
                           wrap_blank(user_specified_val),
                           ('✅' if default_val is not None or user_specified_val is not None else None)))
        #
        if user_specified_val is None:
            vars_not_ready.append(var_name)
    #
    print('Processing....')
    #
    print(tabulate(table_data,
                   headers=table_header,
                   tablefmt='grid',
                   missingval='❌'),
          end='\n\n')

    # generate failed vars
    if len(vars_not_ready) != 0:
        print('❗❗❗error: you must specify manual:', ','.join(vars_not_ready))
        if not cmd_args.force:
            exit(4)
        print('❗❗❗warning: some vars not specified, force generate output...')
    #
    if not cmd_args.dryrun:
        generate_output(cmd_args.template, cmd_args.output, user_specified_vars)
    else:
        print('🙈🙈🙈skip generate step...')
    #
    print('\n🎉🎉🎉 Success! 🎉🎉🎉')


if __name__ == '__main__':
    main()
