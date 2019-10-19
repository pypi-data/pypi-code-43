import minetorch
from . import process_env as env
import torch
from featurize_jupyterlab import core, package_manager, g
from featurize_jupyterlab.transform import Compose
from .plugins import CorePlugin


def init_component(component_config, extra_parameters={}):
    component_name = component_config['name']
    component_type = component_config['type']
    klass = next((klass for klass in core.registed_components() if klass.name == component_name), None)
    if klass is None:
        raise Exception(
            f"Could not found {component_type}: {component_name}, "
            f"be sure to add the coresponding package before use it"
        )
    return klass(**{
        **component_config.get('parameters', {}),
        **extra_parameters
    })



def main(config_file):
    env.init_process_env(config_file)
    blocks = env.config['blocks']

    train_dataloader = Compose()
    val_dataloader = Compose()

    for component_config in blocks['Train Dataloader']:
        train_dataloader.add(init_component(component_config))
    for component_config in blocks['Validation Dataloader']:
        val_dataloader.add(init_component(component_config))

    train_dataset, val_dataset = init_component(blocks['Dataset'][0], extra_parameters={
        'train_dataloader': train_dataloader,
        'val_dataloader': val_dataloader
    })()

    model = init_component(blocks['Model'][0])()

    optimizer = init_component(blocks['Optimizer'][0], extra_parameters={
        'model': model,
    })()

    loss = init_component(blocks['Loss'][0])

    trainer = minetorch.Trainer(
        alchemistic_directory='./log',
        model=model,
        optimizer=optimizer,
        train_dataloader=train_dataset,
        val_dataloader=val_dataset,
        loss_func=loss,
        drawer=None,
        logger=env.logger,
        plugins=[CorePlugin()]
    )

    try:
        trainer.train()
    except Exception as e:
        env.logger.exception(f'unexpected error in training process: {e}')
