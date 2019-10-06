import logging
import pathlib
import sys

from .              import logConfig
from .config        import Configurable
from .config        import SettingManager
from .registry      import Registry
from .signalcontrol import SignalControl
from .util.signal   import Signal

_logger = logging.getLogger(__name__)

class AppInit(Configurable):
    """Handles application initialization, loading the main module components"""

    #TODO: Change this to be a platform specific location!
    configdir    = '~/.moon-nectar'

    initComplete = Signal() # App initialization is complete

    @classmethod
    def create_config(cls, parser):
        parser.description = 'Moon Nectar Music App'

        parser.add('--config',
                is_config_file_arg = True,
                help               = "Specify a configuration file for startup options")

        parser.add('--config-write',
                is_write_out_config_file_arg = True,
                help                         = "Write this command line to a configuration file")

        #XXX This is a horrible hack!
        #XXX Find something better!
        parser.add_argument('--plugins-disabled',
                action  = 'store_true',
                help    = 'Disable Plugin Loading')

    def init(self, args=sys.argv[1:], configdir = None):
        self.configdir    = pathlib.Path(configdir or self.configdir).expanduser()
        self.configfile   = self.configdir / 'config.ini'
        self.appstatefile = self.configdir / 'appstate.ini'
        config_files        = []

        # Ensure the user configfile exists
        # ... Because configargparse doesn't seem to know what to do with a missing config file!
        # ... XXX Look Into This!  Probably a better solution ....
        if not self.configdir.exists():  self.configdir.mkdir()
        if not self.configfile.exists(): self.configfile.touch()

        # Create the settings manager and load any existing settings
        self.settings_manager = SettingManager(self, self.appstatefile)

        # Parse the command line and/or configuration file
        # ... This is a first pass to parse main application options
        # ... necessary in order to load plugin paths!
        # ... unknown options will be ignored here.
        self.config = Configurable.config_parse_args(
            args,
            help=False,
            unknown_ok=True,
            default_config_files=[str(self.configfile)]
        )
        _logger.debug("INIT: Configurable: Parse Main App Args")

        # import all plugins
        # ... Do this immediately after the initial argument parsing
        # ... So that plugins can be imported before further app setup
        # ... But after config options modify plugin detection and import
        _logger.debug("INIT: Plugins: Import")
        Registry.load_entry_points()

        # Parse the command line and/or configuration file (with plugin arguments)
        # ... This is the real command line / config file parser
        # ... Now that plugins are loaded, all available options are used
        # ... Unknown options cause an error here!
        _logger.debug("INIT: Configurable: Parse All Args")
        self.config = Configurable.config_parse_args(
            args, help=True, unknown_ok=False, default_config_files=[self.configfile]
        )

        # Create the signal control class
        self.signal   = SignalControl(self)

        # Create the library
        _logger.debug("INIT: Library")
        Registry.Library.create(self)

        _logger.debug("INIT: External Controllers")
        Registry.Control.create(self)

        _logger.debug("INIT: Backend")
        Registry.Backend.create(self)

        # Create the User Interface
        _logger.debug("INIT: User Interface")
        Registry.UI.create(self)

        _logger.debug("INIT: Complete!")
        self.signal.initComplete.emit()

    def run(self):
        # Run the UI
        self.ui.run()

def run_app():
    app = AppInit()
    app.init()
    return app.run()
