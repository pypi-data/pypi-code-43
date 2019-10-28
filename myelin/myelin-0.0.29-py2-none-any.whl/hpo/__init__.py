import os
import json

from myelin.metric import MetricClient

__HPO_CLIENT__ = MetricClient()


def get_hpo_config():
    hpo_params = os.environ.get('HPO_PARAMS')
    if hpo_params is None:
        return {}
    return json.loads(hpo_params)


def get_hpo_params():
    hpo_params = get_hpo_config()
    if hpo_params == {}:
        return {}
    return extract_hpo_params(hpo_params)


def get_loss_metric():
    return os.environ["LOSS_METRIC"]


def publish_result(loss_value, loss_metric):
    info_map = {'loss value': loss_value}
    config_map = get_hpo_config()
    config_id = config_map['config-id']
    budget = config_map['budget']
    config = extract_hpo_params(config_map)

    __HPO_CLIENT__.post_update(loss_metric, loss_value)
    __HPO_CLIENT__.post_result(config_id, config, budget, loss_value, info_map)


def extract_hpo_params(config_map):
    return json.loads(config_map["hpo-conf"])
