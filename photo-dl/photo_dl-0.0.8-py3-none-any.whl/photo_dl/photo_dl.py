import os
import sys
import getopt
import traceback
import re
from .request import request
from .save import save
from . import parsers


def main():
    opts, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    _help = 'assign a url or .txt file which one url one line\n' +\
            '$ photo-get  url\n' +\
            '$ photo-get xxx.txt'
    if not opts and not args:
        print(_help)
        return
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print(_help)
        return
    if len(args) > 1:
        print('too much parameters')
        return

    arg = args[0]
    albums = []
    try:
        if arg.find('.txt') != -1:
            with open(arg, 'r') as f:
                for line in f.readlines():
                    line = line.strip()
                    parser = parsers.url2parser(line)()
                    albums.extend(parser.url2albums(line))
        else:
            parser = parsers.url2parser(arg)()
            albums.extend(parser.url2albums(arg))
    except:
        print('parse error')
        print(traceback.print_exc())
        return

    for album in albums:
        parser_name = album['parser_name']
        album_name = album['album_name']
        photos = album['photos']
        print(album_name)
        dir = os.path.join('./photo-dl', parser_name, album_name.replace('/', ' '))
        if not os.path.isdir(dir):
            os.makedirs(dir)
        num = len(photos)
        print('total: %dP' % num)
        success = 0
        for i, photo in enumerate(photos):
            path = os.path.join(dir, photo['photo_name'])
            if os.path.exists(path):
                success += 1
                continue
            file = request(photo['photo_url'], html=False)
            success += save(file, path)
            print('\r%d / %s ' % (i + 1, num), end='')
        print()
        print('success: %d, error: %d' % (success, int(num) - success))
        print('-' * 50)
    print('end')


if __name__ == '__main__':
    main()
