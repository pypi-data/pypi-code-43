from dataclasses import dataclass


@dataclass
class TemplateInfo:
    name: str
    file_name: str


@dataclass
class TemplateOptions:
    folder_name: TemplateInfo
    function_component: TemplateInfo
    class_component: TemplateInfo
    styles: TemplateInfo
    css_styles: TemplateInfo
    readme: TemplateInfo
    test: TemplateInfo

    def __init__(self, folder_name: str):
        self.function_component = TemplateInfo(name='function-component', file_name=f'{folder_name}.component.jsx')
        self.class_component = TemplateInfo(name='class-component', file_name=f'{folder_name}.component.jsx')
        self.styles = TemplateInfo(name='styles', file_name=f'{folder_name}.styles.js')
        self.css_styles = TemplateInfo(name='css-module', file_name=f'{folder_name}.styles.scss')
        self.readme = TemplateInfo(name='readme', file_name=f'{folder_name}.readme.md')
        self.test = TemplateInfo(name='test', file_name=f'{folder_name}.test.jsx')

    def get_dictionary(self):
        return {
            'shared-component': [
                self.function_component,
                self.styles,
                self.readme,
                self.test
            ],
            'class-component': [
                self.class_component,
                self.css_styles
            ],
            'function-component': [
                self.function_component,
                self.css_styles
            ]
        }
