import minetorch
from . import process_env as env
import torch
from featurize_jupyterlab import core, package_manager, g
from .plugins import CorePlugin


def init_component(component_type, component_config):
    component_name = component_config['name']
    component_settings = component_config.get('parameters', {})
    if component_type[-1] == 's':
        plural_component_cls_name = f'{component_type}es'
    else:
        plural_component_cls_name = f'{component_type}s'
    register_components = getattr(getattr(core, component_type), f'registed_{plural_component_cls_name}')
    component = next((component for component in register_components if component.name == component_name), None)
    if component is None:
        raise Exception(
            f"Could not found {component_type}: {component_name}, "
            f"be sure to add the coresponding package before use it"
        )
    return component.func(**component_settings)


def main(config_file):
    env.init_process_env(config_file)
    components = env.config['components']
    g.dataset = init_component('dataset', components['dataset'])
    g.dataloader = torch.utils.data.DataLoader(g.dataset, batch_size=256, shuffle=True)
    # TODO: add dataflow
    # dataflow = init_component('dataflow', env.config['dataflow'])
    g.model = init_component('model', components['model'])
    g.optimizer = init_component('optimizer', components['optimizer'])
    g.loss = init_component('loss', components['loss'])

    trainer = minetorch.Trainer(
        alchemistic_directory='./log',
        model=g.model,
        optimizer=g.optimizer,
        train_dataloader=g.dataloader,
        loss_func=g.loss,
        drawer=None,
        logger=env.logger,
        plugins=[CorePlugin()],
    )

    try:
        trainer.train()
    except Exception as e:
        env.logger.exception(f'unexpected error in training process: {e}')
