import logging
import os
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class Writer:
    code_type = None
    path_output = None
    template_path = None

    def print_dict(self, **kwargs):
        if isinstance(kwargs, dict):
            logger.debug(f'Class: {self.__class__.__name__}')
            if len(kwargs.items()) == 0:
                logger.debug('{}')
                return
            logger.debug('{')
            for key, value in kwargs.items():
                if isinstance(value, str):
                    logger.debug(f'{self.fill_space(4) + key + " : " + value}')
                elif isinstance(value, bool):
                    logger.debug(f'{self.fill_space(4) + key + " : " + str(value)}')
                elif isinstance(value, int):
                    logger.debug(f'{self.fill_space(4) + key + " : " + str(value)}')
            logger.debug('}')
        else:
            logger.warning(f'{kwargs} is not a dict')

    def check_path(self, path):
        if not os.path.exists(path):
            raise Exception(f'Путь {path} не существует.')
        else:
            return path

    def fill_space(self, qty):
        if qty == -1:
            return ''
        res = ''
        while True:
            res += ' '
            qty -= 1
            if qty == 0:
                return res

    def uncapitalize(self, str):
        return str[0:1].lower() + str[1:]

    def taged(self, str):
        return '${' + str + '}'

    def braces(self, str):
        return '{' + str + '}'

    def get_pattern(self, str):
        return re.compile('(.+?)(\$?\{' + str + '.*?\})|(.*)')

    def capitalize(self, str):
        return str[0:1].upper() + str[1:]

    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def qutes_str(self, str):
        return f"'{str}'"

    def __init__(self, *args, **kwargs):
        self.path_output = settings.BASE_DIR
        self.check_path(self.path_output)

        self.template_path = settings.BASE_PATH_TEMPLATE
        self.check_path(self.template_path)

    def write_entity(self, replace_map=None):
        o = open(self.path_output, "w+")  # open for append
        for line in open(self.template_path):
            if isinstance(replace_map, dict):
                for key, value in replace_map.items():
                    if isinstance(value, list):
                        value = '\n'.join(value)
                    line = line.replace('${' + key + '}', value)
            o.write(f'{line}')
        o.close()


class Writer:
    code_type = None
    path_output = None
    output_file_ext = None
    output_file_name = None
    template_path = None

    def print_dict(self, **kwargs):
        if isinstance(kwargs, dict):
            logger.debug(f'Class: {self.__class__.__name__}')
            if len(kwargs.items()) == 0:
                logger.debug('{}')
                return
            logger.debug('{')
            for key, value in kwargs.items():
                if isinstance(value, str):
                    logger.debug(f'{self.fill_space(4) + key + " : " + value}')
                elif isinstance(value, bool):
                    logger.debug(f'{self.fill_space(4) + key + " : " + str(value)}')
                elif isinstance(value, int):
                    logger.debug(f'{self.fill_space(4) + key + " : " + str(value)}')
            logger.debug('}')
        else:
            logger.warning(f'{kwargs} is not a dict')

    def check_path(self, path):
        if not os.path.exists(path):
            raise Exception(f'Путь {path} не существует.')
        else:
            return path

    def fill_space(self, qty):
        if qty == -1:
            return ''
        res = ''
        while True:
            res += ' '
            qty -= 1
            if qty == 0:
                return res

    def uncapitalize(self, str):
        return str[0:1].lower() + str[1:]

    def taged(self, str):
        return '${' + str + '}'

    def braces(self, str):
        return '{' + str + '}'

    def get_pattern(self, str):
        return re.compile('(.+?)(\$?\{' + str + '.*?\})|(.*)')

    def capitalize(self, str):
        return str[0:1].upper() + str[1:]

    def dbl_qutes_str(self, str):
        return f'"{str}"'

    def qutes_str(self, str):
        return f"'{str}'"

    def __init__(self, *args, **kwargs):
        self.path_output = kwargs.get('path_output')
        self.output_file_name = kwargs.get('output_file_name')
        self.output_file_ext = kwargs.get('output_file_ext')
        self.template_path = kwargs.get('template_path')

    def write_entity(self, replace_map=None):
        path_output = self.path_output
        if self.output_file_name:
            path_output += os.sep + self.output_file_name
        if self.output_file_ext:
            path_output += self.output_file_ext

        o = open(path_output, "w+")  # open for append
        for line in open(self.template_path):
            if isinstance(replace_map, dict):
                for key, value in replace_map.items():
                    if isinstance(value, list):
                        value = '\n'.join(value)
                    line = line.replace('${' + key + '}', value)
            o.write(f'{line}')
        o.close()
