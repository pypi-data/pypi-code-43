import os
import json

from myelin.metric import MetricClient

__HPO_CLIENT__ = MetricClient()


def get_hpo_params():
    hpo_params = os.environ.get('HPO_PARAMS')
    if hpo_params is None:
        return None
    return extract_hpo_params(json.loads(hpo_params))


def publish_result(loss_value, loss_metric):
    info_map = {'loss value': loss_value}
    config_map = get_hpo_params()
    config_id = config_map['config-id']
    budget = config_map['budget']
    config = extract_hpo_params(config_map)

    __HPO_CLIENT__.post_update(loss_metric, loss_value)
    __HPO_CLIENT__.post_result(config_id, config, budget, loss_value, info_map)


def extract_hpo_params(config_map):
    return json.loads(config_map["hpo-conf"])
