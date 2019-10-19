from featurize_jupyterlab import core
import json
import pytest

RealComponent = None
SomeDatasetComponent = None
AbstractComponent = None
OptionComponent = None


@pytest.fixture(scope='module', autouse=True)
def components():
    global RealComponent, SomeDatasetComponent, AbstractComponent, OptionComponent

    core.clear_registed_components()

    class RealComponent(core.Component):
        """This is a real component
        """
        def __call__(self):
            pass

    class SomeDatasetComponent(core.Dataset):
        """This is a dataset component
        """
        name = 'Name overrided'
        description = 'This is a overrided description'

        def __call__(self):
            pass


    class AbstractComponent(core.Component):
        """if a component has no __call__ method, then it
        is an abstract component
        """
        pass


    class OptionComponent(core.Dataflow):
        """A component with options
        """
        batch_size = core.Option(name='Batch Size', type='number', default=1)
        epochs = core.Option(type='number', default=4)
        remark = core.Option()
        metadata = {
            'banner': 'banner_url'
        }

        def __call__(self):
            return {
                'a': self.batch_size,
                'b': self.epochs,
                'c': self.remark
            }


def test_component_metainfo():
    assert RealComponent.name == 'RealComponent'
    assert RealComponent.description == 'This is a real component'
    assert RealComponent.meta == core.ComponentMeta

    assert SomeDatasetComponent.name == 'Name overrided'
    assert SomeDatasetComponent.description == 'This is a overrided description'
    assert SomeDatasetComponent.meta == core.ComponentMeta


def test_registed_components():
    assert len(core.registed_components()) == 3
    assert core.ComponentMeta.registed_components[0] == RealComponent
    assert core.ComponentMeta.registed_components[1] == SomeDatasetComponent
    assert core.ComponentMeta.registed_components[2] == OptionComponent


def test_options():
    assert len(RealComponent.options) == 0
    assert len(OptionComponent.options) == 3
    assert OptionComponent.options[0].key == 'batch_size'
    assert OptionComponent.options[0].name == 'Batch Size'
    assert OptionComponent.options[0].type == 'number'
    assert OptionComponent.options[0].required == True

    assert OptionComponent.options[1].key == 'epochs'
    assert OptionComponent.options[1].name == 'epochs'
    assert OptionComponent.options[1].type == 'number'
    assert OptionComponent.options[1].default == 4

    assert OptionComponent.options[2].type == 'string'


def test_formalize_component():
    user_settings = {'batch_size': 123, 'epochs': 321, 'remark': 'this is remark'}
    option = OptionComponent(**user_settings)
    result = option()

    assert result['a'] == 123
    assert result['b'] == 321
    assert result['c'] == 'this is remark'


def test_component_serialize():
    result = OptionComponent.to_json_serializable()
    assert result['name'] == 'OptionComponent'
    assert result['description'] == 'A component with options'
    assert result['metadata']['banner'] == 'banner_url'
    assert result['options'][0]['key'] == 'batch_size'


def test_component_type():
    class AnotherOptionComponent(OptionComponent):
        pass

    assert RealComponent.component_type is None
    assert SomeDatasetComponent.component_type == 'Dataset'
    assert AbstractComponent.component_type is None
    assert OptionComponent.component_type == 'Dataflow'
    assert AnotherOptionComponent.component_type == 'Dataflow'


def test_option_post_process():
    class OptionCallbackCompbonent(core.Dataflow):
        """A component with a callback option
        """
        some_json_string = core.Option(type='string', default=1, post_process=lambda x: json.loads(x))

        def __call__(self):
            return self.some_json_string

    component = OptionCallbackCompbonent(some_json_string='{"xxx": "yyy"}')
    result = component()
    assert "xxx" in result
    assert result["xxx"] == "yyy"
