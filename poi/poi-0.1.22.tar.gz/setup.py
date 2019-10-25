# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['poi', 'poi.visitors']

package_data = \
{'': ['*']}

install_requires = \
['xlsxwriter>=1.1,<2.0']

setup_kwargs = {
    'name': 'poi',
    'version': '0.1.22',
    'description': 'Write Excel XLSX declaratively.',
    'long_description': '# Poi: Make creating Excel XLSX files fun again.\n\n![travis](https://travis-ci.org/baoshishu/poi.svg?branch=master)\n\nPoi helps you write Excel sheet in a declarative way, ensuring you have a better Excel writing experience.\n\nIt only supports Python 3.7+.\n\n## Quick start\n\nCreate a sheet object and write to a file.\n\n```python\nfrom poi import Sheet\nsheet = Sheet(\n    root=Col(\n        colspan=8,\n        children=[\n            Row(\n                children=[\n                    Cell(\n                        "hello",\n                        offset=2,\n                        grow=True,\n                        bg_color="yellow",\n                        align="center",\n                        border=1,\n                    )\n                ]\n            ),\n        ],\n    )\n)\nsheet.write(\'hello.xlsx\')\n```\n\nSee, it\'s pretty simple and clear.\n\nSample for rendering a simple table.\n\n```python\nclass Record(NamedTuple):\n    name: str\n    desc: str\n    remark: str\n\ndata = [\n    Record(name=f"name {i}", desc=f"desc {i}", remark=f"remark {i}")\n    for i in range(3)\n]\ncolumns = [("name", "名称"), ("desc", "描述"), ("remark", "备注")]\nsheet = Sheet(\n    root=Table(\n        data=data,\n        columns=columns,\n        cell_width=20,\n        cell_style={\n            "bg_color: yellow": lambda record, col: col.attr == "name"\n            and record.name == "name 1"\n        },\n        date_format="yyyy-mm-dd",\n        align="center",\n        border=1,\n    )\n)\nsheet.write(\'table.xlsx\')\n```\n\n\n\n',
    'author': 'Ryan Wang',
    'author_email': 'hwwangwang@gmail.com',
    'url': 'https://github.com/baoshishu/poi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
