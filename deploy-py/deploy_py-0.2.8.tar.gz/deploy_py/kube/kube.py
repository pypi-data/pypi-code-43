import pykube

from . import exceptions
from ..logging import get_logger


class Client:
    def __init__(self, context, verbosity=1):
        self.logger = get_logger("deploy_py.kube.Client", verbosity)
        conf = pykube.KubeConfig.from_file()
        try:
            conf.set_current_context(context)
        except KeyError:
            raise exceptions.ContextNotFoundError(context, conf.filename)
        self.api = pykube.HTTPClient(conf)
        self.pods = pykube.Pod.objects(self.api)

    def get_pod_by_labels(self, namespace: str, labels: dict) -> pykube.objects.Pod:
        pods = [p for p in self.pods.filter(namespace=namespace, selector=labels).all()]
        if not len(pods):
            raise exceptions.PodNotFoundError(selectors=labels)
        return pods[0]

    def get_pod_name_and_port(self, namespace: str, labels: dict, port_name: str) -> (str, int):
        pod = self.get_pod_by_labels(namespace, labels)
        ports = pod.obj["spec"]["containers"][0]["ports"]
        for port in ports:
            if port["name"] == port_name:
                return pod.name, port["containerPort"]
        raise exceptions.PortNotFoundError(port_name, ports)
