from typing import List, Dict, ClassVar
import random
import string
import logging
import logging.config
import asyncio

from macrobase.cli import Cli, ArgumentParsingException
from macrobase.config import AppConfig, SimpleAppConfig
from macrobase.pool import DriversPool
# from macrobase.context import context

from macrobase.logging import get_logging_config
from macrobase_driver import MacrobaseDriver
from macrobase_driver.hook import HookNames

from structlog import get_logger

log = get_logger('macrobase')


class Application:

    def __init__(self, name: str = None):
        """Create Application object.

        :param loop: asyncio compatible event loop
        :param name: string for naming drivers
        :return: Nothing
        """
        self.name = name
        self.config = AppConfig()
        self._pool = None
        self._drivers: Dict[str, MacrobaseDriver] = {}

    def add_config(self, config: SimpleAppConfig):
        self.config.update(config)

    def get_driver(self, driver_obj: ClassVar[MacrobaseDriver], *args, **kwargs) -> MacrobaseDriver:
        driver = driver_obj(*args, **kwargs)
        driver.update_config(self.config)

        return driver

    def add_driver(self, driver: MacrobaseDriver, alias: str = None):
        if alias is None:
            alias = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
        self._drivers[alias] = driver

    def add_drivers(self, drivers: List[MacrobaseDriver]):
        [self.add_driver(d) for d in drivers]

    def _apply_logging(self):
        self._logging_config = get_logging_config(self.config)
        logging.config.dictConfig(self._logging_config)

    def _prepare(self):
        self._apply_logging()

    def run(self, argv: List[str] = None):
        if argv is None:
            argv = []

        self._prepare()

        try:
            Cli(list(self._drivers.keys()), self._action_start, self._action_list).parse(argv)
        except ArgumentParsingException as e:
            print(e.message)

    def _action_start(self, aliases: List[str]):
        if len(aliases) == 1:
            try:
                self._drivers.get(aliases[0]).run()
            finally:
                asyncio.get_event_loop().close()
        else:
            self._pool = DriversPool()
            self._pool.start([d for a, d in self._drivers.items() if a in aliases])

    def _action_list(self, aliases: List[str]):
        print(f"Available drivers to start: \n{[n for n in aliases]}")
