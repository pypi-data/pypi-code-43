import os
from os.path import join, normpath
from typing import List, Dict
from jinja2 import Template

from template_options import TemplateInfo, TemplateOptions


class TemplatesCreator:
    templates: List[TemplateInfo]
    folder_name: str

    def __init__(self, template_name, folder_name):
        self.folder_name = folder_name
        options = TemplateOptions(folder_name)
        template_dictionary: Dict[str, List[TemplateInfo]] = options.get_dictionary()
        self.templates = template_dictionary.get(template_name)

        if not self.templates:
            raise Exception(f'no templates found for {template_name}')

    def create(self):
        self.create_folder()
        self.create_files()

    def create_folder(self):
        path = normpath(join(os.getcwd(), self.folder_name))
        try:
            os.mkdir(path)
        except OSError:
            print(f'Creation of the directory {path} failed directory probably already exists')
        else:
            print(f'Successfully created the directory {path}')

    def create_files(self):
        for template in self.templates:
            populated_template = self.get_template(template.name)
            file_name = template.file_name
            self.write_to_file(populated_template, normpath(join(self.folder_name, file_name)))
            print(f'{file_name} was written successfully')

    def get_template(self, template_name: str):
        for filename in os.listdir('TemplateCreator/templates'):
            if template_name in filename:
                template_path = normpath(join('TemplateCreator/templates', filename))
                string_template = self.file_to_string(template_path)
                t = Template(string_template)
                class_name = self.get_component_name(self.folder_name)
                return t.render(component_name=class_name)

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
    def get_component_name(word: str):
        return ''.join(x.capitalize() or '-' for x in word.split('-')) + 'Component'
