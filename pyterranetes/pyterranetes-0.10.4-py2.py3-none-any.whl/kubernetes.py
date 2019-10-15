"""Very similar to how things are done with terraform configs, we create
a context and add kubernetes objects to it:

.. code-block:: python

    from p10s import k8s, value

    c = k8s.Context()

    deployment = k8s.Deployment(yaml(\"""
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: nginx-deployment
          labels:
            app: nginx
        spec:
    \"""))

    deployment.body['metadata']['labels']['env'] = value('ENV')

    c += deployment

    c += k8s.Service(yaml(\"""
        kind: Service
        apiVersion: v1
        metadata:
          name: my-service
        spec:
            ...
    \"""))

    ...


While you can always pass in a dict object to the various
KubernetesObject class constructors it's usually easier, and closer to
what you already know, to use the ``yaml`` helper to parse a bock of
yaml code and start working with that. you can use the
:py:meth:`apiVersion <p10s.kubernetes.KubernetesObject.apiVersion>`,
:py:meth:`metadata <p10s.kubernetes.KubernetesObject.metadata>`, and
:py:meth:`spec <p10s.kubernetes.KubernetesObject.spec>` properties no
matter how the object was created.

The various KubernetesObject clsses exist only for readability and
convenience, creating a base KubernetesObject and passing in ``kind``
is the fully equivalent. This is also the way to create ojects for
kinds that are not pre-defined.

p10s takes advantage of the fact that you can have multiple kubernetes
objects in the same yaml file (represented as multiple kubernetes
documents). Multiple ``KubernetesObject`` objects can be added to the
same ``k8s.Context``, in the same p10s script, and kubernetes and helm
will be able to properly parse it.

"""

from copy import deepcopy

from p10s.base import BaseContext
from p10s.config_context import AutoData
from p10s.loads import ruamel, yaml, yaml_all
from p10s.utils import merge_dicts


class Context(BaseContext):
    """Context class for generating kubernetes and helm files.

Really is just a YAML context.
"""

    output_file_extension = ".yaml"

    def __init__(self, *args, data=None, **kwargs):
        if data is None:
            self.data = []
        else:
            self.data = data

        super().__init__(*args, **kwargs)

    def add(self, object):
        if not isinstance(object, (list, tuple)):
            objects = [object]
        else:
            objects = object
        for o in objects:
            if isinstance(o, (AutoData, Data, dict)):
                self.data.append(o)
            else:
                raise Exception(
                    "Can't add %s to %s, is not of type KubernetesObject", o, self
                )
        return self

    def __iadd__(self, object):
        return self.add(object)

    def __add__(self, block):
        new = Context(input=self.input, output=self.output, data=deepcopy(self.data))
        return new.add(block)

    def _render_data(self):
        documents = []
        for doc in self.data:
            if isinstance(doc, Data):
                documents.append(doc.render())
            elif isinstance(doc, AutoData):
                documents.append(doc.data())
            elif isinstance(doc, dict):
                documents.append(doc)
            else:
                raise Exception(
                    "%s is of type %s, which we don't know how to render."
                    % (doc, type(doc))
                )
        return documents

    def render(self):
        with self._output_stream() as out:
            ruamel.dump_all(self._render_data(), out)


class Data:
    def __init__(self, data=None):
        if data is None:
            self.data = {}
        else:
            self.data = data

    def render(self):
        def _rec(object):
            if isinstance(object, (list, tuple)):
                return [_rec(o) for o in object]
            elif isinstance(object, dict):
                return {_rec(k): _rec(v) for k, v in object.items()}
            elif isinstance(object, Data):
                return object.render()
            else:
                return object

        return _rec(self.data)

    @property
    def body(self):
        return self.data

    def update(self, new_body_values):
        """Merges in ``new_body_values`` with this block's body."""
        self.data = merge_dicts(self.data, new_body_values)
        return self


class KubernetesObject(Data):
    KIND = None

    def __init__(self, data=None, kind=None):
        super().__init__(data=data)

        if kind is not None:
            self.kind = kind
        elif self.KIND is not None:
            self.kind = self.KIND

    @property
    def kind(self):
        """Property mapping this object's ``kind`` value"""
        return self.data.get("kind", None)

    @kind.setter
    def kind(self, value):
        self.data["kind"] = value

    @property
    def apiVersion(self):
        """Property mapping this object's ``apiVersion`` value"""
        return self.data.get("apiVersion", None)

    @apiVersion.setter
    def apiVersion(self, value):
        self.data["apiVersion"] = value

    @property
    def metadata(self):
        """Property mapping this object's ``metadata`` value"""
        return self.data.get("metadata", None)

    @metadata.setter
    def metadata(self, value):
        self.data["metadata"] = value

    @property
    def spec(self):
        """Property mapping this object's ``spec`` value"""
        return self.data.get("spec", None)

    @spec.setter
    def spec(self, value):
        self.data["spec"] = value


class Deployment(KubernetesObject):
    KIND = "Deployment"


class ConfigMap(KubernetesObject):
    KIND = "ConfigMap"


class Service(KubernetesObject):
    KIND = "Service"


class Job(KubernetesObject):
    KIND = "Job"


class StatefulSet(KubernetesObject):
    KIND = "StatefulSet"


class Ingress(KubernetesObject):
    KIND = "Ingress"


class Secret(KubernetesObject):
    KIND = "Ingress"


def _data_to_object(data):
    kind = data.get("kind", None)
    if kind is not None:
        cls = None
        if kind == "Deployment":
            cls = Deployment
        if kind == "ConfigMap":
            cls = ConfigMap
        if kind == "Service":
            cls = Service
        return cls(data=data)
    else:
        raise Exception("Missing kind property on %s", data)


def from_yaml(yaml_input):
    """Parse the given yaml_input and return the corresponding ``KubernetesObject``"""
    return _data_to_object(yaml(yaml_input))


def many_from_yaml(yaml_input):
    """Parse the documents from ``yaml_input`` and returns a list of ``KubernetesObject``.
"""
    return [_data_to_object(data) for data in yaml_all(yaml_input)]
