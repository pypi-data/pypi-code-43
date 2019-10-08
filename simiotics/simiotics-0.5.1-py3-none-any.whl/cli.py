"""
Simiotics command line interface
"""

import argparse
import json
from typing import Callable, Dict, Iterator, Tuple

from . import client
from .registry import data_pb2

def generate_command_handler(
        method_name: str,
        list_results: bool = False,
    ) -> Callable[[argparse.Namespace], None]:
    """
    Generates a function that can be used as a handler for an argparse `ArgumentParser` through the
    `func` keyword argument of the `set_defaults` method:
    https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.set_defaults

    This handler is assumed to represent a method call against a Simiotics client and the parameters
    to the client are expected to be set as environment variables (e.g. `SIMIOTICS_DATA_REGISTRY`).

    NOTE: The responsibility of matching the parsed Namespace object to the method arguments is left
    to the caller of this function.

    Args:
    method_name
        Name of the method to expose as an argparse command
    list_results
        Boolean argument, specifying whether or not the return value of the given method is a list
        (or an iterator)

    Returns: Function generated to handle calls to the given method
    """
    def handler(args: argparse.Namespace) -> None:
        """
        Handles an argparse.Namespace object by passing the corresponding arguments to a specific
        method on a Simiotics client object

        Args:
        args
            Arguments parsed by an argparse parser from the command line or a string or a list of
            strings

        Returns: None
        """
        simiotics = client.client_from_env()
        args_dict = vars(args)
        function_args = {key:args_dict[key] for key in args_dict if key != 'func'}
        method = simiotics.__getattribute__(method_name)
        result = method(**function_args)
        if list_results:
            for item in result:
                print(item)
        else:
            print(result)

    return handler

def read_string_from_file(filepath: str) -> str:
    """
    Reads the contents of the file at the given filepath and returns those contents as a string

    Args:
    filepath
        Path to the file to read from

    Returns: String contents of the file
    """
    with open(filepath, 'r') as ifp:
        contents = ifp.read()
    return contents

def samples_parser(raw_samples: str) -> Iterator[Tuple[str, str, str, Dict[str, str]]]:
    """
    Parses samples for register_data from a JSON representation of those samples.

    Each sample is expected to consist of:
    1. Source ID
    2. Sample ID
    3. String specification of sample (e.g. HTTP URL)
    4. Map from string keys to string values tagging the sample

    Args:
    raw_samples
        JSON string representation of the samples

    Returns: Iterator over the Python representation of the samples
    """
    samples_py = json.loads(raw_samples)
    return (tuple(sample) for sample in samples_py)

def generate_cli() -> argparse.ArgumentParser:
    """
    Generates the Simiotics CLI

    Args: None

    Returns: argparse.ArgumentParser which implements the Simiotics CLI
    """
    parser = argparse.ArgumentParser(description='Command-line interface to Simiotics APIs')

    subparsers = parser.add_subparsers(title='Methods')

    list_data_sources_command = 'list_data_sources'
    list_data_sources_parser = subparsers.add_parser(
        list_data_sources_command,
        help='List all the sources registered against a Simiotics Data Registry',
    )
    list_data_sources_parser.add_argument(
        '-o',
        '--offset',
        type=int,
        default=0,
        help='Offset from which to start listing',
    )
    list_data_sources_parser.add_argument(
        '-n',
        '--num-items',
        type=int,
        default=10,
        help='Number of items to list',
    )
    list_data_sources_handler = generate_command_handler(
        list_data_sources_command,
        list_results=True,
    )
    list_data_sources_parser.set_defaults(func=list_data_sources_handler)

    update_data_source_command = 'update_data_source'
    update_data_source_parser = subparsers.add_parser(
        update_data_source_command,
        help='Update a source registered against a Simiotics Data Registry',
    )
    update_data_source_parser.add_argument(
        '-s',
        '--source-id',
        type=str,
        required=True,
        help='ID for source to mark as updated',
    )
    update_data_source_parser.add_argument(
        '-m',
        '--message',
        type=str,
        default='',
        help='Update message',
    )
    update_data_source_handler = generate_command_handler(update_data_source_command)
    update_data_source_parser.set_defaults(func=update_data_source_handler)

    get_data_source_command = 'get_data_source'
    get_data_source_parser = subparsers.add_parser(
        get_data_source_command,
        help='Get a source registered against a Simiotics Data Registry',
    )
    get_data_source_parser.add_argument(
        '-s',
        '--source-id',
        type=str,
        required=True,
        help='ID for source to mark as updated',
    )
    get_data_source_handler = generate_command_handler(get_data_source_command)
    get_data_source_parser.set_defaults(func=get_data_source_handler)

    source_types = {
        'UNKNOWN': data_pb2.Source.SourceType.SOURCE_UNKNOWN,
        'FS': data_pb2.Source.SourceType.SOURCE_FS,
        'HTTP': data_pb2.Source.SourceType.SOURCE_HTTP,
        'S3': data_pb2.Source.SourceType.SOURCE_S3,
        'GCS': data_pb2.Source.SourceType.SOURCE_GCS,
    }
    register_data_source_command = 'register_data_source'
    register_data_source_parser = subparsers.add_parser(
        register_data_source_command,
        help='Register a source against a Simiotics Data Registry',
    )
    register_data_source_parser.add_argument(
        '-t',
        '--source-type',
        type=lambda key: source_types[key],
        required=True,
        help='Type of source; value must be one of {}'.format(', '.join(source_types)),
    )
    register_data_source_parser.add_argument(
        '-s',
        '--source-id',
        type=str,
        required=True,
        help='ID for source to mark as updated',
    )
    register_data_source_parser.add_argument(
        '-k',
        '--data-access-spec',
        type=str,
        required=True,
        help='Specification for accessing the data registered under the source',
    )
    register_data_source_parser.add_argument(
        '-r',
        '--description',
        type=str,
        default='',
        help='Description of the source',
    )
    register_data_source_handler = generate_command_handler(register_data_source_command)
    register_data_source_parser.set_defaults(func=register_data_source_handler)

    register_data_command = 'register_data'
    register_data_parser = subparsers.add_parser(
        register_data_command,
        help='Register data against a source in a Simiotics Data Registry',
    )
    register_data_parser.add_argument(
        'samples',
        type=samples_parser,
        help=(
            'JSON string represent a list of items of the form: '
            '[source_id, sample_id, sample_specifier, {<tag1>: <value1>, ..., <tagN>: <valueN>}]'
        )
    )
    register_data_handler = generate_command_handler(register_data_command, list_results=True)
    register_data_parser.set_defaults(func=register_data_handler)

    describe_data_command = 'describe_data'
    describe_data_parser = subparsers.add_parser(
        describe_data_command,
        help='Describe data registered against a given source in a Simiotics Data Registry',
    )
    describe_data_parser.add_argument(
        '-s',
        '--source-id',
        type=str,
        required=True,
        help='ID of registered source within which you would like to get data descriptions',
    )
    describe_data_parser.add_argument(
        '-i',
        '--data-ids',
        type=str,
        nargs='*',
        default=None,
        help='Restricted set of data IDs to describe',
    )
    describe_data_handler = generate_command_handler(describe_data_command, list_results=True)
    describe_data_parser.set_defaults(func=describe_data_handler)

    register_function_command = 'register_function'
    register_function_parser = subparsers.add_parser(
        register_function_command,
        help='Register a function in a Simiotics Function Registry',
    )
    register_function_parser.add_argument(
        '-k',
        '--key',
        type=str,
        required=True,
        help='Key that the function should be registered under',
    )
    register_function_parser.add_argument(
        '-c',
        '--code',
        type=read_string_from_file,
        required=True,
        help='Path to file containing the code',
    )
    register_function_parser.add_argument(
        '-t',
        '--tags',
        type=json.loads,
        default={},
        required=False,
        help='Tags to associate with the function (string-string key-value pairs)',
    )
    register_function_parser.add_argument(
        '-o',
        '--overwrite',
        action='store_true',
        help='Use this flag to indicate that function should be overwritten if key already exists'
    )
    register_function_handler = generate_command_handler(register_function_command)
    register_function_parser.set_defaults(func=register_function_handler)

    list_registered_functions_command = 'list_registered_functions'
    list_registered_functions_parser = subparsers.add_parser(
        list_registered_functions_command,
        help='List all the functions registered against a Simiotics Function Registry',
    )
    list_registered_functions_parser.add_argument(
        '-o',
        '--offset',
        type=int,
        default=0,
        help='Offset from which to start listing',
    )
    list_registered_functions_parser.add_argument(
        '-n',
        '--num-items',
        type=int,
        default=10,
        help='Number of items to list',
    )
    list_registered_functions_handler = generate_command_handler(
        list_registered_functions_command,
        list_results=True,
    )
    list_registered_functions_parser.set_defaults(func=list_registered_functions_handler)

    get_registered_function_command = 'get_registered_function'
    get_registered_function_parser = subparsers.add_parser(
        get_registered_function_command,
        help='Get a function registered against a Simiotics Function Registry',
    )
    get_registered_function_parser.add_argument(
        '-k',
        '--key',
        type=str,
        required=True,
        help='Function key',
    )
    get_registered_function_handler = generate_command_handler(get_registered_function_command)
    get_registered_function_parser.set_defaults(func=get_registered_function_handler)

    delete_registered_function_command = 'delete_registered_function'
    delete_registered_function_parser = subparsers.add_parser(
        delete_registered_function_command,
        help='Delete a function from a Simiotics Function Registry',
    )
    delete_registered_function_parser.add_argument(
        '-k',
        '--key',
        type=str,
        required=True,
        help='Function key',
    )
    delete_registered_function_handler = generate_command_handler(
        delete_registered_function_command
    )
    delete_registered_function_parser.set_defaults(func=delete_registered_function_handler)

    health_command = 'health'
    health_parser = subparsers.add_parser(health_command, help='Check registry health')
    health_handler = generate_command_handler(health_command)
    health_parser.set_defaults(func=health_handler)

    return parser

def main() -> None:
    """
    Runs the CLI
    """
    simiotics_cli = generate_cli()
    args = simiotics_cli.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
