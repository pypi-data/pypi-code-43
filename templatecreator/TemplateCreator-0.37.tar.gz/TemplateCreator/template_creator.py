import os
from os.path import join, normpath
from typing import List, Dict
from jinja2 import Template

from TemplateCreator.template_options import TemplateOptions
from TemplateCreator.template_options import TemplateInfo


class TemplatesCreator:
    templates: List[TemplateInfo]
    folder_name: str
    template_name: str
    template_info: TemplateInfo
    working_dir = os.path.dirname(os.path.realpath(__file__))
    templates_dir = join(working_dir, 'templates')
    options: TemplateOptions

    def __init__(self, template_name, folder_name):
        self.folder_name = folder_name
        self.template_name = template_name
        self.options = TemplateOptions(folder_name)
        self.template_info = self.options.get_template_info(self.get_template_name_underscore(template_name))
        template_dictionary: Dict[str, List[TemplateInfo]] = self.options.get_batch_templates_dictionary()
        self.templates = template_dictionary.get(template_name)

        if not self.templates:
            raise Exception(f'no templates found for {template_name}')

    def create(self):
        if self.is_batch_template():
            self.create_folder()
        self.create_files()

    def is_batch_template(self) -> bool:
        return self.template_info.is_batch

    def create_folder(self):
        path = normpath(join(os.getcwd(), self.folder_name))
        try:
            os.mkdir(path)
        except OSError:
            print(f'FAILED creating {path}. Directory already exists')
            exit(1)
        else:
            print(f'Successfully created the directory {path}')

    def create_files(self):
        for template in self.templates:
            populated_template = self.get_template(template.name)
            file_name = template.file_name

            if not self.is_batch_template():
                dir_path = './'
            else:
                dir_path = self.folder_name

            print(normpath(join(dir_path, file_name)))
            self.write_to_file(populated_template, normpath(join(dir_path, file_name)))
            print(f'{file_name} was written successfully')

    @staticmethod
    def get_template_name_underscore(template_name):
        return template_name.replace('-', '_')

    def get_template(self, template_name: str):
        suffix = self.options.get_suffix(self.get_template_name_underscore(template_name))
        for filename in os.listdir(self.templates_dir):
            if template_name in filename:
                template_path = normpath(join(self.templates_dir, filename))
                string_template = self.file_to_string(template_path)
                t = Template(string_template)
                class_name = self.get_camel_cased_string(self.folder_name)
                return t.render(
                    component_name=class_name + suffix,
                    folder_name=self.folder_name
                )

    @staticmethod
    def file_to_string(path: str):
        with open(path, 'r') as file:
            return file.read()

    @staticmethod
    def write_to_file(file_content: str, file_name: str):
        f = open(file_name, 'w')
        f.write(file_content)
        f.close()

    @staticmethod
    def get_camel_cased_string(word: str):
        return ''.join(x.capitalize() or '-' for x in word.split('-'))
