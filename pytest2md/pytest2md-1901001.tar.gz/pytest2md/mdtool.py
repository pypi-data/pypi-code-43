"""
Postprocessing the Markdown for various Hosting Ways
"""

from pytest2md.repo_search import search_repo, os_run
from functools import partial
import fnmatch
import json
import time
import sys
import os

# replacer for shortcut curls, which can be themselves replaced by the build
# static is just a static webserver:
known_src_links = {
    'github': (
        'https://github.com/%(gh_repo_name)s/blob/%(git_rev)s/'
        '%(path)s%(line:#L%s)s'
    ),
    'github_raw': (
        'https://raw.githubusercontent.com/%(gh_repo_name)s/'
        '%(git_rev)s/%(path)s%(line:#L%s)s'
    ),
    'static': 'file://%(d_repo_base)s/%(path)s',
}
known_src_links['static_raw'] = known_src_links['static']


def info(msg, **kw):
    print(msg, kw)


valid_file = lambda f: False if f.endswith('.pyc') else True
valid_dir = lambda d: False if (d[0] in ('.', '_') or '.egg' in d) else True


def find_file(pattern, path, match=fnmatch.fnmatch):
    result = []
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if valid_dir(d)]
        for name in files:
            if valid_file(name):
                if match(name, pattern):
                    result.append(os.path.join(root, name))
    return result


class InitData:
    """
    This is delivering values for keys in src_links which are not determinable
    from the markdown itself but from e.g. looking into our git config.

    Example: gh_repo_name is part of the links for github.

    All keys used in the source link templates in 'known_src_links' must be
    having a method here to find them, unless they can be delivered from the
    markdown itself..

    Todo: extend for bitbucket..., custom"""

    @staticmethod
    def d_repo_base(ctx):
        return ctx['d_repo_base']

    @staticmethod
    def gh_repo_name(ctx):
        r = os.popen('cd "%s"; git remote -v' % ctx['d_repo_base']).read()
        r = [l for l in r.splitlines() if 'github.com' in l and 'push' in l]
        if not r:
            raise Exception('No github push remote found. remotes=%s' % str(r))
        r = r[0].split('github.com', 1)[1].rsplit('.git', 1)[-2]
        if r[0] in ('/', ':'):
            r = r[1:]
        return r

    @staticmethod
    def git_rev(ctx):
        r = os.popen('cd "%(d_repo_base)s"; git rev-parse HEAD' % ctx).read()
        return r.strip()


class ItemGetter:
    def __init__(self, ctx):
        # this is a copy of the main context:
        self.ctx = ctx

    def __getitem__(self, k, d=None):
        c = self.ctx
        v = c.get(k, None)
        if v:
            return v
        # %(line:#L%s)s
        if ':' in k and '%s' in k:
            k1, r = k.split(':', 1)
            if k1 in c:
                return r % c.get(k1)
        return ''


class CommitSearchStringLookup:
    """Handles {..} statements in git commits, replaces with links"""

    links = {}
    match_lines = {}

    def __init__(self, mdt):
        self.mdt = mdt

    def __getitem__(self, k):
        # we re-use the main markdown []<SRC> link replacer.
        # it will record all link refs in its .links
        # we keep them in the changlog, they have the versions,
        # might be different / lost in future revisions:
        if len(k) < 5:
            return k  # too wide
        if len(k.split('.')[-1]) < 6:
            # this is a file, we search directly and link fully:
            tit, lnk = self.mdt.build_src_link(k)
            self.links[tit] = self.mdt.links[lnk]
        else:
            # this is a match string
            res = search_repo(k, repo_dir=self.mdt.d_repo_base)
            self.match_lines[k] = res
            return '<details><summary>%s</summary></details>' % k
        return '[%s][%s]' % (tit, lnk)


class ChangeLogWriter:
    """
    This does not try to attempt to build at every pytest run for the
    whole history - but loads the last changelog written and just builds
    the offset by time
    If the user wants to rebuild then he has to remove .changelog.json.

    In turn for this inconvenience we offer efficient matching w/o even
    giving file paths, just substring matches.
    """

    prefixes = {'N': 'New', 'F': 'Fix', 'T': 'Task'}

    def make_changelog(self, change_log, md):
        # this would screw up the changelog
        if os.environ.get('NOLINKREPL'):
            info('Not replacing links -> no changelog', environ='NOLINKREPL')
            return
        try:
            here = os.getcwd()
            os.chdir(self.d_repo_base)
            return self._make_changelog(change_log, md)
        finally:
            os.chdir(here)

    def _make_changelog(self, change_log, md):
        """
        cl stores per entry:
        {'rev' : <long rev>
         'ts'  : unixtime of writing the cl
         'type': <F|B>
         'msg' : commit messge for that feature or bug
         }
        """
        cl = change_log
        fn = self.d_repo_base + '/.changelog.json'
        if os.path.exists(fn):
            have = json.loads(fn.read())
        else:
            have = {}
        last_ts = 1
        for k in self.prefixes.values():
            l = have.get(k)
            last_ts = max(l[-1].get('ts', 0) if l else 1, last_ts)

        # get all since then:
        lines = os_run(
            # 1000000 = year 2001:
            'git log --since %s'
            % (last_ts if last_ts > 1 else 1000000000)
        )
        lines = lines.splitlines()

        def find_refs(line):
            if '{' in line and '}' in line:
                line = line.replace('{', '%(').replace('}', ')s')
                line = line % CommitSearchStringLookup(self)
            return line

        def add_line(l, m):
            tags = self.prefixes.values()
            r = {'msg': find_refs(l), 'ts': int(time.time())}
            for k in m:
                if not k in tags:
                    r[k] = m[k]
            return r

        def add_new(m, have=have):
            if not m:
                return
            for k, v in self.prefixes.items():
                lines = m.get(v)
                if lines:
                    for l in lines:
                        have.setdefault(v, []).append(add_line(l, m))

        m = {}
        while lines:
            line = lines.pop(0)
            ls = line.strip()
            if not ls:
                continue
            if line.startswith('commit '):
                add_new(m)
                m = {}
                m['rev'] = line.split(' ')[1]
                continue
            for k in 'Author:', 'Date:':
                if line.startswith(k):
                    m[k.lower()[:-1]] = ls.split(k)[1].lstrip()
                    break
            for k in self.prefixes:
                if ls.startswith(k + ' ') and line.startswith('  '):
                    kl = self.prefixes[k]
                    n = m.setdefault(kl, []).append(ls[2:])
                    break

        breakpoint()
        # have.setdefault('zrefs', {})[

        if 'details' in change_log:
            '''
            change_log = (
                """
            <details>
            <summary>Change Log (click to expand)</summary>
                %s
            </details>

                % change_log
            )
        if not 'details' in cl or 'header' in cl:
            change_log = '# Change Log\n\n' + change_log
        if not 'bottom' in cl:
            md = '# Changelog\n%s\n' % change_log
            '''


class MDTool(ChangeLogWriter):
    """
    Created when P2M is done with the tutorial markdowns and wants
    to integrate into the main readme
    """

    def __init__(self, md, d_repo_base, src_link_tmpl_name=None):
        C = self.ctx = {
            'md': md,
            'links': {},
            'links_log': [],
            'd_repo_base': d_repo_base,
            'autogen_links_sep': '\n\n<!-- autogenlinks -->\n',
            'src_link_tmpl_name': src_link_tmpl_name,
        }
        C['d_repo_base'] = d_repo_base

        if not C['src_link_tmpl_name']:
            # try to find from within the md itself:
            md = md.split('<!-- md_links_for:')
            if len(md) > 1:
                C['src_link_tmpl_name'] = md[1].split('--', 1)[0].strip()

        C['src_link_tmpl_name'] = C['src_link_tmpl_name'] or 'static'
        print(
            'Rendering links - using source links template:',
            src_link_tmpl_name,
        )
        if 1 or not os.environ.get('NOLINKREPL'):
            init_src_link_tmpl(ctx=C)

        self.do_set_links = partial(do_set_links, ctx=C)
        self.make_toc = partial(make_toc, ctx=C)


def init_src_link_tmpl(ctx):
    """doing all we only have to do once"""

    # mdt.src_link_tmpl = 'github'
    # replace given by name with the lookup result from teh known..dict:
    name, as_dict = ctx['src_link_tmpl_name'], {}
    if ':' in name:
        # the environ tells us we should not consider
        as_dict = to_dict(name)
        name = as_dict['name']

    ctx['src_link_tmpl'] = sl = known_src_links[name]
    ctx['src_link_tmpl_raw'] = known_src_links[name + '_raw']

    if not '/' in sl:
        raise Exception('Not supported', ctx['src_link_tmpl'])
    for k in [l for l in dir(InitData) if not l.startswith('_')]:
        if k in sl:
            # adding git revision to link rednering context
            # k e.g. gh_repo_name
            # this will only work with repos, if not given in as_dict:
            # runs git remote -v
            ctx[k] = as_dict.get(k) or getattr(InitData, k)(ctx)


def do_set_links(ctx):
    """
    Link replacer.
    Rewrites `[k1:v1,k2:v2,...]<SRC>` by replacing k1, k2,... in
    `src_link_tmpl` keys with given values.

    Example: All the values here have to be replaced so that the link
    is working:

        https://github.com/%(gh_repo_name)s/blob/%(git_rev)s/'
        '%(path)s%(line:#L%s)s'

    if a key is not in context the replacement is empty string (e.g. line)

    Replacement can be 1 level nested: [line:#L%s] resolves e.g. to '#L42'
    if line is present else to ''

    Special keys:
    - title: Will become the link text
    - d_repo_base: From App, for pytest the folder of the pytested file.
    - path: file path relative to d_repo_base
    - fmatch: Startswith pattern of file name in dir. Must match uniquely.
        also builds if not present:
        - path
        - title
    - lmatch: Contains match within a file
        also builds if not present:
        - line
    - gh_repo_name, git_rev: determined once at startup

    Trivial format [foo]<SRC> is ident to [fmatch:foo]<SRC>

    """
    if os.environ.get('NO_LINK_REPL'):
        info('Not replacing links', environ='NO_LINK_REPL')
        return
    # mdt.autogen_links_sep is the page bottom links start tag:
    # '\n\n<!-- autogenlinks -->\n'
    md = mdorig = ctx['md'].split(ctx['autogen_links_sep'], 1)[0]
    if '\n```' in md:
        mdparts = md.split('\n```')
    else:
        mdparts = [md]
    r = []
    while mdparts:
        md, fenced_code = mdparts.pop(0), None
        if mdparts:
            fenced_code = mdparts.pop(0)
        parts = md.split(']<SRC>')
        ri = []
        while parts[:-1]:
            part = parts.pop(0)
            if not '[' in part:
                ri.append(part)
                continue
            pre, lnk = part.rsplit('[', 1)
            title, link = build_src_link(ctx, lnk)  # <--------------- !

            if title != None:
                ri.append('%s[%s][%s]' % (pre, title, link))
            else:
                ri.append(part)
        assert len(parts) == 1
        ri.append(parts[0])
        r.append(''.join(ri))
        if fenced_code:
            r.append(fenced_code)
    mdr = '\n```'.join(r)
    links = ctx['links']
    if links:
        mdr += ctx['autogen_links_sep']
        for l in sorted(links.keys()):
            mdr += '[%s]: %s\n' % (l, links[l])

    return mdr, mdr != mdorig


def build_src_link(ctx, lnk):
    """
    Adds to the ctx['links']

    lnk the stuff in [] of a statement like
    [title:foo,fmatch:Readme]<SRC>

    """
    ll = lambda msg, **kw: ctx['links_log'].append([msg, kw])
    # build ld: link dict, {'title', 'file', evtl. lineof...}"""
    if ':' in lnk or ',' in lnk:
        try:
            ld = to_dict(lnk)  # link dict
        except:
            ll('Wrong format', link=lnk)
            return None, None
    else:
        ld = {'title': lnk, 'fmatch': lnk}

    ld['title'] = ld.get('title', ld.get('fmatch', lnk))

    title = ld['title']
    raw = ld.pop('show_raw', 0)
    if raw:
        tmpl = ctx['src_link_tmpl_raw']
    else:
        tmpl = ctx['src_link_tmpl']

    # tmpl is the source link template, usually containing /%(path)s/
    dirmatch = ld.get('dirmatch')
    if '%(path' in tmpl and not 'path' in ld:
        path = find_path(ld, bd=ctx['d_repo_base'], dirmatch=dirmatch)
        if not path:
            ll('Path not found', **ld)
            return None, None
        ld['path'] = path

    ld['file'] = ld.get('file', ld.get('path', '').rsplit('/', 1)[-1])
    ld['fullpath'] = fn = os.path.join(ctx['d_repo_base'], ld['path'])

    if '%(line' in tmpl and not 'line' in ld:
        if 'lmatch' in ld:
            match = ld['lmatch']
            with open(fn, 'r') as fd:
                for (i, line) in enumerate(fd):
                    if match in line:
                        ld['line'] = str(i)
                        break

    link = ld['file']
    if ld.get('line'):
        link += '#%(line)s' % ld
    single_ctx = dict(ctx)
    single_ctx.update(ld)
    target = tmpl % ItemGetter(single_ctx)
    while ctx['links'].get(link) != target:
        if ctx['links'].get(link) == None:
            break
        # collision - add underscores
        link += '_'
    ctx['links'][link] = target
    ll('Replaced', frm=lnk, link=link, to=target)
    return title, link


def make_toc(ctx, add_change_log=None, **kw):
    """making a table of content, replacing "[TOC]" -else at the beginning"""
    from pytest2md import strutils

    md = ctx['md']

    # this allows to jump back to the toc:
    back_ref_id = 0
    tsep = t = '\n<!-- TOC -->\n'
    if not t in md:
        md = md.replace('\n[TOC]\n', t + t)
    if not t in md:
        md = t + t + md
    pre, toc, md = md.split(t)
    if add_change_log and 0:
        # not yet supported
        md = mdt.make_changelog(add_change_log, md)

    lines = md.splitlines()
    toc = ['']
    r = []
    while lines:
        line = lines.pop(0)
        r.append(line)
        if line.startswith('```'):
            while lines:
                r.append(lines.pop(0))
                if r[-1].startswith('```'):
                    break
        if line.startswith('    '):
            while lines and lines[0].startswith('    '):
                r.append(lines.pop(0))

        if line.startswith('#'):
            back_ref_id += 1
            lev, h = line.split(' ', 1)
            toc.append(
                '    ' * (len(lev) - 1)
                + '- <a name="toc%s"></a>[%s](#%s)'
                % (back_ref_id, h, strutils.slugify(h, delim='-'))
            )
            r.pop()
            r.append('%s <a href="#toc%s">%s</a>' % (lev, back_ref_id, h))
    toc.append('')
    res = (
        pre
        + tsep
        + '\n# Table Of Contents\n'
        + '\n'.join(toc)
        + tsep
        + '\n'.join(r)
    )
    return res


def find_path(ld, bd, dirmatch=None):
    """
    link dict, base dir
    dirmatch is a "contains" filter for found matches.
    """
    file = ld.get('fmatch')
    if not file:
        return
    found = find_file(file + '*', bd)
    if len(found) == 0:
        print('Not found', file, 'from', ld, 'builddir', bd)
        return
    elif len(found) > 1:
        if dirmatch:
            found = [f for f in found if dirmatch in f]
        # take shortest path to match:
        cur = found[0]
        for l in found[1:]:
            if len(l) < len(cur):
                cur = l
        found = [cur]
        # found = [f for f in found if f.rsplit('/', 1)[-1] == file]
        # if len(found) != 1:
        #    return
        # info('No unique source link found')
    if len(found) == 1:
        return found[0][len(bd) + 1 :]


def to_dict(s):
    l = [kv.strip().split(':', 1) for kv in s.split(',')]
    try:
        return dict([(k.strip(), v.strip()) for k, v in l])
    except Exception as ex:
        ms = 'Trying to parse "%s" into a key value dict:' % s
        raise Exception('%s - %s' % (ms, ex))
