from operator import attrgetter

from dxf2x.compiler import syntax
from dxf2x.model_pb2 import Document, Block, Insert, Polyline, Vertex, Line, Point, Text

# read

def float_to_str(number):
    return '%.6f' % number

def to_insert(proto):
    return {
        '0': 'INSERT',
        '8': '1',
        '10': float_to_str(proto.x),
        '20': float_to_str(proto.y)
    }

def to_polyline(proto):
    polyline = {
        '0': 'POLYLINE',
        '8': str(proto.layer) if proto.layer >= 0 else 'CUTME',
        '66': '1',
        '70': '1' if proto.closed else '0'
    }
    if proto.style:
        polyline['6'] = proto.style
    yield polyline
    for vertex in proto.vertices:
        yield {
            '0': 'VERTEX',
            '8': polyline['8'],
            '10': float_to_str(vertex.x),
            '20': float_to_str(vertex.y)
        }
    yield {'0': 'SEQEND', '8': polyline['8']}

def to_line(proto):
    line = {
        '0': 'LINE',
        '8': str(proto.layer),
        '10': float_to_str(proto.x1),
        '20': float_to_str(proto.y1),
        '11': float_to_str(proto.x2),
        '22': float_to_str(proto.y2)
    }
    if proto.style:
        line['6'] = proto.style
    return line

def to_point(proto):
    point = {
        '0': 'POINT',
        '8': str(proto.layer),
        '10': float_to_str(proto.x),
        '20': float_to_str(proto.y)
    }
    if proto.layer == 2:
        point['30'] = '3'
        point['50'] = float_to_str(proto.rotate)
    return point

def to_text(proto):
    return {
        '0': 'TEXT',
        '8': str(proto.layer),
        '10': float_to_str(proto.x),
        '20': float_to_str(proto.y),
        '40': float_to_str(proto.height),
        '50': float_to_str(proto.rotate),
        '1': proto.content
    }

def to_block(block):
    yield {'0': 'BLOCK', '8': '1', '2': block.name, '70': '0', '10': '0.0', '20': '0.0'}
    entities = []
    entities.extend(block.polylines)
    entities.extend(block.lines)
    entities.extend(block.points)
    entities.extend(block.annotations)

    entities.sort(key = attrgetter('id'))
    for entity in entities:
        if type(entity) is Polyline:
            for token in to_polyline(entity):
                yield token
        elif type(entity) is Line:
            yield to_line(entity)
        elif type(entity) is Point:
            yield to_point(entity)
        elif type(entity) is Text:
            yield to_text(entity)
    
    yield {'0': 'ENDBLK'}

def lexical(proto):
    yield {'0': 'SECTION', '2': 'BLOCKS'}
    for block in proto.blocks:
        for token in to_block(block):
            yield token
    yield {'0': 'ENDSEC'}

    yield {'0': 'SECTION', '2': 'ENTITIES'}
    for insert in proto.inserts:
        yield to_insert(insert)
    for text in proto.attributes:
        yield to_text(text)
    yield {'0': 'ENDSEC'}

    yield {'0': 'EOF'}

def read(filename):
    with open(filename, 'rb') as f:
        return syntax(lexical(Document.FromString(f.read())))

# write

create_proto_rules = {
    'BLOCK': {
        'type': Block,
        '2': ('name', str)
    },
    'INSERT': {
        'type': Insert,
        '2': ('name', str),
        '10': ('x', float),
        '20': ('y', float)
    },
    'POLYLINE': {
        'type': Polyline,
        '6': ('style', str),
        '8': ('layer', lambda layer: int(layer) if layer.isdigit() else -1),
        '70': ('closed', lambda flag: flag == '1')
    },
    'VERTEX': {
        'type': Vertex,
        '10': ('x', float),
        '20': ('y', float)
    },
    'LINE': {
        'type': Line,
        '6': ('style', str),
        '8': ('layer', int),
        '10': ('x1', float),
        '20': ('y1', float),
        '11': ('x2', float),
        '21': ('y2', float)
    },
    'POINT': {
        'type': Point,
        '8': ('layer', int),
        '10': ('x', float),
        '20': ('y', float),
        '50': ('rotate', float)
    },
    'TEXT': {
        'type': Text,
        '1': ('content', str),
        '8': ('layer', int),
        '10': ('x', float),
        '20': ('y', float),
        '40': ('height', float),
        '50': ('rotate', float)
    }
}

fill_proto_rules = {
    'blocks': {
        'BLOCK': {
            'collection': 'blocks',
            'children': {
                'entities': {
                    'POLYLINE': {
                        'collection': 'polylines',
                        'children': {
                            'vertices': {
                                'VERTEX': {
                                    'collection': 'vertices'
                                }
                            }
                        }
                    },
                    'LINE': {'collection': 'lines'},
                    'POINT': {'collection': 'points'},
                    'TEXT': {'collection': 'annotations'}
                }
            }
        }
    },
    'entities': {
        'INSERT': {
            'collection': 'inserts'
        },
        'TEXT': {
            'collection': 'attributes'
        }
    }
}

index = 0

def create(entity):
    global create_proto_rules, index
    name = entity['0']
    if name in create_proto_rules:
        meta = create_proto_rules[name]
        params = {meta[code][0]: meta[code][1](value) for code, value in entity.items() if code in meta}
        proto = meta['type'](**params)
        if hasattr(proto, 'id'):
            index += 1
            proto.id = index
        return proto
    else:
        return None

def fill(ast, proto, mappings):
    for node, rules in mappings.items():
        for element in ast[node]:
            name = element['0']
            if name in rules:
                rule = rules[name]
                collection = getattr(proto, rule['collection'])
                collection.append(create(element))
                if 'children' in rule:
                    fill(element, collection[-1], rule['children'])

def write(ast, filename):
    global index
    with open(filename, 'wb') as f:
        index = 0
        document = Document()
        fill(ast, document, fill_proto_rules)
        f.write(document.SerializeToString())
