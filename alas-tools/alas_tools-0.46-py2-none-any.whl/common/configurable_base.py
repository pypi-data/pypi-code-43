class ConfigurableManagerBase(object):
    def __init__(self, **kwargs):
        self.set_all_configs(**kwargs)

    def set_all_configs(self, **kwargs):
        if 'deploy_env' in kwargs:
            self.deploy_env = kwargs.pop('deploy_env')

        if 'storage_access_config' in kwargs:
            self.storage_access_config = kwargs.pop('storage_access_config')

        if 'firebase_access_config' in kwargs:
            self.firebase_access_config = kwargs.pop('firebase_access_config')

        if 'indexer_access_config' in kwargs:
            self.indexer_access_config = kwargs.pop('indexer_access_config')

        if 'whatsapp_access_config' in kwargs:
            self.whatsapp_access_config = kwargs.pop('whatsapp_access_config')

        if 'google_maps_access_config' in kwargs:
            self.google_maps_access_config = kwargs.pop('google_maps_access_config')

        if 'task_queue_handler_mapping' in kwargs:
            self.task_queue_handler_mapping = kwargs.pop('task_queue_handler_mapping')

        if 'device_magic_access_config' in kwargs:
            self.device_magic_access_config = kwargs.pop('device_magic_access_config')

        if 'render_access_config' in kwargs:
            self.render_access_config = kwargs.pop('render_access_config')

        if 'sendgrid_access_config' in kwargs:
            self.sendgrid_access_config = kwargs.pop('sendgrid_access_config')

        if 'proxy_access_config' in kwargs:
            self.proxy_access_config = kwargs.pop('proxy_access_config')

        if 'api_access_config' in kwargs:
            self.api_access_config = kwargs.pop('api_access_config')

        if 'web_access_config' in kwargs:
            self.web_access_config = kwargs.pop('web_access_config')

    def get_all_configs(self):
        all_configs = {}

        if self.deploy_env:
            all_configs.update({'deploy_env': self.deploy_env})

        if self.storage_access_config:
            all_configs.update({'storage_access_config': self.storage_access_config})

        if self.firebase_access_config:
            all_configs.update({'firebase_access_config': self.firebase_access_config})

        if self.indexer_access_config:
            all_configs.update({'indexer_access_config': self.indexer_access_config})

        if self.whatsapp_access_config:
            all_configs.update({'whatsapp_access_config': self.whatsapp_access_config})

        if self.google_maps_access_config:
            all_configs.update({'google_maps_access_config': self.google_maps_access_config})

        if self.task_queue_handler_mapping:
            all_configs.update({'task_queue_handler_mapping': self.task_queue_handler_mapping})

        if self.device_magic_access_config:
            all_configs.update({'device_magic_access_config': self.device_magic_access_config})

        if self.render_access_config:
            all_configs.update({'render_access_config': self.render_access_config})

        if self.sendgrid_access_config:
            all_configs.update({'sendgrid_access_config': self.sendgrid_access_config})

        if self.proxy_access_config:
            all_configs.update({'proxy_access_config': self.proxy_access_config})

        if self.api_access_config:
            all_configs.update({'api_access_config': self.api_access_config})

        if self.web_access_config:
            all_configs.update({'web_access_config': self.api_access_config})

        return all_configs