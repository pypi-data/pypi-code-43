from optparse import OptionParser
import pathlib
import os
import sys
from mt import Article as MTArticle
from markdown import Writer as MDWriter


class Converter:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inner_writer = MDWriter()

    def validate_input_file_path(self, input_file_path):
        if os.path.isfile(input_file_path):
            return True
        print("Input file path {} is not a file!".format(input_file_path))
        return False

    def validate_output_base_path(self, output_base_path):
        if os.path.isdir(output_base_path):
            return True
        if not os.path.isdir(output_base_path):
            print("Output base path {} does not exist. Creating...".format(
                output_base_path))
            pathlib.Path(output_base_path).mkdir(parents=True, exist_ok=True)
            return True
        print("Output base path {} is not a directory!".format(output_base_path))
        return False

    def convert(self, input_file_path, output_base_path):
        abs_input_file_path = os.path.abspath(input_file_path)
        abs_output_base_path = os.path.abspath(output_base_path)

        if not self.validate_input_file_path(abs_input_file_path) or not self.validate_output_base_path(abs_output_base_path):
            sys.exit(-1)

        with open(abs_input_file_path, "r") as fp:
            article = MTArticle()
            for line in fp:
                article.append_line(line)
                if article.fullfilled():
                    self.inner_writer.write(abs_output_base_path, article)
                    article = MTArticle()


def main():
    option_parser = OptionParser()
    option_parser.add_option("-i", "--input-file", dest="input_file_path",
                             help="input file path (MovableType)", metavar="PATH")
    option_parser.add_option("-I", "--input-base-url", dest="input_base_url",
                             help="input base URL (Web site)", metavar="URL")
    option_parser.add_option("-o", "--output-directory", dest="output_directory_path",
                             help="output base directory path (Hugo)", metavar="PATH")
    (options, args) = option_parser.parse_args()

    parser = Converter()
    #TODO: parser.convert(input_config,output_config)
    # parser.convert(options.input_file_path, options.output_directory_path)
    parser.convert(options.input_file_path, options.output_directory_path)


if __name__ == '__main__':
    main()
