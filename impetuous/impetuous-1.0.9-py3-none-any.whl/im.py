import logging
from contextlib import contextmanager
from datetime import timedelta

import attr
from sqlalchemy import create_engine

from impetuous.config import get_config
from impetuous.data import DATA_PATH, ensure_sane
from impetuous.ext import Ext, LudicrousConditions
from impetuous.ext.freshdesk import Freshdesk
from impetuous.ext.jira import Jira
from impetuous.interaction import Interaction, impetuous_access_control

logger = logging.getLogger(__name__)

NOT_EXT_SECTIONS = 'DEFAULT', 'impetuous'
API_CLASSES = {Jira.identifier: Jira,
               Freshdesk.identifier: Freshdesk}


@attr.s()
class Settings(object):
    round_durations_to_minute = attr.ib(default=True)


class Impetuous(object):
    """ Base program behaviour. TODO dissolve into nothing...?
    """
    # TODO cache most of these things? Or require explicit loading so state can
    # be invalidated explicitly.

    api_classes = API_CLASSES

    def __init__(self, dbecho=False):
        # TODO load config and settings from user or something? For one day
        # when this is a multi-user system ...
        try:
            self.config = get_config()
        except FileNotFoundError as e:
            logger.debug(_("Config could not be loaded: %r"), e)
            self.config = None
            self.config_error = e
        else:
            self.config_error = None
        self.settings = Settings()  # TODO load from impetuous section in config
        self.access_control = impetuous_access_control
        self.engine = create_engine(f'sqlite:///{DATA_PATH}', echo=dbecho)
        ensure_sane(self.engine)

    @contextmanager
    def interact(self, agent):
        with self.engine.connect() as conn:
            i = Interaction(conn, agent, self.access_control)
            with conn.begin():
                yield i

    def get_config_or_none(self):
        return self.config

    def get_config_or_empty(self):
        if self.config is None:
            return {}
        else:
            return self.config

    def get_config_or_quit(self):
        if self.config_error is not None:
            logger.error(self.config_error)
            logger.error(_("Try creating that file, see the readme for some ideas of what to put in it."))
            raise SystemExit(1)
        else:
            return self.config

    def get_entry_submissions(self, *entries):
        """
        Returns a list of module, entry, submission tuples.
        Ordered by module and entry for easy grouping.
        """
        # TODO don't call this so often and cache the dumb thing better ...
        for __, ext in self.section_exts(self.get_config_or_quit()):
            try:
                for entry, submission in ext.api.discover(self, *entries):
                    logger.debug(_("%s found submission %r."), ext.name, submission)
                    yield ext, entry, submission
            except LudicrousConditions as e:
                logger.warning(_("%s could not discover submissions") + ': %s. %s', ext.name, e.error, e.suggestion)

    def section_apis(self, config):
        """ Return section, API class pair.
        """
        for __, section in config.items():
            if section.name == 'DEFAULT':
                continue
            if 'api' in section:
                ident = section['api']
                if ident in self.api_classes:
                    api = self.api_classes[ident].from_config(section)
                    yield section, api
            else:
                logger.debug("Unrecognized section %s.", section)

    def section_exts(self, config):
        """ Returns section, Ext class pair.
        """
        for section, api in self.section_apis(config):
            name = section.get('name', section.name)
            assert name, "Unnamed sections are for jerks"
            abbr = section.get('abbr', name[0].upper())
            yield section, Ext(api=api, name=name, abbr=abbr)
