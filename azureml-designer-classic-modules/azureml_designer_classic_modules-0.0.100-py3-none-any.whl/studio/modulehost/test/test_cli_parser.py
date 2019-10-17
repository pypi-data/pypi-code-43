import pytest
import argparse

from azureml.studio.modulehost.cli_parser import _make_action, CliArgumentParser


@pytest.fixture
def expected_dict():
    return {
        'dest1': {
            'key11': 'val11',
            'key22': 'val22',
        },
        'dest2': {
            'key21': 'val21',
            'key22': 'val22',
        },
    }


def test_make_action(expected_dict):
    parser = argparse.ArgumentParser()
    args = []
    for dest, kv in expected_dict.items():
        for k, v in kv.items():
            arg = f'--{dest}-{k}'
            parser.add_argument(
                arg,
                type=str,
                dest=dest,
                action=_make_action(k),
            )
            args.append(f'{arg}={v}')
    result_dict = vars(parser.parse_args(args))
    assert result_dict == expected_dict


@pytest.mark.parametrize(
    'module, args, input_dict, output_dict, param_dict',
    [
        (
            'enter_data', [
                '--module-name=azureml.studio.modules.dataio.enter_data',
                '--data-format=CSV',
                '--data=a,b,c',
                '--dataset=dataset'
            ], {
            }, {
                'dataset': 'dataset',
            }, {
                'Data': 'a,b,c',
                'DataFormat': 'CSV',
            }
        ),
        (
            'add_rows', [
                '--module-name=azureml.studio.modules.datatransform.manipulation.add_rows',
                '--dataset1=gen',
                '--dataset2=gen',
                '--results-dataset=results',
            ], {
                'Dataset1': 'gen',
                'Dataset2': 'gen',
            }, {
                'Results dataset': 'results',
            }, {
            }
        ),
        (
           'import_data', [
                '--module-name=azureml.studio.modules.dataio.import_data',
                '--account-key=i9T9e3XGzovFJWMnrqXeSg==',
            ], {
            }, {
            }, {
                'Account Key': 'afasdfdasfas',
            },
        ),
    ]
)
def test_cli_parser(module, args, input_dict, output_dict, param_dict):
    parser = CliArgumentParser(args)
    assert parser.output_port_dict == output_dict
    assert parser.param_dict == param_dict
    for k, v in parser.input_port_dict.items():
        assert v.folder == input_dict.get(k)
