
from typing import Optional, Tuple


def text_reader(path: str) -> Tuple[list, list]:
    """Read a text file, and return data
    data should follow this format:

    I O
    want O
    to O
    New B-City
    York I-City
    """
    with open(path, 'r') as fobj:
        parts = fobj.read().split('\n\n')
        parts = [part.strip() for part in parts]
        parts = [part for part in parts if len(part) > 0]
    assert parts, 'text file empty "{}"'.format(path)

    x_data = []
    y_data = []
    for part in parts:
        lines = part.split('\n')
        lines = [line.split() for line in lines]
        words = [x[0] for x in lines]
        tags = [x[-1] for x in lines]
        x_data.append(words)
        y_data.append(tags)
        assert len(words) == len(tags), \
            'line "{}" and "{}" do not match "{}" vs "{}"'.format(
                len(words), len(tags), words, tags)
    return x_data, y_data