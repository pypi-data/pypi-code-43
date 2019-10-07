import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'pyven',
        version = '7',
        description = 'Management of PYTHONPATH for simultaneous dev of multiple projects',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/pyven',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['gclean', 'tasks', 'release', 'runtests', 'travis_ci', 'pyven', 'toplevel', 'tests'],
        install_requires = ['aridity'],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = ['gclean.py', 'tasks.py', 'pyven', 'release.py', 'runtests.py', 'travis_ci.py', 'pyven.py', 'toplevel.py', 'tests', 'foreignsyms'])
