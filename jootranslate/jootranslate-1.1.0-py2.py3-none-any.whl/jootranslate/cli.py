import argparse
import os
import re
from builtins import input
from typing import Union

from configobj import ConfigObj


class JooTranslate(object):
    paths = {}
    not_conform = []
    missing = []
    logfile = os.path.join(os.getcwd(), 'jootranslate.log')

    def __init__(self, args: argparse.ArgumentParser) -> None:
        """

        :param args:
        :type args: argparse.ArgumentParser
        """
        self.args = args
        self.search_pattern = r'(label=|description=|hint=|JText::_\(|JText::script\()(\'|"){1}(.*?)(\'|"){1}'
        self.config_search_pattern = r'(title=)(\'|\"){1}(.*?)(\'|\"){1}|(<\!\[CDATA\[)(.*?)(]){1}'
        self.settings_search_pattern = r'(<){1}(name>|description>)(.*?)(<\/){1}(name|description)(>){1}'
        self.set_file_paths()
        self.read_dir()
        self.read_menu_configs()
        self.print_log()

    @staticmethod
    def get_logfile() -> Union[bytes, str]:
        """get the path of the logfile"""
        return JooTranslate.logfile

    def read_dir(self) -> None:
        """
        reads all php and xml files and searches for regex pattern

        :return void:
        """
        matches = []
        settings_file = os.path.join(self.args.path, '{}.xml'.format(self.args.com.split('_')[1]))
        if os.path.isfile(settings_file):
            settings = open(settings_file, 'rb')
            matches = self._get_pattern(settings, self.settings_search_pattern)
        for key, value in self.paths.items():
            patterns = []
            if key == 'admin':
                patterns = patterns + matches
            for folder, dirs, files in os.walk(value, topdown=False):
                for filename in files:
                    if filename.endswith(('.php', '.xml')):
                        with open(os.path.join(folder, filename), 'rb') as dest:
                            patterns = patterns + self._get_pattern(dest, self.search_pattern)

            self.write_file(value, patterns)

    def read_menu_configs(self) -> None:
        """
        reads all php and xml files and searches for regex pattern

        :return void:
        """
        patterns = []
        for folder, dirs, files in os.walk(os.path.join(self.paths['component'], 'views'), topdown=False):
            for filename in files:
                if filename.endswith(('.xml')):
                    with open(os.path.join(folder, filename), 'rb') as dest:
                        patterns = patterns + self._get_pattern(dest, self.config_search_pattern)

        self.write_file(self.paths['admin'], patterns, True)

    def _get_pattern(self, dest, search_pattern) -> list:
        """

        :param dest:
        :return:
        """
        patterns = []
        for l in dest.readlines():
            try:
                pattern = re.search(search_pattern, l.decode(('utf8'))).group(3)
                if not pattern:
                    pattern = re.search(search_pattern, l.decode(('utf8'))).group(6)
                if pattern == '':
                    self.missing.append('{} - {}'.format(dest.name, l))
                    continue
                if self.args.com.upper() in pattern:
                    patterns.append(pattern)
                else:
                    self.not_conform.append('{} - {}'.format(dest.name, pattern))
            except AttributeError:
                continue
            except Exception as e:
                print(e)
                continue
        return patterns

    def write_file(self, path, patterns, sys=False) -> None:
        """
        writes all found patterns to the ini file if pattern not exist

        :param path: the path to admin or component root
        :type path: str
        :param patterns: list of found translation strings
        :type patterns: list
        :return void:
        """
        lang_file = os.path.join(path, 'language', self.args.lang, self.get_filename(sys=sys))
        if self.args.trans and patterns:
            print('working on {}'.format(lang_file))

        self._create_dir(lang_file)
        self._create_file(lang_file)

        try:
            conf_obj = ConfigObj(lang_file, stringify=True, unrepr=True, encoding='utf-8')
        except Exception as e:
            for err in e.errors:
                print(err.line)
            raise Exception('Make sure to use \' instead of ". And use spaces like TRANSLATION = \'translation\'')
        for p in patterns:
            if p not in conf_obj:
                if self.args.trans:
                    key = input('translation for: {}\n'.format(p))
                    conf_obj[p] = u'{}'.format(key)
                else:
                    conf_obj[p] = ""
        conf_obj.write()

    def _create_file(self, lang_file) -> None:
        """
        create necessary file if not exist

        :param lang_file: path to the language file
        :type lang_file: str
        :return: void
        """
        if not os.path.isfile(lang_file):
            f = open(lang_file, 'w+')
            f.close()

    def _create_dir(self, lang_file) -> None:
        """
        create necessary dirs if not exist

        :param lang_file:  path to the language file
        :type lang_file: str
        :return: void
        """
        if not os.path.exists(os.path.dirname(lang_file)):
            os.mkdir(os.path.dirname(lang_file))

    def get_filename(self, sys=False) -> str:
        """
        :param: sys
        :type sys: bool
        :return: name of the language ini file
        :rtype: str
        """
        if sys:
            return '{}.{}.sys.ini'.format(self.args.lang, self.args.com.lower())
        return '{}.{}.ini'.format(self.args.lang, self.args.com.lower())

    def set_file_paths(self) -> None:
        """
        sets the needed paths to admin and component part

        :return: void
        """
        self.paths['component'] = os.path.join(self.args.path, 'site')
        self.paths['admin'] = os.path.join(self.args.path, 'admin')

    def print_log(self) -> None:
        """print some debug information"""
        if self.args.log:
            log_file = open(self.logfile, 'w+')
            log_file.write('missing translations:\n')
            for m in self.missing:
                log_file.write(m + '\n')
            log_file.write('not conform translation strings:\n')
            for nc in self.not_conform:
                log_file.write(nc + '\n')
            log_file.close()
        else:
            print('missing translations:')
            for m in self.missing:
                print(m)
            print('------------------')
            print('not conform translation strings:')
            for nc in self.not_conform:
                print(nc)


def main():
    parser = argparse.ArgumentParser(description='A translation ini file generator for joomla developers')
    parser.add_argument('-s', '--source', dest='path', help="directory to search in", required=True)
    parser.add_argument('-c', '--com', dest='com', help="the name of the component", required=True)
    parser.add_argument('-l', '--lang', dest='lang', default='en-GB', help="language localisation. default is en-GB")
    parser.add_argument(
        '-t', '--translate', dest='trans', action='store_true',
        help="If you want to translate the strings on console")
    parser.add_argument("--logfile", dest='log', default=False, action="store_true", help="write stdout to logfile")
    args = parser.parse_args()
    jt = JooTranslate(args=args)


if __name__ == '__main__':
    main()
