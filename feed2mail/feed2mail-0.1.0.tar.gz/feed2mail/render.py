from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader('feed2mail', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


def as_html(items):
    template = env.get_template('email.html.j2')
    return template.render(feeds=items)

def as_text(items):
    template = env.get_template('email.text.j2')
    return template.render(feeds=items)

