import os
import json

from myelin.metric import MetricClient

__HPO_CLIENT__ = MetricClient()


def get_hpo_params():
    hpo_params = os.environ.get('HPO_PARAMS')
    if hpo_params is None:
        return None
    return json.loads(hpo_params)


def publish_result(loss_value, loss_metric):
    info_map = {'loss value': loss_value}
    hpo_params = get_hpo_params()
    config_id = hpo_params['config-id']
    budget = hpo_params['budget']
    config = hpo_params.copy()
    del config['config-id']
    del config['budget']
    del config['task-id']
    del config['model-path']
    del config['data-path']

    __HPO_CLIENT__.post_update(loss_metric, loss_value)
    __HPO_CLIENT__.post_result(config_id, config, budget, loss_value, info_map)
