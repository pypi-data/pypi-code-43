#!/usr/bin/env python

import click
import os
import sys
import json
import exifread
import re
import pprint
from geopy.distance import geodesic

DEFAULT_FILE_PATTERN='.*\.[jJ][pP][gG]$|.*\.[jJ][pP][eE][gG]$'
DEFAULT_INCLUDE='.'
DEFAULT_EXCLUDE='.*[tT]humbnail.*'

@click.command()
@click.option('-r', '--recurse', is_flag=True, default=False, help='descend into subdirectories')
@click.option('-f', '--file_filter', type=click.STRING, default=DEFAULT_FILE_PATTERN, help='regex pattern to select filenames')
@click.option('-t', '--include_filter', type=click.STRING, default=DEFAULT_INCLUDE, help='regex pattern to select EXIF tags (default is all)') 
@click.option('-T', '--exclude_filter', type=click.STRING,
default=DEFAULT_EXCLUDE, help='regex pattern to exclude EXIF tags (default is \'%s\' use \'\.^\' to exclude nothing' % DEFAULT_EXCLUDE)
@click.option('-j', '--format-json', is_flag=True, default=False, help='output as JSON')
@click.option('-c', '--compact', is_flag=True, default=False, help='compact output')
@click.option('-n', '--no_exif', is_flag=True, default=False, help='output only files with no EXIF data')
@click.option('-d', '--distance', type=click.STRING, default=None, help='filter output by distance given LATITUDE,LONGITUDE,METERS in decimal (include_filter must include GPS data')
@click.option('--data/--no-data', is_flag=True, default=True, help='output EXIF data')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, allow_dash=True), default='.')

def cli(directory, recurse, file_filter, include_filter, exclude_filter,
format_json, compact, no_exif, distance, data):
    """Scan DIRECTORY for image files, printing filenames and selected EXIF data"""

    if distance:
        distance = parse_distance(distance)

    if directory == '-':
        read_stdin(re.compile(file_filter), re.compile(include_filter),
        re.compile(exclude_filter), format_json, compact, no_exif,
        distance, data)  
    else:
        read_directory(directory, recurse, re.compile(file_filter),
        re.compile(include_filter), re.compile(exclude_filter), format_json,
        compact, no_exif, distance, data)

def read_stdin(file_filter, include_filter, exclude_filter, format_json,
compact, no_exif, distance):
    for pathname in sys.stdin:
        pathname = pathname.strip()
        process_file(pathname, file_filter, include_filter, exclude_filter,
        format_json, compact, no_exif, distance, data)

def read_directory(directory, recurse, file_filter, include_filter,
exclude_filter, format_json, compact, no_exif, distance, data):
    for name, dirs, files in os.walk(directory):
        for f in files:
            process_file(os.path.join(name, f), file_filter, include_filter,
            exclude_filter, format_json, compact, no_exif, distance, data)
        if not recurse:
            break

def process_file(pathname, file_filter, include_filter, exclude_filter,
format_json, compact, no_exif, distance, data):
    #print('process_file%s' % repr((pathname, file_filter, include_filter, exclude_filter, format_json, compact, no_exif, distance)))
    if filter_filename(pathname, file_filter):
        tags = read_exif(pathname, include_filter, exclude_filter)
        if (no_exif and not tags) or (not no_exif and tags):
           if not distance or within_distance(distance, tags): 
               output = format_output(pathname, tags, format_json, compact) if data else pathname
               sys.stdout.write(output+'\n')
               sys.stdout.flush()

def parse_distance(distance):
    """parse comma delimited string returning (latitude, longitude, meters)"""
    latitude, longitude, meters = [float(n) for n in distance.split(',')]
    return (latitude, longitude, meters)

def within_distance(distance, tags):
    dlat, dlon, limit = distance
    plat, plon = parse_gps(tags)
    distance = geodesic((dlat, dlon), (plat, plon)).meters
    limit=float(limit)
    #print('GPS: picture=%f,%f location=%f,%f distance=%f limit=%f' % (plat, plon, dlat, dlon, distance, limit))
    return distance < limit

def parse_gps(tags):
    ret={}
    for label in ['Latitude', 'Longitude']:
        text_key = 'GPS GPS' + label
        ref_key = 'GPS GPS' + label + 'Ref'
        ret[label] = parse_dms(tags.get(text_key, '[0,0,0]'), tags.get(ref_key,''))
    return (ret['Latitude'], ret['Longitude'])

"""
"GPS GPSLatitudeRef": "N",
    "GPS GPSLatitude": "[37, 11, 2611/100]",

see https://sno.phy.queensu.ca/~phil/exiftool/TagNames/GPS.html
"""
def parse_dms(text, ref):
    value = 0
    fields = re.match('\[\s*(.+)\s*,\s*(.+)\s*,\s*(.+)\s*\]', text).groups()
    for i in range(3):
        if '/' in fields[i]:
           num, den = fields[i].split('/') 
           fval = float(num) / float(den)
        else:
           fval = float(fields[i])
        value += fval / (60 ** i)
    return -value if ref in ['S', 'W'] else value

def filter_filename(pathname, pattern):
    #print('filter_filename%s' % repr((pathname, pattern)))
    if pattern: 
        if pattern.match(pathname):
            ret = pathname
        else:
            ret = None
    else:
       ret = pathname
    #print('ret=%s'% ret)
    return ret

def read_exif(pathname, include, exclude):
    #print('read_exif%s' % repr((pathname, include, exclude)))
    with open(pathname, 'rb') as f:
        tags = exifread.process_file(f)
    ret = filter_tags(tags, include, exclude)
    #print('ret=%s'% ret)
    return ret

def filter_tags(tags, include, exclude):
    #print('filter_tags%s' % repr((tags, include, exclude)))
    ret = {}
    for key in tags.keys():
        if re.match(include, key) and not re.match(exclude, key):
            ret[key] = str(tags[key])
    #print('ret=%s'% ret)
    return ret 

def format_output(pathname, tags, format_json, compact):
    #print('format_output%s' % repr((pathname, tags, format_json, compact)))
    if format_json: 
        output = json.dumps({pathname: tags}, separators=(',',':') if compact else None,
        indent=None if compact else 2)
    else:
        if compact:
            output = pathname
            if tags:
                output += '\t%s' % repr(tags)
        else:
            output = pprint.pformat({pathname: tags})
    return output
