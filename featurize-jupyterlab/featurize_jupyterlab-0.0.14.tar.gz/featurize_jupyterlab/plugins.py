from . import process_env as env
from . import constants as C

class Plugin():

    registed_plugins = []

    @classmethod
    def register(cls, plugin):
        cls.registed_plugins.append(plugin)

    def after_init(self, payload, trainer):
        pass

    def before_epoch_start(self, payload, trainer):
        pass

    def after_epoch_end(self, payload, trainer):
        pass

    def before_train_iteration_start(self, payload, trainer):
        pass

    def after_train_iteration_end(self, payload, trainer):
        pass

    def before_val_iteration_start(self, payload, trainer):
        pass

    def after_val_iteration_end(self, payload, trainer):
        pass

    def before_checkpoint_persisted(self, payload, trainer):
        pass

    def after_checkpoint_persisted(self, payload, trainer):
        pass

    def before_quit(self, payload, trainer):
        pass


class CorePlugin(Plugin):
    """The Minetorch Trainer can be runned independently.
    This plugin activate Trainer with the ability to communicate with the
    Minetorch Server with some basic data collection such as loss.
    """
    def after_init(self, payload, trainer):
        env.rpc.create_graph('train_epoch_loss')
        env.rpc.create_graph('val_epoch_loss')
        env.rpc.create_graph('train_iteration_loss')

    def after_epoch_end(self, payload, trainer):
        env.rpc.add_point('train_epoch_loss', payload['train_loss'])
        env.rpc.add_point('val_epoch_loss', payload['val_loss'])

    def after_train_iteration_end(self, payload, trainer):
        env.rpc.add_point('train_iteration_loss', payload['loss'])


class TestLoggerPlugin(Plugin):
    """This is just for dev test"""
    def before_epoch_start(self, payload, trainer):
        env.logger.error('this is a error')
        env.logger.debug('this is a debug')
        env.logger.info('this is a info')
        env.logger.warn('this is a warning')
