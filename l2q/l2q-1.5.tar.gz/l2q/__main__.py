import argparse
import logging
import os
from l2q.query_builder import QueryBuilder


def write(file, query):
    f = open(file, "w+")
    f.write(query)
    f.close()


def main():
    parser = argparse.ArgumentParser(description='List-to-query')
    parser.add_argument('--log-level', type=str, help='CRITICAL, ERROR, WARNING, INFO, DEBUG', default='WARN')
    parser.add_argument('file', type=str, help='Input file')
    parser.add_argument('-o', '--output', type=str, help='Output file')
    parser.add_argument('-s', '--sheet', type=str, help='Worksheet', default='Sheet1')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    logging.basicConfig(level=numeric_level)

    if args.file is None:
        exit(0)

    filename, extension = os.path.splitext(args.file)
    query = ''
    if extension == '.xlsx':
        query = QueryBuilder.build_query_from_excel(args.file, args.sheet)
    elif extension == '.docx':
        query = QueryBuilder.build_query_from_word_doc(args.file)
    else:
        try:
            query = QueryBuilder.build_query_from_txt(args.file)
        except UnicodeDecodeError:
            print('Unable to read file')

    if args.output is not None:
        write(args.file, query)
    else:
        print(query)


if __name__ == '__main__':
    main()
