from xml.dom import minidom
from io import StringIO
import os
import datetime
import csv
import re


def format_sf_date(src, format='%m/%d/%Y'):
    if not re.match('\d+-\d+-\d+', src):
        d = datetime.datetime.strptime(src, format)
        return datetime.datetime.strftime(d, '%Y-%m-%d')
    return src


def decode_xml(text):
    """Parse an XML document into a dictionary.  This assume that the
    document is only 1 level, i.e.:
    <top>
        <child1>content</child1>
        <child2>content</child2>
    </top>
    will be parsed as: child1=content, child2=content"""
    xmldoc = minidom.parseString(text)
    return dict([(x.tagName, x.firstChild.nodeValue)
                 for x in xmldoc.documentElement.childNodes
                 if x.childNodes.length == 1])


def make_csv(data):
    """Create a CSV string from an array of dictionaries"""
    if type(data) == str:
        return data
    buf = StringIO()
    writer = csv.DictWriter(buf, data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    r = buf.getvalue()
    buf.close()
    return r


def parse_csv(data):
    """Parse a CSV string into an array of dictionaries"""
    buf = StringIO(data)
    result = [r for r in csv.DictReader(buf)]
    buf.close()
    return result


def appendcsv(path, header, keys, data):
    """Append to an existing CSV file, or create a new one if it does not
    exist.
    'header' is only used if the file does not exist.
    'data' is an array of dictionary objects."""
    if os.path.exists(path):
        f = open(path, 'a')
    else:
        f = open(path, 'w')
        f.write(header + '\n')
    writer = csv.DictWriter(f, keys, extrasaction='ignore')
    for row in data:
        writer.writerow(row)
    f.close()


def updatecsv(path, data):
    """Rewrite an existing CSV file.  Assumes the keys in data match the ones in the CSV.  If there are extra keys they will be appended."""
    with open(path, 'r') as f:
        keys = csv.reader(f).next()
    keyset = set(keys)
    keys = keys + [k for k in data[0].keys() if k not in keyset]
    with open(path, 'w') as out:
        writer = csv.DictWriter(out, keys)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
