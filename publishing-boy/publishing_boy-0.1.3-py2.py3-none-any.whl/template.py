TEMPLATE = """title: {title}
date: {cdate}
modified: {mdate}
category: {categories}
authors: {authors}

{content}
"""


def render(context):
    """Use simple template render to generate content"""
    return TEMPLATE.format(**context)
