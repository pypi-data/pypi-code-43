import os
from collections.abc import MutableSequence
import json
import glob

import yaml
from cerberus import Validator
import requests

from .helpers import fail, success, configure_logger, enable_debug, get_logger


logger = configure_logger()


class ArrayVariable(MutableSequence):
    """

    Example:

    >>> env = {
    ...        'EXTRA_ARGS_COUNT': 3,
    ...        'EXTRA_ARGS_0': '--description',
    ...        'EXTRA_ARGS_1': 'text containing spaces',
    ...        'EXTRA_ARGS_2': '--verbose'}
    >>>
    >>> array_variable = ArrayVariable('EXTRA_ARGS', env)
    >>> array_variable[2]
    '--verbose'
    """

    def __init__(self, name, env):
        self._name = name
        self._count = int(env.get(f'{name}_COUNT', '0'))
        self._variables = [env.get(f'{name}_{i}') for i in range(self._count)]

    def __getitem__(self, i):
        return self._variables[i]

    def __setitem__(self, index, value):
        self._variables[index] = value

    def __delitem__(self, index):
        del self._variables[index]

    def insert(self, index, value):
        self._variables.insert(index, value)

    def __len__(self):
        return len(self._variables)

    @classmethod
    def from_list(cls, name, lst):
        array_variable = cls(name, {})
        for var in lst:
            array_variable.append(var)
        return array_variable

    def decompile(self):
        """
        
        Example

        >>> var = ArrayVariable.from_list('TEST', ['foo','bar', 'baz'])
        >>> var.decompile()
        {'TEST_0': 'foo', 'TEST_1': 'bar', 'TEST_2': 'baz', 'TEST_COUNT': 3}

        """
        dct = {f"{self._name}_{i}": value for i, value in enumerate(self._variables)}
        dct[f"{self._name}_COUNT"] = len(self)
        return dct





class SharedData:
    """This is an interface to the shared pipes data directory

    Example:

    >>> shared_data = SharedData('/tmp')
    >>> shared_data.get_variable('foo') is None
    True
    >>> shared_data.set_variable('foo', 'bar')
    >>> shared_data.get_variable('foo')
    'bar'
    >>> shared_data.purge()

    Example storing complex data

    >>> shared_data = SharedData('/tmp')
    >>> shared_data.set_variable('my_data', {'my_variable': 'my_value'})
    >>> shared_data.get_variable('my_data')['my_variable']
    'my_value'
    >>> shared_data.purge()
    """

    def __init__(self, path):
        self._path = path
        self._shared_json_file = os.path.join(self._path, '_shared_variables.json')


    def get_json(self, name):
        with open(os.path.join(self._path, name), 'r') as fp:
            return json.load(name)

    def store_json(self, name, data):
        with open(os.path.join(self._path, name), 'w+') as fp:
            return json.dump(data, fp)

    def set_variable(self, key, value):
        """Set the shared varialbe

        Args:
            key (str): Variable key
            value: The value of the variable
        """
        try:
            with open(self._shared_json_file, 'r') as storage:
                data = json.loads(storage.read())
            with open(self._shared_json_file, 'w') as storage:
                data[key] = value
                json.dump(data, storage)
        except FileNotFoundError:
            with open(self._shared_json_file, 'w+') as storage:
                data = {key: value}
                json.dump(data, storage)

    def get_variable(self, key):
        """Get the value of some variable

        Args:
            key (str): Variable key

        Returns:
            The value of the variable.
        """
        try:
            with open(self._shared_json_file, 'r') as storage:
                data = json.load(storage)
                return data.get(key)
        except FileNotFoundError as error:
            return None

    def purge(self):
        """
        Purge all shared data
        """
        files = glob.glob(os.path.join(self._path, '_shared_*'))
        for f in files:
            os.remove(f)



class Pipe:
    """Base class for all pipes. Provides utitilfdfites to work with configuration, validation etc.

    Attributes:
        variables (dict): Dictionary containing the pipes variables.
        schema (dict): Dictionary with the pipe parameters shema in the cerberus format.
        env (dict): Dict-like object conitining pipe parameters. This is usually the environment variables that 
            you get from os.environ

    Args:
        pipe_metadata (dict): Dictionary containing the pipe metadata
        schema (dict): Shema for pipe variables.
        
    Pipe variables validation
        Pip variables validation is done at the time of initializing a pipe. The environment variables are
        validated against the schema provided. See https://docs.python-cerberus.org/en/stable/ for more 
        details on how to specify schemas.

    """

    def fail(self, message):
        """Fail the pipe and exit.

        Args:
            message (str): Error message to show.
        """
        fail(message=message)

    def success(self, message, do_exit=False):
        """Show a success message.

        Args:
            message (str): Message to print
            do_exit (bool): Call sys.exit or not

        """
        success(message, do_exit=do_exit)

    def log_info(self, message):
        """Log an info message

        >>> pipe = Pipe(schema={})
        >>> pipe.log_info('hello')

        """
        return self.logger.info(message)

    def log_error(self, message):
        """Log an error message

        >>> pipe = Pipe(schema={})
        >>> pipe.log_info('hello')

        """

        return self.logger.error(message)

    def log_debug(self, message):
        """Log a debug message

        >>> pipe = Pipe(schema={})
        >>> pipe.log_info('hello')

        """
        return self.logger.debug(message)

    def log_warning(self, message):
        """Log a warning message

        >>> pipe = Pipe(schema={})
        >>> pipe.log_info('hello')

        """
        return self.logger.warning(message)

    def enable_debug_log_level(self): # pragma: no cover
        """Enable the DEBUG log level."""

        if self.get_variable('DEBUG'):
            self.logger.setLevel('DEBUG')

    def __init__(self, pipe_metadata=None, schema=None, env=None, logger=logger, check_for_newer_version=False):
        if pipe_metadata is None:
            pipe_metadata = {}
        if env is None:
            self.env = os.environ.copy()
        else:
            self.env = env

        self.metadata = pipe_metadata

        self.variables = None
        self.schema = schema
        self.logger = logger
        # validate pipe parameters
        self.variables = self.validate()
        self.enable_debug_log_level()
        if check_for_newer_version:
            self.check_for_newer_version()

    def check_for_newer_version(self):
        """Check if a newer version is available and show a warning message

        >>> metadata = {'image': 'bitbucketpipelines/aws-ecs-deploy:0.0.3', 'repository': 'https://bitbucket.org/atlassian/aws-ecs-deploy'}
        >>> pipe = Pipe(pipe_metadata=metadata, schema={})
        >>> pipe.check_for_newer_version()
        True
        """
        image = self.metadata.get('image')
        if image is None:
            return False
        current_version = image.split(':')[1]
        repo_url = self.metadata.get('repository')
        response = requests.get(f"{repo_url}/raw/master/pipe.yml")
        if not response.ok:
            self.log_warning('Failed to get the latest pipe version info')
        pipe_yml = yaml.safe_load(response.content)
        latest_version = pipe_yml.get('image').split(':')[1]

        if tuple(map(int, latest_version.split('.'))) > tuple(map(int, current_version.split('.'))):
            self.log_warning(f'You are using the {current_version} version of the pipe, but the {latest_version} is already available!')
            return True



    def validate(self):
        """Validates the environment variables against a provided schema.

        Variable schema is a dictionary in a cerberus format. See https://docs.python-cerberus.org/en/stable/ 
        for more details about this library and validation rules.

        """
        if self.schema is None:
            schema = self.metadata['variables']
        else:
            schema = self.schema

        validator = Validator(
            schema=schema, purge_unknown=True)
        env = {}
        for key, value in self.env.items():
            if key in schema:
                try:
                    env[key] = yaml.safe_load(value)
                except yaml.scanner.ScannerError:
                    # keep a string value
                    env[key] = value

        for key, key_schema in schema.items():
            if key_schema.get('type') == 'list':
                env[key] = ArrayVariable(key, self.env)

        if not validator.validate(env):
            self.fail(
                message=f'Validation errors: \n{yaml.dump(validator.errors, default_flow_style = False)}')
        validated = validator.validated(env)
        return validated

    def get_variable(self, name):
        """Retrive a pipe variable.

        Args:
            name (str): The name of a variable.

        Returns:
            The value of the variable.
        """

        return self.variables.get(name)

    def run(self):
        """Run the pipe.

        The main entry point for a pipe execution. This will do
        all the setup steps, like enabling debug mode if configure etc.
        """
        self.enable_debug_log_level()
