"""
Creates markdown - while testing contained code snippets.

"""
from ast import literal_eval as ev
from pytest2md import strutils
from functools import partial
from pytest2md import mdtool
from textwrap import dedent
import subprocess as sp
import threading
import inspect
import pytest
import socket
import time
import json
import sys
import pdb
import os


PY2 = sys.version_info[0] < 3
exists = os.path.exists
abspath = os.path.abspath
dirname = os.path.dirname


if not hasattr(sp, 'getoutput'):
    # adding the convenient PY3 getoutput to sp.
    # hope correct (in plane, offline):
    import subprocess as sp

    def _(*a, **kw):
        kw['stdout'] = sp.PIPE
        kw['stderr'] = sp.PIPE
        # we are not at docu build time but at test time
        kw['shell'] = True
        out, err = sp.Popen(*a, **kw).communicate()
        if out.endswith('\n'):
            out = out[:-1]
        return out + err

    sp.getoutput = _

dflt_md_sep = '<!-- autogen tutorial -->'

DIR = lambda d: abspath(dirname(d))


def rpl(what, *with_):
    for w in with_:
        if not isinstance(w, (tuple, list)):
            w = (w, '')
        what = what.replace(w[0], w[1])
    return what


def d_repo_base(tests_dir):
    # where is our root for paths? If we have it its easy:
    here = os.getcwd()
    try:
        os.chdir(tests_dir)
        d = sp.getoutput('git rev-parse --show-toplevel')
        if not d:
            raise
    except:
        # only change, hope the testmodule is one of these top level ones:
        # note: The whole point of py2m is working at test phase
        # i.e. with repos
        d = tests_dir.split('/tests', 1)[0].split('/test', 1)[0]
    os.chdir(here)
    return d


# ------------------------------------------------------- Creating the Markdown

code = """
```code
%s
```"""


def details(md=None, summary='details'):
    # blank line MUST be there:
    return """
<details><summary>%s</summary>

%s
</details>
""" % (
        summary,
        md,
    )


# fmt: off
nothing  = lambda s: s
python   = lambda s: code.replace('code', 'python')   % s
javascript = js  = lambda s: code.replace('code', 'javascript')   % s
bash     = lambda s: code.replace('code', 'bash')     % s
markdown = lambda s: code.replace('code', 'markdown') % (s.replace('```', "``"))
as_lang  = lambda s, lang: code.replace('code', lang) % s
# fmt: on


def deindent(p):
    pp = p.replace('\n', '')
    ind = len(pp) - len(pp.lstrip())
    if not ind:
        return p
    return '\n'.join(
        [l[ind:] if not l[:ind].strip() else l for l in p.splitlines()]
    )


class P2M:
    """API Deliverer for the test files
    """

    def d_test(self):
        return self.ctx['d_test']

    def __init__(
        self,
        fn_test_file,
        d_assets=None,
        fn_target_md=None,
        md_sep=dflt_md_sep,
        fn_target_md_tmpl=None,
        frontmatter=None,
    ):

        """
        called at module level by pytest test module, which creates the md
        e.g. fn_test_file=/Users/gk/GitHub/pytest2md/tests/test_tutorial.py

        - fn_target_md: The final rendered result file. Default: HERE/README.md
        - md_sep: A seperator where we fill in the mardkown from the pytest
        - fn_target_md_tmpl: A template file, containing the static md around the seps.
                        If not given we replace the content at every pytest run in
                        fn_target_md itself.
                        This is useful when you edit a lot in markdown and don't want
                        clutter from the autogen result in that file.
        Filenames relative to directory of fn_test_file or absolut.

        In this setup function we generate e.g. this as config:
        (Pdb) pp self.ctx (for a run of our own tutorial)
        {'d_assets'         : '/data/root/pytest2md/tests/tutorial/',
        'fn_md'             : '/data/root/pytest2md/tests/tutorial.md',
        'fn_target_md'      : '/data/root/pytest2md/README.md.tmpl',
        'd_test'              : '/data/root/pytest2md/tests',
        'md_sep'            : '<!-- autogen tutorial -->',
        'name'              : 'tutorial',
        'fn_target_md_tmpl' : '/data/root/pytest2md/README.md.tmpl'}
        """

        # contains output for printing python funcs:
        # self.printed = Printed()

        abs = abspath
        self.ctx = C = {}
        C['fn_test_file'] = fnt = abs(fn_test_file)

        # '<!-- autogen... as default:
        C['md_sep'] = md_sep
        C['d_test'] = d_test = DIR(fn_test_file)
        C['d_repo_base'] = d_repo_base(d_test)
        if frontmatter:
            C['frontmatter'] = frontmatter
        C['fn_target_md'] = fn = abs(
            fn_target_md or dflt_target_md(fnt, d_test)
        )

        C['fn_target_md_tmpl'] = find_template(fn, fn_target_md_tmpl)
        # tests/test_foo.py -> name is 'foo'
        C['name'] = name = rpl(fn_test_file.rsplit('/', 1)[-1], 'test_', '.py')
        # conventional:
        C['d_assets'] = d_assets or (d_test + '/assets')

        # the produced markdown:
        C['md'] = []
        # log for all shell actions:
        C['cmd_log'] = []

        # Generator API:
        self.md_from_source_code = partial(md_from_source_code, ctx=C)
        self.md = partial(md, ctx=C)
        self.bash_run = partial(bash_run, ctx=C)

        self.sh_file = partial(sh_file, ctx=C)
        C['env_exports'] = {}
        self.export = partial(export, ctx=C)
        self.export_add = partial(export_add, ctx=C)
        # tools for the functions:
        self.sh_code = partial(sh_code, ctx=C)
        self.as_json = as_json
        self.html_table = html_table
        self.convert_to_staticmethods = convert_to_staticmethods

        # writing API
        self.write_markdown = partial(write_markdown, ctx=C)
        # mdtool access:
        self.src_link_templates = mdtool.known_src_links

        MdInline.bash = partial(
            self.bash_run, cmd_path_from_env=True, md_insert=False
        )
        MdInline.sh_file = partial(self.sh_file, md_insert=False)


def export_add(key, val, ctx, append=False):
    v = os.environ.get(key)
    val = ':'.join((v, val) if append else (val, v))
    return export(key, val, ctx)


def export(key, val, ctx):
    ctx['env_exports'][key] = val
    ctx['cmd_log'].append('export %s="%s"' % (key, val))
    os.environ[key] = val


class MdInline:
    """Funcs which can be supplied inline:
    <bash: ls /etc>
    (further funcs can be set by the user into this)
    """

    pass


class Printed:
    def __init__(self):
        self.stdout = []
        self.stderr = []

    def write(self, *a):
        self.stdout.extend(list(a))


def dflt_target_md(test_file, d_test):
    # assuming tests in <base>/tests:
    return d_test + '/../README.md'


def find_template(fn_target_md, fn_target_md_tmpl):
    """
    templates are good for md source editing, w/o the clutter of the generated.
    fn the name of the final markdown file. Can have a .tmpl.md next to it
    or a file of same name in templates folder next to it"""

    fn, fnt = fn_target_md, fn_target_md_tmpl

    def find(fn):
        fnb = os.path.basename(fn)
        t1 = fn.replace('.md', '.tmpl.md')
        t2 = fn.replace(fnb, '.' + fnb).replace('.md', '.tmpl.md')
        t3 = DIR(fn) + '/templates/%s' % fnb
        for t in (t1, t2, t3):
            if os.path.exists(t):
                return t

    fnt = fnt or find(fn)
    if not fnt:
        print('Replacing content in the final markdown, no template', fn)
    return fnt or fn


def create_empty_md_file(ctx):
    """the work markdown will be in tests/foo.md for test_foo.md"""
    d_test = ctx['d_test']
    # create
    fn_md = ctx['fn_md'] = d_test + '/%(name)s.md' % ctx
    if exists(fn_md):
        os.unlink(fn_md)
    with open(fn_md, 'w') as fd:
        fd.write('')
    return fn_md


# ---------------------------------------------- Markdown Writing API Functions
def write_markdown(
    with_source_ref=False,
    no_link_repl=False,
    make_toc=True,
    make_cmd_log=True,
    no_write=False,
    fn_target_md=None,  # normally in ctx. this is an overwrite possiblity for error handlers
    ctx=None,
):
    """
    adds generated markdown to the destination file
    """
    # just required for 'with_source_ref':
    # src = sys._getframe().f_back.f_code
    if isinstance(ctx['md'], str):
        ctx['md'] = [ctx['md']]

    if make_cmd_log:
        cl = ctx['cmd_log']
        if cl:
            cl = bash('\n'.join(cl))
            d = details(cl, 'Command Summary')
            ctx['md'].append('\n\n%s\n' % d)

    if with_source_ref:
        msg = (
            '*Auto generated by [pytest2md](https://github.com/'
            'axiros/pytest2md), running [%s](%s)'
        )
        # msg = msg % src.co_filename.rsplit('/', 1)[-1]
        fn = ctx['fn_test_file'].replace(ctx['d_repo_base'], '.')
        msg = msg % (fn, fn)
        ctx['md'].append('\n\n%s\n' % msg)

    # we first embed the md into the template:
    fnr = ctx['fn_target_md_tmpl']
    if not exists(fnr):
        readm = ''
    else:
        with open(fnr) as fd:
            readm = fd.read()
    # something like <! autoconf...:
    sep = ctx['md_sep']
    if not sep in readm:
        readm = '\n%s\n%s\n%s\n' % (sep, readm, sep)
    pre, _, post = readm.split(sep, 3)
    ctx['md'] = ''.join(
        (pre, sep, '\n' + '\n'.join(ctx['md']), '\n', sep, post)
    )

    print('Now postprocessing', ctx['fn_target_md'])

    mdt = mdtool.MDTool(
        md=ctx['md'],
        d_repo_base=ctx['d_repo_base'],
        src_link_tmpl_name=os.environ.get('MD_LINKS_FOR'),
    )
    if not no_link_repl:
        ctx['md'], changed = mdt.do_set_links()
        mdt.ctx['md'] = ctx['md']

    if make_toc:
        if not isinstance(make_toc, dict):
            make_toc = {}
        mdt.ctx['md'] = ctx['md'] = mdt.make_toc(**make_toc)
        # mdt.ctx['md'] = ctx['md']
    fm = ctx.get('frontmatter')
    if fm:
        frntmt = json.dumps(fm, indent=4, sort_keys=True)
        md = ctx['md']
        if md.lstrip().startswith('{'):
            md = md.split('\n}\n\n', 1)
            if len(md) == 2:
                md = md[1]
        ctx['md'] = '\n%s\n\n%s' % (frntmt, md)

    if no_write:
        return ctx['md']
    f = ctx['fn_target_md']
    if not exists(dirname(f)):
        # TODO: fix security:
        sp.getoutput('mkdir -p "%s"' % dirname(f))
    with open(fn_target_md or ctx['fn_target_md'], 'w') as fd:
        fd.write(ctx['md'])
    return ctx['md']


# ------------------------------------------- Markdown Generation API Functions


def md(
    paras,
    ctx,
    into=nothing,
    test_func_frame=None,
    summary=None,
    no_sh_func_output=False,
):
    """adds generated markdown into our context"""
    # get a hold on the test function currently executed, to be able, to
    # find and run pyrun <funcfname> statements:
    test_func_frame = test_func_frame or sys._getframe().f_back
    paras = [paras] if not isinstance(paras, list) else paras
    lctx = {}
    lctx['in_code_block'] = False

    paras = [deindent(p) for p in paras]
    parts = paras[0].split('\npyrun: ')
    after = parts.pop(0)
    if parts:
        r = run_pyrun_funcs(
            parts,
            test_func_frame,
            ctx=ctx,
            no_sh_func_output=no_sh_func_output,
        )
        after += r

    paras = [after]

    def repl(l, lctx=lctx, ctx=ctx):
        if '```' in l:
            lctx['in_code_block'] = not lctx['in_code_block']
        ls = l.lstrip()
        if not ls.startswith('<') or not ':' in l:
            return l

        md_inline_cmd, args = ls[1:].split(':', 1)
        # todo: do this via MdInline:
        if md_inline_cmd == 'from_file':
            ff = '<from_file: '
            pre, post = l.split(ff, 1)
            fn, post = post.rsplit('>', 1)
            if not fn.startswith('/'):
                fn = ctx['d_assets'] + fn
            if not exists(fn):
                s = l
            else:
                with open(fn) as fd:
                    s = fd.read().strip()
                if fn.endswith('.py'):
                    s = python(s)
                else:
                    s = code % s
            res = pre + s + post
        else:
            f = getattr(MdInline, md_inline_cmd, None)
            if not f:
                return l
            args = args.strip()[:-1].rstrip()  # remove last '>'
            if not args:
                args = [args]
            elif args[0] in ('{', '['):
                args = json.loads(args)
            elif ',' in args and ':' in args:
                args = args.strip()
                # allow for bash run to omit the cmd prefix:
                if (
                    getattr(getattr(f, 'func', {}), '__name__', None)
                    == 'bash_run'
                ):
                    if not args.startswith('cmd:'):
                        args = 'cmd:' + args
                args = mdtool.to_dict(args)
            else:
                args = [args]
            if isinstance(args, list):
                res = f(*args)
            else:
                res = f(**args)
        return res

    r = '\n'.join([repl(l) for para in paras for l in para.splitlines()])
    r = into(r)
    if summary:
        r = details(r, summary)
    ctx['md'].append(r)


def _bash_run_cmd_structure(c):
    if isinstance(c, str):
        return {'cmd': c, 'res': ''}
    elif isinstance(c, (list, tuple)):
        # run([['ls /etc', 'hosts'], ['ps ax', 'systemd']])
        return {'cmd': c[0], 'res': '', 'assert': c[1]}
    else:
        raise Exception('Err: not support command structure', cmd)


def _bash_run_check_asserts(c, ctx, expect=None):
    ass = c.get('assert') or expect
    if ass is not None:
        if not ass in c['res']:
            dump_cmd_log(ctx)
            raise Exception('Assertion violation in bash_run:', c)


def dump_cmd_log(ctx):
    cl = ctx['cmd_log']
    if not cl:
        return
    cl, fn = '\n'.join(ctx['cmd_log']), '/tmp/p2mcmdlog'
    print('\nCommand log to this point\n', '=' * 80)
    os.system('echo -e "\x1b[1;48;5;245m"')
    print(cl)
    os.system('echo -e "\x1b[0m"')
    print('=' * 80)
    print('Written into', fn)
    with open(fn, 'w') as fd:
        fd.write(cl + '\n')
    os.system('chmod +x "%s"' % fn)
    errmd = '/tmp/md_error_p2m.md'
    print('Writing markdown to this point to ' + errmd)
    try:
        ctx['fn_target_md'] = errmd
        write_markdown(ctx=ctx)
    except Exception as ex:
        print(
            'Failed generating error reporting markdown until point of failure',
            str(ex),
        )


def bash_run(
    cmd,
    res_as=None,
    cmd_path_from_env=True,  # and not from assets
    no_show_in_cmd='',
    summary=None,
    into_file=None,  # output to that file in assets/logs/<into_file>, linked. Only last command logged
    md_insert=True,
    ign_err=False,  # currently only for non into_file commands
    pdb=False,
    expect=None,
    retry_secs=None,  # on failures, retry until now() + this
    ctx=None,
):
    """runs unix commands, then writes results into the markdown"""
    if isinstance(retry_secs, str):
        retry_secs = float(retry_secs)

    if isinstance(cmd, str):
        cmds = [{'cmd': cmd, 'res': ''}]

    elif isinstance(cmd, list):

        cmds = [_bash_run_cmd_structure(c) for c in cmd]

    else:
        cmds = cmd

    orig_cmd = cmds[0]['cmd']
    if not res_as and orig_cmd.startswith('python -c'):
        res_as = python
    d_ass = ctx['d_assets']
    into_file_res = []
    if into_file:
        dl = d_ass + '/bash_run_outputs'
        if not exists(dl):
            os.system('mkdir -p "%s"' % dl)
        fn_into = dl + '/%s' % into_file

    for c in cmds:
        cmd = c['cmd']
        fncmd = cmd if cmd_path_from_env else (d_ass + '/' + cmd)
        ctx['cmd_log'].append(fncmd)
        # run it:
        if str(pdb).lower() not in ('none', 'false', '0'):
            print('pdb is set -> requested break')
            print('locals at bash_run:')
            print(json.dumps(locals(), indent=2, sort_keys=True, default=str))
            breakpoint()

        if into_file:
            if into_file.endswith('.html'):
                _ = fncmd + ' 2>&1 | ansi2html > "%s"' % fn_into
            else:
                _ = fncmd + '> "%s" 2>&1' % fn_into
            # don't generate output which would be shown in the markdown
            # this is for the user running the tests, so that he can tail
            # the file for long running commands:
            print('Running', _, '...')
            sp.Popen(_, shell=True).communicate()

        else:
            if fncmd.strip().endswith('&'):
                exitc, res = os.system(fncmd), '(backgrounded)'
            else:
                t0 = time.time()
                while True:
                    exitc, res = sp.getstatusoutput(fncmd)
                    if expect and retry_secs and time.time() - t0 < retry_secs:
                        if expect in res:
                            break
                        print('Retrying %s' % fncmd)
                        time.sleep(0.2)
                        continue
                    break

            c['exitcode'], c['res'] = exitc, res

            if not ign_err and exitc:
                dump_cmd_log(ctx)
                raise Exception('Command run error: %s %s' % (fncmd, res))

        if no_show_in_cmd:
            fncmd = fncmd.replace(no_show_in_cmd, '')
        # .// -> when there is cmd_path_from_env we would get that, ugly:
        # this is just for md output, not part of testing:
        c['cmd'] = fncmd.replace(d_ass, './').strip().replace('.//', './')
        if into_file:
            if not into_file.endswith('.html'):
                # just a few lines, rest in log:
                msg = '\n...(output truncated - see link below)\n'
                with os.popen('head -n 5 "%s"' % fn_into) as fd:
                    c['res'] = fd.read() + msg
            fn = fn_into.replace(ctx['d_repo_base'], '.')
            into_file_res.append([c['cmd'], fn])

    r = '\n\n'.join(['$ %(cmd)s\n%(res)s' % c for c in cmds])
    [_bash_run_check_asserts(c, ctx, expect=expect) for c in cmds]
    into = res_as if res_as else bash
    # when we have an inline func we want the content only:
    if not md_insert:
        r = into(r)
        if summary:
            r = details(r, summary)
        return r
    else:
        md(r, into=into, summary=summary, ctx=ctx)

    # show links of the output logs:
    for cmd, fn in into_file_res:
        if fn.endswith('.html'):
            md('\n[%s](%s)\n\n' % (cmd, fn), ctx=ctx)
        else:
            md('- [Output](%s) of `%s`  \n\n' % (fn, cmd), ctx=ctx)
    return cmds


import shutil


def sh_file(
    fn,
    lang='python',
    content=None,
    summary=None,
    as_link=None,
    ctx=None,
    md_insert=True,
):
    ex = exists(fn)
    if not ex and not content:
        raise Exception('not found', fn)
    dn = dirname(fn)
    if not exists(dn):
        os.system('mkdir -p "%s"' % dn)
    if content:
        with open(fn, 'w') as fd:
            fd.write(content)
    else:
        with open(fn) as fd:
            content = fd.read()
    FN = abspath(fn).rsplit('/', 1)[1]
    content = ('$ cat "%s"' % FN) + '\n' + content
    content = as_lang(content, lang)
    if summary:
        content = details(content, summary)
    if as_link:
        d_ass = ctx['d_assets']
        dl = d_ass + '/sh_files'
        if not exists(dl):
            os.system('mkdir -p "%s"' % dl)
        fn_into = dl + '/%s' % FN
        shutil.copyfile(fn, fn_into)
        n = FN if as_link == True else as_link
        fn = fn_into.replace(ctx['d_repo_base'], '.')
        content = '\n[%s](%s)\n' % (n, fn)
    if md_insert:
        md(content, ctx=ctx)
    return content


def sh_code(func, ctx=None):
    return md(python(inspect.getsource(func)), ctx=ctx)


_print_redir_lock = threading.RLock()


def run_pyrun_funcs(blocks, test_func_frame, ctx, no_sh_func_output=False):
    r = []
    printed = Printed()
    for b in blocks:
        func_name = b.split('\n', 1)[0].strip()
        func = test_func_frame.f_locals[func_name]
        s = inspect.getsource(func).split('\n', 1)[1]
        s = deindent(s).lstrip() + '\n'
        # if the function is called outside (to test asserttions) then it'll end
        # with a return - we omit that, if the user wants the reader to see the
        # assertion he should put it inside the func:
        pre, last = s.rsplit('\n', 1)
        if last.lstrip().startswith('return '):
            s = pre
        # wrap into python code block:
        s = python(s.strip())
        with _print_redir_lock:
            del printed.stdout[:]  # py2, no clear
            del printed.stderr[:]  # py2, no clear
            try:
                o = sys.stdout
                e = sys.stderr
                if not 'breakpoint' in s:
                    sys.stdout = printed
                    sys.stderr = printed
                func()
            finally:
                sys.stdout = o
                sys.stderr = e
        if not no_sh_func_output:
            so = ''.join(printed.stdout)
            if so:
                if so.startswith('MARKDOWN:'):
                    so = so.replace('MARKDOWN:', '\n')
                elif not so.lstrip().startswith('```'):
                    so = '\nOutput:\n\n```\n' + so.rstrip() + '\n```'
                # we should to the user as test output:
                # not only bury into markdown
                if not 'breakpoint' in s:
                    print(so)
                s += so
        r.append(s)
    return '\n'.join(r)


def _is_outer_func_def(line):
    return line.startswith('def ') and line.split('#', 1)[0].strip().endswith(
        ':'
    )


def md_from_source_code(ctx, pre_md='', no_sh_func_output=False, repl=None):
    """Called from within test func blocks. Just a convience wrapper around
    adding 'pyrun: <funcname>' on every func to be run - we run all defined.
    We run the functions one by one and replace their source within.
    then hand over to the .md function:

    repl is a simple pre parse replacement dict.
    """
    test_func_frame = sys._getframe().f_back
    # removes the test function itself and de-indents the text block:
    mdsrc = dedent(inspect.getsource(test_func_frame.f_code).split(':', 1)[1])
    if repl:
        for k, v in repl.items():
            mdsrc = mdsrc.replace(k, v)
    lines = mdsrc.splitlines()
    # find text versus code lines:
    r = ['', pre_md] if pre_md else []

    while lines:
        orig_line = lines.pop(0)
        line = orig_line.strip()
        # the conversion instruction has to be at the end:
        if 'md_from_source_code(' in line:
            break
        if not line:
            r.append(line)
            continue
        if line[:3] in ('"""', "'''"):
            sep = line[:3]
            if len(line) > 3:
                r.append(line[3:])
            while lines:
                line = lines.pop(0)
                if line.endswith(sep):
                    if len(line) > 3:
                        r.append(line[:-3])
                    r[-1] += '  '  # md line sep
                    break
                else:
                    r.append(line)
            continue
        if orig_line[0] in ('"', "'"):
            r.append(line[1:-1] + '  ')  # md line sep
            continue

        # code lines - we put not into the markdown -except functions, which we'll run.
        if _is_outer_func_def(orig_line):
            # there are no args
            func_name = line[4:].split('(', 1)[0]
            # a simple name is enough, since the source code is in the locals
            # our test func, under the key of its name:
            r.append(
                run_pyrun_funcs(
                    [func_name],
                    test_func_frame,
                    ctx,
                    no_sh_func_output=no_sh_func_output,
                )
            )
            while lines:
                # remove all source code:
                if lines[0].startswith(' ') or not lines[0]:
                    lines.pop(0)
                else:
                    # one \n at the end:
                    r.append('')
                    break
    return md(
        '\n'.join(r),
        ctx,
        test_func_frame=test_func_frame,
        no_sh_func_output=no_sh_func_output,
    )


def as_json(d):
    if not isinstance(d, str):
        d = json.dumps(d, sort_keys=True, default=str, indent=4)
    return 'MARKDOWN:\n```javascript\n%s\n```' % d


# *headers is not py2 compatible :-(
def html_table(list, headers, summary=None):
    """ A tool which test pythons' may use to format their func results"""
    p = '</td><td>'
    row = lambda r: '<tr><td>' + r + '</td></tr>'
    r = (row(p.join(headers)),)
    for l in list:
        r += (row(p.join([str(s) for s in l])),)
    r = '<table>\n' + '\n'.join(r) + '\n</table>'
    if summary:
        r = details(r, summary)
    return 'MARKDOWN:\n' + r


def convert_to_staticmethods(cls):
    """Helper for Py2 - in docu we often use classes as namespaces"""
    meths = [(k, getattr(cls, k)) for k in dir(cls)]
    c = callable
    meths = [(k, meth) for k, meth in meths if k[:2] != '__' and c(meth)]
    [setattr(cls, k, staticmethod(f.__func__ if PY2 else f)) for k, f in meths]


class util:
    @staticmethod
    def wait_for_port(port, host='localhost', timeout=5.0):
        """
        Utility:
        Wait until a port starts accepting TCP connections.
        Args:
            port (int): Port number.
            host (str): Host address on which the port should exist.
            timeout (float): In seconds. How long to wait before raising errors.
        Raises:
            TimeoutError: The port isn't accepting connection after time specified in `timeout`.
        """
        start_time = time.perf_counter()
        while True:
            try:
                with socket.create_connection((host, port), timeout=0.1):
                    break
            except OSError as ex:
                time.sleep(0.03)
                if time.perf_counter() - start_time >= timeout:
                    raise TimeoutError(
                        'Waited too long for the port {} on host {} to start accepting '
                        'connections.'.format(port, host)
                    )  # from ex


# .
