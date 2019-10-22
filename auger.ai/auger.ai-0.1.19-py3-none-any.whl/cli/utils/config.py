class AugerConfig(object):
    """Modify configuration options in auger.yaml."""

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    def _with_config_yaml(decorated):
        def wrapper(self, *args, **kwargs) :
            auger_config = self.ctx.get_config('auger')
            general_config = self.ctx.get_config('config')
            decorated(
                self, auger_config.yaml, general_config.yaml, *args, **kwargs)
            auger_config.write()
            if auger_config != general_config:
                general_config.write()
            return self
        return wrapper

    @_with_config_yaml
    def config(self, auger_yaml, config_yaml, *args, **kwargs):
        config_yaml['name'] = kwargs.get('project_name', '')

        config_yaml['source'] = kwargs.get('source', '')
        auger_yaml['dataset'] = kwargs.get('data_set_name', '')
        config_yaml['target'] = kwargs.get('target', '')

        auger_yaml['experiment']['name'] = kwargs.get('experiment_name', '')
        model_type = kwargs.get('model_type', None)
        if model_type:
            auger_yaml['experiment']['metric'] = \
                'f1_macro' if model_type == 'classification' else 'r2'
        config_yaml['model_type'] = model_type or ''

    @_with_config_yaml
    def set_project(self, auger_yaml, config_yaml, project_name):
        config_yaml['name'] = project_name

    @_with_config_yaml
    def set_data_set(
        self, auger_yaml, config_yaml, data_set_name, data_set_source=None):
        auger_yaml['dataset'] = data_set_name
        if data_set_source:
            config_yaml['source'] = data_set_source

    @_with_config_yaml
    def set_experiment(
        self, auger_yaml, config_yaml, experiment_name, session_id=None):
        auger_yaml['experiment']['name'] = experiment_name
        auger_yaml['experiment']['experiment_session_id'] = session_id
