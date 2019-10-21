from __future__ import print_function
from __future__ import unicode_literals

import argparse
import contextlib
import copy
import io
import os
import pipes
import shutil
import stat
import subprocess
import sys
import tempfile

from setuptools.command.build_ext import build_ext as _build_ext


@contextlib.contextmanager
def _tmpdir():
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        def err(action, name, exc):  # pragma: no cover (windows)
            """windows: can't remove readonly files, make them writeable!"""
            os.chmod(name, stat.S_IWRITE)
            action(name)

        shutil.rmtree(tempdir, onerror=err)


def _get_cflags(compiler):
    return str(' ').join(str('-I{}').format(p) for p in compiler.include_dirs)


LFLAG_CLANG = '-Wl,-undefined,dynamic_lookup'
LFLAG_GCC = '-Wl,--unresolved-symbols=ignore-all'
LFLAGS = (LFLAG_CLANG, LFLAG_GCC)


def _get_ldflags():
    """Determine the correct link flags.  This attempts dummy compiles similar
    to how autotools does feature detection.
    """
    # windows gcc does not support linking with unresolved symbols
    if sys.platform == 'win32':  # pragma: no cover (windows)
        prefix = getattr(sys, 'real_prefix', sys.prefix)
        libs = os.path.join(prefix, str('libs'))
        return str('-L{} -lpython{}{}').format(libs, *sys.version_info[:2])

    cc = subprocess.check_output(('go', 'env', 'CC')).decode('UTF-8').strip()

    with _tmpdir() as tmpdir:
        testf = os.path.join(tmpdir, 'test.c')
        with io.open(testf, 'w') as f:
            f.write('int f(int); int main(void) { return f(0); }\n')

        for lflag in LFLAGS:  # pragma: no cover (platform specific)
            try:
                subprocess.check_call((cc, testf, lflag), cwd=tmpdir)
                return lflag
            except subprocess.CalledProcessError:
                pass
        else:  # pragma: no cover (platform specific)
            # wellp, none of them worked, fall back to gcc and they'll get a
            # hopefully reasonable error message
            return LFLAG_GCC


def _check_call(cmd, cwd, env):
    envparts = [
        '{}={}'.format(k, pipes.quote(v))
        for k, v in sorted(tuple(env.items()))
    ]
    print(
        '$ {}'.format(' '.join(envparts + [pipes.quote(p) for p in cmd])),
        file=sys.stderr,
    )
    subprocess.check_call(cmd, cwd=cwd, env=dict(os.environ, **env))


def _get_build_extension_method(base, root):
    def build_extension(self, ext):
        def _raise_error(msg):
            raise IOError(
                'Error building extension `{}`: '.format(ext.name) + msg,
            )

        # If there are no .go files then the parent should handle this
        if not any(source.endswith('.go') for source in ext.sources):
            # the base class may mutate `self.compiler`
            compiler = copy.deepcopy(self.compiler)
            self.compiler, compiler = compiler, self.compiler
            try:
                return base.build_extension(self, ext)
            finally:
                self.compiler, compiler = compiler, self.compiler

        if len(ext.sources) != 1:
            _raise_error(
                'sources must be a single file in the `main` package.\n'
                'Recieved: {!r}'.format(ext.sources)
            )

        main_file, = ext.sources
        if not os.path.exists(main_file):
            _raise_error('{} does not exist'.format(main_file))
        main_dir = os.path.dirname(main_file)

        # Copy the package into a temporary GOPATH environment
        with _tmpdir() as tempdir:
            root_path = os.path.join(tempdir, 'src', root)
            # Make everything but the last directory (copytree interface)
            os.makedirs(os.path.dirname(root_path))
            shutil.copytree('.', root_path, symlinks=True)
            pkg_path = os.path.join(root_path, main_dir)

            env = {str('GOPATH'): tempdir}
            cmd_get = ('go', 'get', '-d')
            _check_call(cmd_get, cwd=pkg_path, env=env)

            env.update({
                str('CGO_CFLAGS'): _get_cflags(self.compiler),
                str('CGO_LDFLAGS'): _get_ldflags(),
            })
            cmd_build = (
                'go', 'build', '-buildmode=c-shared',
                '-o', os.path.abspath(self.get_ext_fullpath(ext.name)),
            )
            _check_call(cmd_build, cwd=pkg_path, env=env)

    return build_extension


def _get_build_ext_cls(base, root):
    class build_ext(base):
        build_extension = _get_build_extension_method(base, root)

    return build_ext


def set_build_ext(dist, attr, value):
    root = value['root']
    base = dist.cmdclass.get('build_ext', _build_ext)
    dist.cmdclass['build_ext'] = _get_build_ext_cls(base, root)


GOLANG = 'https://storage.googleapis.com/golang/go{}.linux-amd64.tar.gz'
SCRIPT = '''\
cd /tmp
curl {golang} --silent --location | tar -xz
export PATH="/tmp/go/bin:$PATH" HOME=/tmp
for py in {pythons}; do
    "/opt/python/$py/bin/pip" wheel --no-deps --wheel-dir /tmp /dist/*.tar.gz
done
ls *.whl | xargs -n1 --verbose auditwheel repair --wheel-dir /dist
ls -al /dist
'''


def build_manylinux_wheels(argv=None):  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--golang', default='1.12',
        help='Override golang version (default %(default)s)',
    )
    parser.add_argument(
        '--pythons', default='cp27-cp27mu,cp36-cp36m,cp37-cp37m,cp38-cp38',
        help='Override pythons to build (default %(default)s)',
    )
    args = parser.parse_args(argv)

    golang = GOLANG.format(args.golang)
    pythons = ' '.join(args.pythons.split(','))

    assert os.path.exists('setup.py')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    os.makedirs('dist')
    _check_call(('python', 'setup.py', 'sdist'), cwd='.', env={})
    _check_call(
        (
            'docker', 'run', '--rm',
            '--volume', '{}:/dist:rw'.format(os.path.abspath('dist')),
            '--user', '{}:{}'.format(os.getuid(), os.getgid()),
            'quay.io/pypa/manylinux1_x86_64:latest',
            'bash', '-o', 'pipefail', '-euxc',
            SCRIPT.format(golang=golang, pythons=pythons),
        ),
        cwd='.', env={},
    )
    print('*' * 79)
    print('Your wheels have been built into ./dist')
    print('*' * 79)
