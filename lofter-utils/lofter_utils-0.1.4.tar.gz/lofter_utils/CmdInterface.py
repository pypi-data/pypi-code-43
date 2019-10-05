import argparse

from lofter_utils.TagConverterHelper import convert_file, convert_dir
from lofter_utils.TagDownloadHelper import download_line, download_file, download_dir


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True, choices=['download', 'convert'])
    parser.add_argument('--data-type', required=True, choices=['line', 'file', 'dir'])
    parser.add_argument('--data-value', required=True)
    parser.add_argument('--meta-type', choices=['tag, fav'], default='tag')
    parser.add_argument('--add-dir-timestamp', action='store_true')
    parser.add_argument('--add-file-timestamp', action='store_true')
    parser.add_argument('--output-dir')
    args = parser.parse_args()
    if args.action == 'download':
        if args.data_type == 'line':
            download_line(args.data_value, output_dir=args.output_dir)
        elif args.data_type == 'file':
            download_file(args.data_value, add_dir_timestamp=args.add_dir_timestamp,
                          output_dir=args.output_dir,
                          add_file_timestamp=args.add_file_timestamp)
        elif args.data_type == 'dir':
            download_dir(args.data_value, add_dir_timestamp=args.add_dir_timestamp,
                         output_dir=args.output_dir,
                         add_file_timestamp=args.add_file_timestamp)
    elif args.action == 'convert':
        if args.data_type == 'file':
            convert_file(args.data_value, output_dir=args.output_dir)
        elif args.data_type == 'dir':
            convert_dir(args.data_value, output_dir=args.output_dir)
        else:
            print('Illegal param: --data-type=%s' % args.data_type)
            exit(1)
    else:
        print('Illegal param: --action=%s' % args.action)
        exit(1)


if __name__ == '__main__':
    main()
