"""Module containing the output handler base class and default handlers."""
import pickle
import tempfile

try:
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze

from .base import OutputHandler
from .db import DB, DbModel
from .utils import load_project_config
from .utils import LOGGER


class PrintHandler(OutputHandler):
    """Prints the results."""

    def handle_result(self, result):
        """
        Prints the results of an evaluator.

        Args:
            result: passed from an evaluator.
        """
        print(result)


class PickleBackupHandler(OutputHandler):
    """Pickes the results."""

    def __init__(self, directory=None):
        """
        Intitializes the handler.

        Args:
            directory: the directory where the pickle file gets stored.
        """
        self.directory = directory

    def handle_result(self, result):
        """
        Pickles the results of an evaluator.

        Args:
            result: passed from an evaluator.
        """
        # TODO: think of a useful naming/storage strategy
        with tempfile.NamedTemporaryFile(
                dir=self.directory, suffix='.result',
                delete=False) as output_file:

            pickle.dump(result, output_file)
            LOGGER.debug(f'wrote pickle to {output_file.name}')


class PostGresOutputHandler(OutputHandler):
    """Stores the meta-data, configuration and results of a run in the DB."""

    def __init__(self, table='results'):
        """
        Creates a new instance.

        Args:
            table: the name of the database table used to store the results.
        """
        self.config = load_project_config()
        self.engine = DB.engine
        self.session = DB.session

    def _get_requirements(self):
        return list(freeze.freeze())

    def handle_result(self, result):
        """
        Stores the result of an evaluator in the DB.

        Args:
            result: passed from an evaluator.
        """
        commit_id, remote_url, is_dirty = result['git_info']
        if 'project' in self.config and 'name' in self.config['project']:
            project_name = self.config['project']['name']
        else:
            project_name = result['sourcefile']
        db_entry = DbModel(
            project_name=project_name,
            git_commit_id=commit_id,
            git_remote_url=remote_url,
            git_is_dirty=is_dirty,
            sourcefile=result['sourcefile'],
            config=result['config_file'],
            dataloader=result['dataloader'],
            pipeline=result['pipeline'],
            evaluator=result['evaluator'],
            outcome=result['outcome'],
            platform=result['platform'],
            requirements=self._get_requirements())

        session = self.session()

        session.add(db_entry)
        session.commit()
