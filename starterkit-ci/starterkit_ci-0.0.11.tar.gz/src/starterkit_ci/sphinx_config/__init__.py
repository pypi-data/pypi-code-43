import os
from os.path import dirname, join

from recommonmark.transform import AutoStructify

from . import panels
from . import fix_markdown_file_downloads


extensions = [
    'sphinx_rtd_theme',
    'recommonmark',
    'sphinx.ext.mathjax',
    'nbsphinx',
]

templates_path = [
    '_templates',
]

html_theme = 'sphinx_rtd_theme'
html_show_sourcelink = True
html_theme_options = {
    'collapse_navigation': False,
}

exclude_patterns = [
    '**.ipynb_checkpoints',
]

html_context = {
    'display_github': True,
    'github_user': 'lhcb',
    'github_repo': 'starterkit-lessons',
    'github_version': 'master',
    'conf_py_path': '/source/',
}
highlight_language = 'none'

html_static_path = [
    f'{dirname(__file__)}/_static',
]

linkcheck_ignore = [
    # Expect certificate errors
    r'https://lhcb-portal-dirac\.cern\.ch/DIRAC/',
    r'https://lhcb-nightlies\.cern\.ch.*',
    # 404 if not logged in
    r'https://gitlab\.cern\.ch/.*/merge_requests/new',
    # Anchors to specific lines are generated with Javascript
    r'https://gitlab\.cern\.ch/lhcb/Stripping/blob/.*',
    # Seems to be unreliable?
    r'http://pdg.*\.lbl\.gov/.*',
    # FIXME: The URLs have changed
    r'https://research\.cs\.wisc\.edu/htcondor/.*',
]
linkcheck_workers = 32

starterkit_ci_redirects = {}


def setup(app):
    app.add_config_value('recommonmark_config', {
        # 'url_resolver': lambda url: 'http://0.0.0.0/' + url,
        'auto_toc_tree_section': 'Contents',
        'enable_math': True,
        'enable_inline_math': True,
        'enable_eval_rst': True,
    }, True)
    app.add_transform(AutoStructify)
    fix_markdown_file_downloads.configure_app(app)
    panels.configure_app(app)
    for extra_setup_func in setup.extra_setup_funcs:
        extra_setup_func(app)

    # Create redirects
    for origin, target in starterkit_ci_redirects.items():
        # import pdb
        # pdb.set_trace()
        origin = join(app.outdir, origin)
        print('Creating redirect from', origin, 'to', target)
        os.makedirs(dirname(origin), exist_ok=True)
        with open(origin, 'wt') as fp:
            fp.write(f'<meta http-equiv="refresh" content="0; url={target}">\n')
            fp.write(f'<link rel="canonical" href="{target}" />\n')


# Allow additional setup functions to be defined in projects
setup.extra_setup_funcs = []
