from __future__ import absolute_import
from __future__ import print_function
import os
from kubernetes import client, config
import requests
import logging

logging.basicConfig(level=logging.DEBUG)


class MetricClientKubernetes(object):
    group = 'monitoring.coreos.com'
    version = 'v1'
    plural = 'prometheusrules'
    metric_prefix = "metric/"

    def __init__(self, config_file, port=9091):
        self.port = port

        config.load_kube_config(config_file=config_file)
        configuration = client.Configuration()
        configuration.verify_ssl = False
        configuration.debug = True

        client.Configuration.set_default(configuration)

        self.api_instance = client.CustomObjectsApi(client.ApiClient(configuration))
        self.v1 = client.CoreV1Api()

        self.namespace = os.environ["NAMESPACE"]
        self.task_id = os.environ["TASK_ID"]
        self.axon_name = os.environ["AXON_NAME"]
        self.metrics = self.get_metrics(self.axon_name, self.namespace)
        self.url = "http://prometheus-pushgateway.{}:{}/metrics/job/{}/pod/".format(self.namespace, self.port,
                                                                                    self.task_id)

    def get_metrics(self, name, namespace):
        ret = self.api_instance.get_namespaced_custom_object(group=MetricClientKubernetes.group,
                                                             version=MetricClientKubernetes.version,
                                                             plural=MetricClientKubernetes.plural,
                                                             namespace=namespace,
                                                             name=name)

        m = {k.split(self.metric_prefix)[1]: v for k, v in ret["metadata"]["labels"].items()
             if k.startswith(self.metric_prefix)}

        return m

    def post_update(self, metric, value):
        internal_metric_name = self.metrics[metric]
        payload = "{} {}".format(internal_metric_name, value)
        res = requests.post(self.url, payload, headers={'Content-Type': 'application/octet-stream'})
        return res


class MetricClient(object):

    def __init__(self, port=9091):
        self.port = port
        self.namespace = os.environ["NAMESPACE"]
        self.myelin_installation_namespace = os.environ["MYELIN_NAMESPACE"]
        self.task_id = os.environ["TASK_ID"]
        self.axon_name = os.environ["AXON_NAME"]
        self.pushgateway_url = os.environ["PUSHGATEWAY_URL"]
        self.url = "http://{}.{}.svc.cluster.local:{}/metrics/job/{}/pod/".format(self.pushgateway_url,
                                                                                  self.myelin_installation_namespace,
                                                                                  self.port,
                                                                                  self.task_id)

    def get_metric(self, name):
        metric = "{}_{}".format(name, self.axon_name)
        return metric.replace("-", "__")

    def post_update(self, metric, value):
        internal_metric = self.get_metric(metric)
        payload = "{} {}\n".format(internal_metric, value)
        res = requests.post(url=self.url, data=payload,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})
        print(res.text)
        return res

    def post_result(self, config_id, config, budget, loss, info_map):
        train_controller_url = os.environ['TRAIN_CONTROLLER_URL']
        logging.info("train_controller_url: %s" % train_controller_url)

        result_dict = ({
            'loss': loss,
            'info': info_map
        })
        result = {'result': result_dict, 'exception': None}
        res_post = {'result': result, 'budget': budget, 'config_id': self.build_config_id(config_id), 'config': config}
        response = requests.post("%s/submit_result" % train_controller_url, json=res_post)
        print('response: %s' % response.status_code)
        if response.status_code != 200:
            raise Exception("reporting HP failed, error: %s" % response.text)

    @staticmethod
    def build_config_id(config_id):
        return [int(x) for x in config_id.split("_")]
