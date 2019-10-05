author = 'decentral1se'
copyright = '2019, decentral1se'
html_static_path = ['_static']
html_theme = 'alabaster'
master_doc = 'index'
project = 'hypercore-crypto'
templates_path = ['_templates']
extensions = ['sphinx.ext.autodoc', 'sphinx_autodoc_typehints']
autodoc_mock_imports = ['pysodium']  # no libsodium in the RTD environment
