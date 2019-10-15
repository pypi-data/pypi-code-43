from argparse import ArgumentParser
import sys
import os

from dxf2x import dxf, tsv, svg, proto

def command_line_options():
    parser = ArgumentParser(prog = 'dxf2x',
                            description = 'convert between DXF, TSV, SVG, PXF(Protobuf) formats.',
                            epilog = 'Report bugs to <redraiment@gmail.com>.')
    parser.add_argument('files', metavar = 'FILE', nargs = '+',
                        help = 'All the files are read and converted in turn.')

    parser.add_argument('-s', '--source', metavar = 'FORMAT',
                        choices = ['dxf', 'tsv', 'svg', 'pxf'],
                        help = 'Specifies the format of the input. Determined by FILE by default.')
    parser.add_argument('-t', '--target', metavar = 'FORMAT', required = True,
                        choices = ['dxf', 'tsv', 'svg', 'pxf'],
                        help = 'Specifies the format of the output.')
    parser.add_argument('-d', '--dir',
                        help = 'Specifies the directory for output files.')
    parser.add_argument('-q', '--quiet', action = 'store_true', default = False,
                        help = 'Disable the progress.')

    parser.add_argument('-v', '--version', action = 'version', version = '%(prog)s 0.0.1')

    options = parser.parse_args()

    if options.dir and not os.path.isdir(options.dir):
        sys.stderr.write(f'DIR {options.dir} is not a directory.\n')
        sys.exit(-1)

    return options

def guess_format(filename):
    return os.path.splitext(filename)[1][1:].lower()

def guess_target_filename(dir, source, target):
    path, filename = os.path.split(source)
    name, ext = os.path.splitext(filename)
    return os.path.join(dir or path, f'{name}.{target}')

def dxf2x():
    options = command_line_options()
    readers = {
        'dxf': dxf.read,
        'svg': svg.read,
        'tsv': tsv.read,
        'pxf': proto.read
    }
    writers = {
        'dxf': dxf.write,
        'svg': svg.write,
        'tsv': tsv.write,
        'pxf': proto.write
    }
    for source_filename in options.files:
        source = options.source or guess_format(source_filename)
        target_filename = guess_target_filename(options.dir, source_filename, options.target)

        if not options.quiet:
            print(f'convert {source_filename} to {target_filename}')

        reader = readers[source]
        writer = writers[options.target]
        writer(reader(source_filename), target_filename)

if __name__ == '__main__':
    dxf2x()
