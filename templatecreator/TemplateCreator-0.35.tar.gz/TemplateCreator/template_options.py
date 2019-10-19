from dataclasses import dataclass, field


@dataclass
class TemplateInfo:
    # name should be the same as template file name (no extension)
    name: str
    # name of the file to create
    file_name: str
    # suffix appended to class names
    suffix: str = field(default='')


@dataclass
class Suffixes:
    component = 'Component'
    reducer = 'Reducer'
    service = 'Service'
    state = 'State'


@dataclass
class TemplateOptions:
    folder_name: TemplateInfo
    function_component: TemplateInfo
    class_component: TemplateInfo
    styles: TemplateInfo
    css_module: TemplateInfo
    readme: TemplateInfo
    test: TemplateInfo
    state: TemplateInfo
    actions: TemplateInfo
    reducer: TemplateInfo
    service: TemplateInfo

    def __init__(self, folder_name: str):
        self.function_component = TemplateInfo(
            name='function-component',
            file_name=f'{folder_name}.component.jsx',
            suffix=Suffixes.component
        )
        self.class_component = TemplateInfo(
            name='class-component',
            file_name=f'{folder_name}.component.jsx',
            suffix=Suffixes.component
        )
        self.styles = TemplateInfo(name='styles', file_name=f'{folder_name}.styles.js')
        self.css_module = TemplateInfo(name='css-module', file_name=f'{folder_name}.styles.scss')
        self.readme = TemplateInfo(
            name='readme',
            file_name=f'{folder_name}.readme.md',
            suffix=Suffixes.component
        )
        self.test = TemplateInfo(
            name='test',
            file_name=f'{folder_name}.test.jsx',
            suffix=Suffixes.component
        )
        self.state = TemplateInfo(
            name='state',
            file_name=f'{folder_name}.state.js',
            suffix=Suffixes.state
        )
        self.actions = TemplateInfo(name='actions', file_name=f'{folder_name}.actions.js')
        self.reducer = TemplateInfo(
            name='reducer',
            file_name=f'{folder_name}.reducer.js',
            suffix=Suffixes.reducer
        )
        self.service = TemplateInfo(
            name='service',
            file_name=f'{folder_name}.service.js',
            suffix=Suffixes.service
        )

    def get_suffix(self, template_name):
        try:
            template = self.__getattribute__(template_name)
            return template.suffix
        except ModuleNotFoundError:
            return ""

    def get_batch_templates_dictionary(self):
        return {
            'shared-component': [
                self.function_component,
                self.styles,
                self.readme,
                self.test
            ],
            'class-component': [
                self.class_component,
                self.css_module
            ],
            'function-component': [
                self.function_component,
                self.css_module
            ],
            'state': [
                self.state,
                self.reducer,
                self.actions
            ],
            'service': [
                self.service
            ]
        }
