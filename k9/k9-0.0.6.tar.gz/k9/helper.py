from kubernetes import client, config
from k9.pretty_object import PrettyObject
import yaml

po = PrettyObject()
config.load_kube_config()

v1 = client.CoreV1Api()
appsv1 = client.AppsV1Api()
rbac = client.RbacAuthorizationV1Api()
api = client.ApiextensionsV1beta1Api()

default_namespace = None


###########################################################################
# Utility Functions
###########################################################################

def last_word(value: str):
    """ Splits out the word after the last slash in a string.  K8
        objects are expressed in a path style name                 """
    return value.split('/')[-1:][0]


def view_yaml(fn: str):
    """ Dumps out yaml file in simplified JSON format for easy viewing. This
        is useful when constructing the body of a request that matches aknown yaml format."""
    file = None
    try:
        file = open(fn)
        po.print(yaml.safe_load(file))

    finally:
        if file is not None:
            file.close()


###########################################################################
# Namespaces
###########################################################################

def set_default_namespace(namespace: str = None):
    """sets the default namespace for all functions that need namespace."""

    global default_namespace
    default_namespace = namespace
    print(f"default_namespace={default_namespace}")


def get_default_namespace():
    global default_namespace
    return default_namespace


def list_namespaces():
    """Returns a list of dictionaries with name and status."""

    return [
        {'name': last_word(namespace.metadata.self_link), 'status': namespace.status.phase}
        for namespace in v1.list_namespace().items
    ]


def namespace_exists(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    found = [
        ns['name']
        for ns in list_namespaces()
        if ns['status'] == 'Active' and ns['name'] == namespace
    ]

    return len(found) > 0


def create_namespace(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    body = \
        {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": namespace,
            }
        }

    return v1.create_namespace(body)


def delete_namespace(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    return v1.delete_namespace(namespace)


###########################################################################
# Pods
###########################################################################

def list_pods(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    pod_list = v1.list_namespaced_pod(namespace)
    return [
        {'name': pod.metadata.name, 'status': pod.status.phase, 'ip': pod.status.pod_ip, 'labels': pod.metadata.labels, 'reason': pod.status.reason, 'start_time': pod.status.start_time}
        for pod in pod_list.items
    ]


###########################################################################
# Deployments
###########################################################################

def list_deployments(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    return [
        last_word(deployment.metadata.self_link)
        for deployment in appsv1.list_namespaced_deployment(namespace).items
    ]


def get_deployment(name: str, namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    return appsv1.read_namespaced_deployment(name, namespace)


###########################################################################
# Service Accounts
###########################################################################

def create_service_account(name: str, namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    body =\
        { 'apiVersion': 'v1',
          'kind': 'ServiceAccount',
          'metadata' : { 'name': name }
        }

    return v1.create_namespaced_service_account(namespace, body)


def delete_service_account(name: str, namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    return v1.delete_namespaced_service_account(name, namespace)


def list_service_account(name: str, namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    return v1.read_namespaced_service_account(name, namespace)


###########################################################################
# Cluster Roles
###########################################################################

def list_cluster_roles():
    return [
        {'name': last_word(role.metadata.self_link).replace('%3A', ':'), 'created': role.metadata.creation_timestamp}
        for role in rbac.list_cluster_role().items
    ]


def create_cluster_role(body: dict):
    return rbac.create_cluster_role(body)


def delete_cluster_role(name: str):
    return rbac.delete_cluster_role(name)


def get_cluster_role(name: str):
    try:
        return rbac.read_cluster_role(name)
    except Exception as e:
        return None


def create_cluster_role_binding(binding: str, role: str, sa: str, namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    body =\
        {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'ClusterRoleBinding',
            'metadata': {'name': binding},
            'roleRef': {
                'apiGroup': '',
                'kind': 'ClusterRole',
                'name': role
            },
            'subjects': {
                'kind': 'ServiceAccount',
                'name': sa,
                'namespace': namespace
            }
        }

    return rbac.create_cluster_role_binding(body)


def delete_cluster_role_binding(binding: str):
    pass


def get_cluster_role_binding(binding: str):
    pass

###########################################################################
# Custom Functions
###########################################################################

def create_ecr_login_role(name: str):
    # Create service account AWS login role
    body = \
    { 'apiVersion': 'rbac.authorization.k8s.io/v1',
      'kind': 'ClusterRole',
      'metadata': { 'name': name },
      'rules': [
        { 'apiGroups': [''],
          'resources': ['serviceaccounts'],
          'verbs': ['get', 'patch'] },

        { 'apiGroups': [''],
          'resources': ['secrets'],
          'verbs': ['create', 'delete']}
               ]
    }

    return create_cluster_role(body)

cluster_role = 'test-ecr-role'
#pprint(create_ecr_login_role(cluster_role))
#pprint(get_cluster_role(cluster_role))
#pprint(delete_cluster_role(cluster_role))



