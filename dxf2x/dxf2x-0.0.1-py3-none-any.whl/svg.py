from xml.etree.ElementTree import Element, SubElement, ElementTree, iterparse
from functools import reduce
from operator import gt, lt

from dxf2x.compiler import syntax

# read

def to_insert(node):
    return {
        '0': 'INSERT',
        '8': node.attrib.get('class', '')[1:],
        '2': node.attrib.get('data-name', ''),
        '10': node.attrib.get('x', '0'),
        '20': node.attrib.get('y', '0')
    }

def to_text(node):
    return {
        '0': 'TEXT',
        '8': node.attrib.get('class', '')[1:],
        '10': node.attrib.get('x', '0'),
        '20': node.attrib.get('y', '0'),
        '40': node.attrib.get('data-height', '0'),
        '50': node.attrib.get('data-rotate', '0'),
        '1': node.text
    }

def to_polyline(node):
    polyline = {
        '0': 'POLYLINE',
        '8': node.attrib.get('class', '')[1:],
        '66': '1',
        '70': '1' if node.tag == 'polygon' else '0'
    }
    if 'data-style' in node.attrib:
        polyline['6'] = node.attrib['data-style']
    yield polyline
    for vertex in node.attrib['points'].split(' '):
        x, y = vertex.split(',')
        yield {
            '0': 'VERTEX',
            '8': polyline['8'],
            '10': x,
            '20': y
        }
    yield {'0': 'SEQEND', '8': polyline['8']}

def to_line(node):
    line = {
        '0': 'LINE',
        '8': node.attrib.get('class', '')[1:],
        '10': node.attrib.get('x1', '0'),
        '20': node.attrib.get('y1', '0'),
        '11': node.attrib.get('x2', '0'),
        '21': node.attrib.get('y2', '0')
    }
    if 'data-style' in node.attrib:
        line['6'] = node.attrib['data-style']
    return line

def to_point(node):
    point = {
        '0': 'POINT',
        '8': node.attrib.get('class', '')[1:],
        '10': node.attrib.get('cx', '0'),
        '20': node.attrib.get('cy', '0')
    }
    if point['8'] == 2:
        point['30'] = '3'
        point['50'] = node.attrib.get('data-rotate', '0')
    return point

def to_block(block):
    yield {'0': 'BLOCK', '8': '1', '2': block.attrib['data-name'], '70': '0', '10': '0.0', '20': '0.0'}
    for entity in list(block):
        if entity.tag in {'polyline', 'polygon'}:
            for token in to_polyline(entity):
                yield token
        elif entity.tag == 'line':
            yield to_line(entity)
        elif entity.tag == 'circle':
            yield to_point(entity)
        elif entity.tag == 'text':
            yield to_text(entity)

    yield {'0': 'ENDBLK'}

def lexical(svg):
    _, blocks, *entities = list(svg)

    yield {'0': 'SECTION', '2': 'BLOCKS'}
    for block in list(blocks):
        for token in to_block(block):
            yield token
    yield {'0': 'ENDSEC'}

    yield {'0': 'SECTION', '2': 'ENTITIES'}
    for entity in entities:
        if entity.tag == 'use':
            yield to_insert(entity)
        elif entity.tag == 'text':
            yield to_text(entity)
    yield {'0': 'ENDSEC'}

    yield {'0': 'EOF'}

def read(filename):
    svg = iterparse(filename)
    for _, e in svg:
        e.tag = e.tag[e.tag.find('}')+1:]
    return syntax(lexical(svg.root))

# write

class BoundingBox:

    directions = {'left': gt, 'right': lt, 'bottom': gt, 'top': lt}

    def fromPoint(point):
        return BoundingBox(left = point[0], right = point[0], bottom = point[1], top = point[1])

    def __init__(self, **box):
        self.box = box

    def __getattr__(self, name):
        if name in BoundingBox.directions:
            return self.box[name] if name in self.box else 0
        elif name == 'width':
            return self.right - self.left
        elif name == 'height':
            return self.top - self.bottom
        return None

    def merge(self, other):
        this = self.box
        that = other.box
        for name, compare in BoundingBox.directions.items():
            if name in that and (name not in this or compare(this[name], that[name])):
                this[name] = that[name]
        return self

    def add(self, other):
        this = self.box
        that = other.box
        for name in BoundingBox.directions.keys():
            if name in that:
                if name in this:
                    this[name] += that[name]
                else:
                    this[name] = that[name]
        return self

    def __str__(self):
        return f'{{"left": {self.left}, "right": {self.right}, "bottom": {self.bottom}, "top": {self.top}}}'

class Shape:

    def getter(key, f = None):
        if f is not None:
            return lambda entity: f(entity[key]) if key in entity else None
        else:
            return lambda entity: entity.get(key, None)

    getters = {
        'layer': getter('8', lambda layer: f'L{layer}'),
        'rotate': getter('50')
    }

    rules = {
        'POLYLINE': {
            'tag': lambda entity: 'polygon' if entity['70'] == '1' else 'polyline',
            'attributes': {
                'class': getters['layer'],
                'data-style': getter('6'),
                'points': lambda entity: ' '.join([f'{vertex["10"]},{vertex["20"]}' for vertex in entity['vertices']])
            },
            'bounding-box': lambda entity: [(float(vertex['10']), float(vertex['20'])) for vertex in entity['vertices']]
        },
        'LINE': {
            'tag': 'line',
            'attributes': {
                'class': getters['layer'],
                'x1': '10',
                'y1': '20',
                'x2': '11',
                'y2': '21',
                'data-style': getter('6')
            },
            'bounding-box': [('10', '20'), ('11', '21')]
        },
        'POINT': {
            'tag': 'circle',
            'attributes': {
                'class': getters['layer'],
                'cx': '10',
                'cy': '20',
                'r': lambda entity: '1',
                'data-rotate': getters['rotate']
            },
            'bounding-box': [('10', '20')]
        },
        'TEXT': {
            'tag': 'text',
            'attributes': {
                'class': getters['layer'],
                'x': '10',
                'y': '20',
                'data-height': getter('40'),
                'data-rotate': getters['rotate']
            },
            'bounding-box': lambda entity: [(float(entity['10']), float(entity['20'])),
                                            (float(entity['10']) + len(entity['1']) * 12, float(entity['20']) - 12)],
            'text': '1'
        },
        'INSERT': {
            'tag': 'use',
            'attributes': {
                'class': getters['layer'],
                'data-name': '2',
                'x': '10',
                'y': '20',
                'xlink:href': lambda entity: f'#{entity["id"]}'
            },
            'bounding-box': [('10', '20')]
        }
    }

    def eval(entity, expression):
        return entity[expression] if isinstance(expression, str) else expression(entity)

    def __init__(self, parent):
        self.parent = parent

    def __call__(self, entity):
        if entity['0'] not in Shape.rules:
            return BoundingBox()

        rule = Shape.rules[entity['0']]
        tag = rule['tag']
        element = SubElement(self.parent, tag if isinstance(tag, str) else tag(entity))
        for attribute, expression in rule['attributes'].items():
            value = Shape.eval(entity, expression)
            if value is not None:
                element.attrib[attribute] = value
        if 'text' in rule:
            element.text = entity[rule['text']]

        bounds = rule['bounding-box']
        if isinstance(bounds, list):
            points = [(float(entity[point[0]]), float(entity[point[1]])) for point in bounds]
        else:
            points = bounds(entity)
        return reduce(BoundingBox.merge, map(BoundingBox.fromPoint, points), BoundingBox())

class Svg:

    def __init__(self):
        self.svg = Element('svg')
        style = SubElement(self.svg, 'style')
        style.text = '''
    polyline, polygon {
      fill: none;
      stroke: red;
      stroke-width: 1px;
    }
    line {
      fill: none;
      stroke: blue;
      stroke-width: 1px;
    }
    text {
      fill: rgba(0.5, 0.5, 0.5, 0.5);
    }
  '''

    def foreach_blocks(self, ast):
        blocks = {}
        defs = SubElement(self.svg, 'defs')
        for index, block in enumerate(ast):
            id = str(index + 1)
    
            g = SubElement(defs, 'g')
            g.attrib = {
                'id': str(id),
                'data-name': block['2']
            }
    
            name = block['2']
            if name not in blocks:
                blocks[name] = []
            blocks[name].append({
                'id': id,
                'box': reduce(BoundingBox.merge, map(Shape(g), block['entities']))
            })
        return blocks

    def foreach_entities(self, ast, blocks):
        box = BoundingBox()
        shape = Shape(self.svg)
        for entity in ast:
            if entity['0'] == 'INSERT':
                name = entity['2']
                if name in blocks and blocks[name]:
                    block = blocks[name].pop()
                    entity['id'] = block['id']
                    box.merge(shape(entity).add(block['box']))
            elif entity['0'] == 'TEXT':
                box.merge(shape(entity))
        return box

    def __call__(self, ast):
        box = self.foreach_entities(ast['entities'], self.foreach_blocks(ast['blocks']))
        self.svg.attrib = {
            'version': '1.0',
            'width': str(box.width + 20),
            'height': str(box.height + 20),
            'viewBox': f'{box.left - 10} {box.bottom - 10} {box.width + 20} {box.height + 20}',
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink'
        }
        return self.svg

def write(ast, filename):
    svg = ElementTree(Svg()(ast))
    svg.write(filename, encoding = 'utf-8')
