import sys
import logging
from cliff.app import App
from cliff.commandmanager import CommandManager


class MicropipesCliApp(App):

    def __init__(self):
        super(MicropipesCliApp, self).__init__(
            description='micropipes cli',
            version='0.4',
            command_manager=CommandManager('mpipes'),
            deferred_help=True,
            )

    def initialize_app(self, argv):
        root_logger = logging.getLogger('')
        root_logger.setLevel(logging.ERROR)
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    myapp = MicropipesCliApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))