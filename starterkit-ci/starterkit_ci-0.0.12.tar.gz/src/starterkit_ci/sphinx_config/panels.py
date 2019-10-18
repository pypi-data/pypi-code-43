__all__ = [
    'configure_app',
    'AddPanels',
]

import re

from docutils import nodes
from sphinx.transforms import SphinxTransform


def configure_app(app):
    app.add_transform(AddPanels)
    app.add_css_file('panels.css')
    app.add_js_file('panels.js')


class AddPanels(SphinxTransform):
    default_priority = 10

    # Mapping of name -> (default_visibile, icon)
    panel_defaults = {
        'prereq': (True, 'rocket'),
        'callout': (True, 'info-circle'),
        'challenge': (True, 'square-o'),
        'hiddenchallenge': (False, 'square-o'),
        'solution': (False, 'check-square-o'),
        'objectives': (True, 'line-chart'),
        'keypoints': (True, 'key'),
        'discussion': (False, 'bell'),
    }

    def apply(self, **kwargs):
        for node in self.document.traverse(nodes.Element)[::-1]:
            match = re.match(r'^ *{%\s*(\w+)\s*"([^"]+)"\s*%} *$', node.rawsource)
            if match:
                panel_type, title = match.groups()
                try:
                    visibile, icon = self.panel_defaults[panel_type]
                except KeyError:
                    raise ValueError(f'Unrecognised panel type {panel_type}',
                                     self.panel_defaults.keys())

                # Find the body of the panel
                inner_node = node
                current_nodes = []
                while True:
                    inner_node = inner_node.next_node(descend=False, siblings=True, ascend=False)
                    if inner_node is None:
                        raise ValueError(f'Failed to find end block for {node.rawsource} in {node.source}')
                    match = re.match(r'^ *{%\s*(\w+)\s*"([^"]+)"\s*%} *$', node.rawsource)
                    # Check if we're at the end of the panel block
                    if re.match(r'^\s*{%\s*end' + panel_type + r'\s*%}\s*$', inner_node.rawsource):
                        inner_node.parent.remove(inner_node)
                        break
                    current_nodes.append(inner_node)

                # Create a div
                panel_body = nodes.container()
                panel_body.attributes['classes'].append('panel-body')
                for inner_node in current_nodes:
                    inner_node.parent.remove(inner_node)
                    panel_body.append(inner_node)

                # Create the title text
                header_text = nodes.paragraph(ids=[title.replace(' ', '-').lower()])
                header_text.append(nodes.raw('', f'<i class="fa fa-{icon}"></i> ', format='html'))
                header_text.append(nodes.Text(title))

                # Create the title bar
                header = nodes.container()
                header.attributes['classes'].append('panel-header')
                if visibile:
                    header.attributes['classes'].append('open')
                header.append(header_text)

                # Move the inner nodes to the new container node and replace the parent
                new_node = nodes.container()
                new_node.attributes['classes'].append('panel')
                new_node.attributes['classes'].append('panel-' + panel_type)
                new_node.append(panel_body)
                new_node.insert(0, header)
                node.parent.replace(node, new_node)
