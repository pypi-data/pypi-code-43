from kubernetes import client, config
from k9.pretty_object import PrettyObject
import os
import yaml
import pprint
from datetime import datetime, timezone

po = PrettyObject()
config.load_kube_config()

v1_core = client.CoreV1Api()
v1_apps = client.AppsV1Api()
v1_rbac = client.RbacAuthorizationV1Api()
v1_apix = client.ApiextensionsV1beta1Api()
v1_exts = client.ExtensionsV1beta1Api()
v1_batch = client.BatchV1beta1Api()

default_namespace = None

###########################################################################
# Utility Functions
###########################################################################

def last_word(value: str):
    """
    Splits out the word after the last slash in a string.  K8
    objects are expressed in a path style name

    Example
    -------

    >>> last_word('pods/my-pod')
    'my-pod'
    """
    return value.split('/')[-1:][0]


def view_yaml(fn: str):
    """
    Dumps out yaml file in JSON format for easy viewing. This
    is useful when constructing the body of a request that matches a known yaml format.

    Example
    -------

    >>> view_yaml('tomcat-deploy-dev.yml')
    """
    file = None
    try:
        file = open(fn)
        pprint.pprint(yaml.safe_load(file))

    finally:
        if file is not None:
            file.close()


def read_yaml(fn: str):
    """
    Reads a YAML file and returns the resulting the object.

    Example
    -------

    >>> read_yaml('tomcat-deploy-dev.yml')

    """
    file = None
    try:
        file = open(fn)
        return yaml.safe_load(file)

    finally:
        if file is not None:
            file.close()


def get_age(creation_time: datetime):
    """
    Given a creation timestamp, return the difference in time from now.

    :param creation_time: The time we want to measure age from
    :return: timedelta - the amount of time since creation_time
    """
    now = datetime.now(timezone.utc)
    delta = now - creation_time

    if delta.days > 0:
        return f'{delta.days}d'

    hours = delta.seconds/3600

    seconds = delta.seconds%3600

    minutes = seconds/60
    seconds = seconds % 60

    return '%02d:%02d:%02d' % (hours, minutes, seconds)


def abs_path(file: str):
    """
    Sets an absolute path relative to the **k9** package directory.

    Example::
        result = abs_path('myfile)

    Result::
        /Users/simon/git/k9/k9/myfile


    This is used primarily for building unit tests within the K9 package
    and is not expected to be useful to K9 library users.

    :param file: File or directory to attach absolute path with
    :return: absolute path to specified file or directory
    """
    basedir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(basedir, file)

###########################################################################
# Namespaces
###########################################################################

def set_default_namespace(namespace: str = None):
    """
    Sets the default namespace for all functions that need namespace.

    Most of the functions in this library will require a namespace parameter.
    If the namespace is not provided, the default namespace you set will
    be used instead, simplifying the call.

    Typically, this should be one of the first calls you make when
    working with this library.
    """
    global default_namespace
    default_namespace = namespace


def get_default_namespace():
    """
    Gets the default namespace set using set_default_namespace().
    """
    global default_namespace
    if default_namespace is None:
        raise Exception("You must call get_default_namespace() first before using most of the K9 API functions.")

    return default_namespace


def list_namespaces():
    """
    Retrieves a list of namespaces and associated status.  Returns same
    information as `kubectl get namespaces`

    :return: list of dictionaries with **name** and **status**
    """

    return [
        {
            'name': namespace.metadata.name,
            'status': namespace.status.phase,
            'age': get_age(namespace.metadata.creation_timestamp)
        }
        for namespace in v1_core.list_namespace().items
    ]

def get_namespace(namespace: str = None):
    """

    :param namespace: Namespace to retrieve.  If None, will use default namespace.
    :return: `V1Namespace <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Namespace.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_core.read_namespace(namespace)


def namespace_exists(namespace: str = None):
    """
    Determines if the specified namespace exists.

    :param namespace: The namespace to check for.  If None, then the default namespace is used.
    :return: bool - True if namespace exists
    """
    try:
        if namespace is None:
            namespace = get_default_namespace()

        result = get_namespace(namespace)
        return result.status.phase == 'Active' and result.metadata.name == namespace

    except:
        return False

def create_namespace(namespace: str = None):
    """
    Creates the specified namespace.

    :param namespace: Specifies the namespace to create.  If None, then the default namespace is used.
    :return: `V1Namespace <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Namespace.md>`_
    """

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

    result = v1_core.create_namespace(body)

    # Wait Loop
    # i = 0
    # while result.status.phase != 'Active':
    #     time.sleep(1)
    #     i += 1
    #     if i < 30:
    #         break
    #     result = get_namespace(namespace)

    return result


def delete_namespace(namespace: str = None):
    """
    Deletes the specified namespace.

    :param namespace: Namespace to delete.  If None, the default namespace is used.
    :return: None if namespace doesn't exist, otherwise `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if namespace_exists(namespace):
        result = v1_core.delete_namespace(namespace)
    else:
        return None


###########################################################################
# Pods
###########################################################################

def list_pods(namespace: str = None):
    """
    List all pods in a given namespace

    :param namespace: Namespace to search.  If None, uses the default namespace
    :return: Returns a list of pods - each pod represented by a dictionary with **name**, **status**, **ip**, **labels**, **reason**, and **start_time**
    """
    if namespace is None:
        namespace = get_default_namespace()

    pod_list = v1_core.list_namespaced_pod(namespace)
    return [
        {
            'name': pod.metadata.name,
            'status': pod.status.phase,
            'ip': pod.status.pod_ip,
            'labels': pod.metadata.labels,
            'reason': pod.status.reason,
            'age': get_age(pod.status.start_time)
        }
        for pod in pod_list.items
    ]


###########################################################################
# Secrets
###########################################################################

def list_secrets(namespace: str = None):
    """
    Lists secrets in a given namespace.

    :param namespace: Namespace you want to search.  If None, the default namespace is used.
    :return: A list of dictionaries with **name**, **type**, **data** (for number of entries), and **age**
    """
    if namespace is None:
        namespace = get_default_namespace()

    return [
        {
            'name': secret.metadata.name,
            'type': secret.type,
            'data': len(secret.data),
            'age': get_age(secret.metadata.creation_timestamp)
        }
        for secret in v1_core.list_namespaced_secret(namespace).items
    ]


def secret_exists(name: str, namespace: str = None):
    """
    As this is intended to be used to retrieve a secret and also determine if a secret exists.

    :param name: Name of secret
    :param namespace: Namespace to search, if None, uses default namespace
    :return: True if specfied secret exists.
    """
    if namespace is None:
        namespace = get_default_namespace()

    try:
        result = get_secret(name, namespace)
        return result.metadata.name == name

    except:
        return False


def get_secret(name: str, namespace: str = None):
    """
    As this is intended to be used to retrieve a secret and also determine if a secret exists.

    :param name: Name of secret
    :param namespace: Namespace to search, if None, uses default namespace
    :return: None if not found, otherwise `V1Secret <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Secret.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_core.read_namespaced_secret(name, namespace)


def create_secret(name: str, secrets: dict, namespace: str = None):
    """
    Creates a secret.

    :param name: Name of secret
    :param secrets: Dictionary containing name value pairs of secrets
    :param namespace:
    :return: `V1Secret <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Secret.md>`_

    Example::

        # Note that you should not embed secrets in your source code, this is
        # simply to illustrate how the function call works.
        secret_name = "tomcat-dev"
        secrets = {
            'ds-url': 'https://some/url',
            'password': 'My1SecretPassword',
            'username': 'postgres'
        }

        # Test create_secret()
        result = create_secret(secret_name, secrets)

    Output::

        {'api_version': 'v1',
         'data': {'ds-url': 'aHR0cHM6Ly9zb21lL3VybA==',
                  'password': 'TXkxU2VjcmV0UGFzc3dvcmQ=',
                  'username': 'cG9zdGdyZXM='},
         'kind': 'Secret',
         'metadata': {'annotations': None,
                      'cluster_name': None,
                      'creation_timestamp': datetime.datetime(2019, 10, 17, 17, 20, 56, tzinfo=tzutc()),
                      'deletion_grace_period_seconds': None,
                      'deletion_timestamp': None,
                      'finalizers': None,
                      'generate_name': None,
                      'generation': None,
                      'initializers': None,
                      'labels': None,
                      'managed_fields': None,
                      'name': 'tomcat-dev',
                      'namespace': 'default',
                      'owner_references': None,
                      'resource_version': '2053051',
                      'self_link': '/api/v1/namespaces/default/secrets/tomcat-dev',
                      'uid': '7ab378c0-f102-11e9-a715-025000000001'},
         'string_data': None,
         'type': 'Opaque'}
    """
    if namespace is None:
        namespace = get_default_namespace()

    body = client.V1Secret()
    body.api_version = 'v1'
    body.kind = 'Secret'
    body.metadata = {'name': name}
    body.string_data = secrets
    body.type = 'Opaque'

    return v1_core.create_namespaced_secret(namespace, body)


def delete_secret(name: str, namespace: str = None):
    """
    Delete specified secret.

    :param name: Name of secret to delete.
    :param namespace: Namespace to delete from.  If None, default namespace is used.
    :return: `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_ if secret exists, if not, None.
    """
    if namespace is None:
        namespace = get_default_namespace()

    if secret_exists(name, namespace):
        return v1_core.delete_namespaced_secret(name, namespace)
    else:
        return None


###########################################################################
# Deployments
###########################################################################

def list_deployments(namespace: str = None):
    """
    Lists deployments in a given namespace.

    :param namespace: Namespace you want to search.  If None, the default namespace is used.
    :return: A list of deployment names.
    """
    if namespace is None:
        namespace = get_default_namespace()

    return [
        {
            'name': deployment.metadata.name,
            'ready': f'{deployment.status.ready_replicas}/{deployment.status.replicas}',
            'available': deployment.status.available_replicas,
            'up-to-date': deployment.status.updated_replicas,
            'age': get_age(deployment.metadata.creation_timestamp)
        }
        for deployment in v1_apps.list_namespaced_deployment(namespace).items
    ]


def deployment_exists(name: str, namespace: str = None):
    """Returns True if the specified deployment exists."""
    try:
        if namespace is None:
            namespace = get_default_namespace()

        result = get_deployment(name, namespace)
        return result.metadata.name == name

    except:
        return False

def get_deployment(name: str, namespace: str = None):
    """
    Get a specific deployment by name.

    :param name: Name of deployment to retrieve.
    :param namespace:  Namespace to search.  If None, the default namespace is used.

    :return: `V1Deployment <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Deployment.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_apps.read_namespaced_deployment(name, namespace)


def create_deployment(body: dict, namespace: str = None):
    """
    Create a deployment from a definition file:

    :param body: Deployment Description - https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/AppsV1beta1Deployment.md
    :param namespace: Namespace to create Deployment in.  If None, the default namespace is used.
    :return: `V1Deployment <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Deployment.md>`_

    You'll most likely create a deployment configuration file and import that in as follows:

    Sample YAML file::

        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: tomcat-dev
        spec:
          replicas: 1
          selector:
            matchLabels:
              app: tomcat
              env: dev
          strategy:
            type: RollingUpdate
            rollingUpdate:
              maxSurge: 1
              maxUnavailable: 1
          minReadySeconds: 5
          template:
            metadata:
              labels:
                app: tomcat
                env: dev
            spec:
              containers:
              - name: tomcat
                image: tomcat:7
                ports:
                  - containerPort: 8080
                env:
                  - name: DS_URL
                    valueFrom:
                      secretKeyRef:
                        name: tomcat-dev
                        key: ds-url
                  - name: DS_USR
                    valueFrom:
                      secretKeyRef:
                        name: tomcat-dev
                        key: username
                  - name: DS_PWD
                    valueFrom:
                      secretKeyRef:
                        name: tomcat-dev
                        key: password

    Example::

        import k9.helper as k9

        body = k9.read_yaml('tomcat-deploy-dev.yml')
        k9.create_deployment(body)


    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_apps.create_namespaced_deployment(namespace, body)

def delete_deployment(name: str, namespace: str = None):
    """
    Delete the specified deployment.

    :param name: Name of deployment to remove.
    :param namespace: Namespace to remove deployment from.   If None, the default namespace is used.
    :return: None if deployment did not exist, otherwise `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if deployment_exists(name, namespace):
        return v1_apps.delete_namespaced_deployment(name, namespace)
    else:
        return None


def update_deployment_image(name: str, container: str, image: str, namespace: str = None):
    """
    Updates the specified deployment name with a new image tag for the container.  The container name must
    match the container name specified in the original deployment.

    This will perform a rolling update if  max_unavailable replicas is less than the total number of replicas
    for the cluster.

    :param name: Name of the deployment to update
    :param container: Name of the container within the deployment to update.
    :param image: The image and tag of the image to update the container to.
    :param namespace: The namespace to find the deployment in.  If None, the default namespace is used.
    :return: `V1Deployment <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Deployment.md>`_

    The following example results in a rolling update to to Tomcat 8::

            update_deployment_image(deploy_name, 'tomcat', 'tomcat:8')

    Note that the container name matches the specification of the deployment YAML shown above
    and changes the version of Tomcat from version 7 to version 8.
    """
    if namespace is None:
        namespace = get_default_namespace()

    body = {
        'apiVersion': "apps/v1",
        'kind': "Deployment",
        'metadata': {
            'name': name
        },
        'spec': {
            'template': {
                'spec': {
                    'containers': [
                        {
                            'name': container,
                            'image': image
                        }
                    ]
                }
            }
        }
    }

    return v1_apps.patch_namespaced_deployment(name, namespace, body)

def scale_deployment(name: str, spec: str, namespace:str = None):
    """
    Updates the scaling specification for this deployment.

    :param name: Name of deployment to update.
    :param spec: The updated specification of the scaling parameters.
    :param namespace: The namespace to update the deployment in.  If namespace is None, the default namespace is used.
    :return: `V1Scale <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Scale.md>`_

    Other useful references: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#scaling-a-deployment

    Example to scale up the deployment to 3 replicas::

            spec = {
                'replicas': 3
            }
            scale_deployment(deploy_name, spec)

    """

    if namespace is None:
        namespace = get_default_namespace()
    body = {
        'apiVersion': "apps/v1",
        'kind': "Deployment",
        'metadata': {
            'name': "tomcat-dev"
        },
        'spec': spec
    }

    return v1_apps.patch_namespaced_deployment_scale(name, namespace, body)

###########################################################################
# Services
###########################################################################

def list_services(namespace: str = None):
    """
    Lists the services in the namespace.

    :param namespace: Namespace to list services from.  If None, default namespace will be used.
    :return: List of dictionaries with **name**, **type**, **cluster-ip**, **external-ips**, **ports**, and **age**
    """
    if namespace is None:
        namespace = get_default_namespace()

    return [
        {
            'name': svc.metadata.name,
            'type': svc.spec.type,
            'cluster-ip': svc.spec.cluster_ip,
            'external-ips': svc.spec.external_i_ps,
            'ports': [
                f'{port.target_port}/{port.protocol}'
                for port in svc.spec.ports
            ],
            'age': get_age(svc.metadata.creation_timestamp)
        }
        for svc in v1_core.list_namespaced_service(namespace).items
    ]


def service_exists(name: str, namespace: str = None):
    """
    Checks existence of specified service.

    :param name: Name of service.
    :param namespace: Namespace to get service from.  If None, will use default namespace.
    :return: True if service exists.
    """
    if namespace is None:
        namespace = get_default_namespace()
    try:
        result = get_service(name, namespace)

        return result.metadata.name == name
    except:

        return False;

def get_service(name: str, namespace: str = None):
    """
    Retrieves details on the specified service.

    :param name: Name of service to get.
    :param namespace: Namespace to get service from.  If None, will use default namespace.
    :return: `V1Service <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Service.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_core.read_namespaced_service(name, namespace)

def create_service(body: dict, namespace: str = None):
    """
    Creates a service based on definition provided by **body**.

    :param body:  Service description: https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Service.md
    :param namespace: Namespace to create service in.  If None, will use default namespace.
    :return: `V1Service <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Service.md>`_

    You'll most likely create a YAML file to describe your service and read that in.  You can use
    read_yaml() to generate the body as follows:

    Example::

        result = create_service(read_yaml('my-service.yaml'))

    Sample YAML file::

        apiVersion: v1
        kind: Service
        metadata:
          name: tomcat-svc-dev
          labels:
                svc: tomcat
                env: dev
        spec:
          type: ClusterIP
          ports:
          - port: 8080
            targetPort: 8080
            protocol: TCP
          selector:
                app: tomcat
                env: dev
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_core.create_namespaced_service(namespace=namespace, body=body)


def delete_service(name: str, namespace: str = None):
    """
    Deletes the specified service.  This function will check whether the service exists before attempting the delete.

    :param name: Name of service to delete
    :param namespace: Namespace to delete from.  If None, default namespace is used.
    :return: None if service doesn't exist, otherwise `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if service_exists(name, namespace):
        return v1_core.delete_namespaced_service(name, namespace)
    else:
        return None


###########################################################################
# Ingress
###########################################################################

def list_ingress(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    return [
        {
            'name': ing.metadata.name,
            'namespace': ing.metadata.namespace,
            'hosts': [
                tls.hosts
                for tls in ing.spec.tls
            ],
            'address': [
                rule.host
                for rule in ing.spec.rules
            ],
            'age': get_age(ing.metadata.creation_timestamp)
        }
        for ing in v1_exts.list_namespaced_ingress(namespace).items
    ]


def ingress_exists(name: str, namespace: str = None):
    """
    Checks existence of specified ingress.

    :param name: Name of ingress to check.
    :param namespace: Namespace to check, if None, check in default namespace.
    :return: True if specified ingress exists.
    """
    try:
        if namespace is None:
            namespace = get_default_namespace()

        result = get_ingress(name, namespace)
        return result.metadata.name == name

    except:
        return False


def get_ingress(name: str, namespace: str = None):
    """
    Get details of specified ingress.

    :param name: Name of ingress to get.
    :param namespace: Namespace to get ingress from.  If None, get from default namespace.
    :return: `ExtensionsV1beta1Ingress <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Ingress.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_exts.read_namespaced_ingress(name, namespace)


def create_ingress(body: dict, namespace: str = None):
    """
    Creates an ingress point - which defines

    :param body: Contains Ingress Definition - https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Ingress.md
    :param namespace: Namespace to create ingress in.  If None, use default namespace
    :return: `ExtensionsV1beta1Ingress <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/ExtensionsV1beta1Ingress.md>`_

    Example YAML File::

        apiVersion: extensions/v1beta1
        kind: Ingress
        metadata:
          name: tomcat-ing-dev
        spec:
          rules:
            - host: tomcat.dev.sandbox.simoncomputing.com
              http:
                paths:
                  - path: /
                    backend:
                      serviceName: tomcat-svc-dev
                      servicePort: 8080
          tls:
          - hosts:
            - dev.sandbox.simoncomputing.com

    Example Call:

        from k9.helper import read_yaml, create_ingress

        body = read_yaml('../test/tomcat-ing-dev.yml')
        create_ingress(body)

    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_exts.create_namespaced_ingress(namespace, body)


def delete_ingress(name: str, namespace: str = None):
    """
    Deletes specified ingress.

    :param name: Name of ingress
    :param namespace: Namespace to delete from.  If None, remove from default namespace.
    :return: None if ingress doesn't exist, `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if ingress_exists(name, namespace):
        return v1_exts.delete_namespaced_ingress(name, namespace)
    else:
        return None


###########################################################################
# Service Accounts
###########################################################################

def list_service_accounts(namespace: str = None):
    if namespace is None:
        namespace = get_default_namespace()

    result = v1_core.list_namespaced_service_account(namespace)

    return [
        {
            'name': sa.metadata.name,
            'age': get_age(sa.metadata.creation_timestamp)
        }
        for sa in result.items
    ]


def create_service_account(name: str, namespace: str = None):
    """
    Create a service account.

    :param name: Name of service account.
    :param namespace: namespace to create service account in.  If None, create service account in default namespace
    :return: `V1ServiceAccount <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ServiceAccount.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    body =\
        { 'apiVersion': 'v1',
          'kind': 'ServiceAccount',
          'metadata' : { 'name': name }
        }

    result = v1_core.create_namespaced_service_account(namespace, body)

    # Wait for creation
    # i = 0
    # while not service_account_exists(name):
    #     time.sleep(2)
    #     i += 1
    #     if i > 30:
    #         break

    return result

def get_service_account(name: str, namespace: str = None):
    """
    Get details of specified service account

    :param name: Name of service account to retrieve.
    :param namespace: Namespace to retrieve service account from. If None, retrieve from default namespace.
    :return: `V1ServiceAccount <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ServiceAccount.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()
    pass

    return v1_core.read_namespaced_service_account(name, namespace)


def service_account_exists(name: str, namespace: str = None):
    """
    Checks for existence of service account

    :param name: Name of service account to look for.
    :param namespace: Namespace to look in.  If None, look in default namespace.
    :return: True if specified account exists.
    """
    if namespace is None:
        namespace = get_default_namespace()

    try:
        result = get_service_account(name, namespace)
        return result.metadata.name == name

    except:
        return False


def delete_service_account(name: str, namespace: str = None):
    """
    Delete specified service account.

    :param name: Name of service account to delete.
    :param namespace: Namespace to delete from.  If None, delete from default namespace.
    :return: None if service account doesn't exists, otherwise returns `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if service_account_exists(name, namespace):
        return v1_core.delete_namespaced_service_account(name, namespace)
    else:
        return None


###########################################################################
# Cron Jobs
###########################################################################

def list_cron_jobs(namespace: str = None):
    """
    List all cluster cron jobs
    :param namespace: Then namespace to list cron jobs from.  If None, uses the default namespace.
    :return: A list of dictionary items with **name** and **created**.
    """
    if namespace is None:
        namespace = get_default_namespace()

    return [
        {
            'name': cj.metadata.name,
            'created': cj.metadata.creation_timestamp
        }
        for cj in v1_batch.list_namespaced_cron_job(namespace).items
    ]


def create_cron_job(body: dict, namespace: str = None):
    """
    Create a cron job

    :param body: The cron job definition object.
    :param namespace: Then namespace to create cronjob in.  If None, uses the default namespace.
    :return: `V1beta1CronJob <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1beta1CronJob.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_batch.create_namespaced_cron_job(namespace, body)


def delete_cron_job(name: str, namespace: str = None):
    """
    Deletes the specified cron job

    :param name: Name of cron job
    :param namespace: Then namespace to delete cron job from.  If None, uses the default namespace.
    :return: None if cron job doesn't exist, `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if cron_job_exists(name, namespace):
        return v1_batch.delete_namespaced_cron_job(name, namespace)
    else:
        return None


def get_cron_job(name: str, namespace: str = None):
    """
    Gets the specified cron job

    :param name: Name of cron job
    :param namespace: Then namespace to get cron job from.  If None, uses the default namespace.
    :return: `V1beta1CronJob <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1beta1CronJob.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_batch.read_namespaced_cron_job(name, namespace)


def cron_job_exists(name:str, namespace: str = None):
    """
    Checks for the cron job's existence.

    :param name: Name of cron job to look for.
    :param namespace: Then namespace to check for cron job.  If None, uses the default namespace.
    :return: True if specified cron job exists
    """
    try:
        if namespace is None:
            namespace = get_default_namespace()

        result = get_cron_job(name, namespace)
        return result.metadata.name == name

    except:
        return False

###########################################################################
# Roles
###########################################################################

def list_roles(namespace: str = None):
    """
    List all cluster roles
    :param namespace: Then namespace to list roles from.  If None, uses the default namespace.
    :return: A list of dictionary items with **name** and **created**.
    """
    if namespace is None:
        namespace = get_default_namespace()

    return [
        {
            'name': role.metadata.name,
            'created': role.metadata.creation_timestamp
        }
        for role in v1_rbac.list_namespaced_role(namespace).items
    ]


def create_role(body: dict, namespace: str = None):
    """
    Create a role from an object defining the role.

    :param body: The role definition object.
    :param namespace: Then namespace to create role in.  If None, uses the default namespace.
    :return: `V1Role <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Role.md>`_

    Example YAML file::

        apiVersion: rbac.authorization.k8s.io/v1
        kind: ClusterRole
        metadata:
          name: ecr-login-role
        rules:
        - apiGroups: [""]
          resources: ["secrets"]
          verbs: ["create", "delete"]
        - apiGroups: [""]
          resources: ["serviceaccounts"]
          verbs: ["get", "patch"]


    Example Call::

        from k9.helper import (
            set_default_namespace,
            create_role,
            read_yaml
        )

        set_default_namespace('my-namespace')

        body = read_yaml('ecr-login-role.yml')
        result = create_role(body)

    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_rbac.create_namespaced_role(namespace, body)


def delete_role(name: str, namespace: str = None):
    """
    Deletes the specified cluster

    :param name: Name of cluster
    :param namespace: Then namespace to delete role from.  If None, uses the default namespace.
    :return: None if role exists, otherwise return `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if role_exists(name, namespace):
        return v1_rbac.delete_namespaced_role(name, namespace)
    else:
        return None


def get_role(name: str, namespace: str = None):
    """
    Gets the specified cluster role.

    :param name: Name of cluster role to retrieve.
    :param namespace: Then namespace to get role from.  If None, uses the default namespace.
    :return: `V1Role <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Role.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_rbac.read_namespaced_role(name, namespace)


def role_exists(name:str, namespace: str = None):
    """
    Checks for the cluster role's existence.

    :param name: Name of cluster role to look for.
    :param namespace: Then namespace to check for role.  If None, uses the default namespace.
    :return: True if specified cluster role exists.
    """
    try:
        if namespace is None:
            namespace = get_default_namespace()

        result = get_role(name, namespace)
        return result.metadata.name == name

    except:
        return False


def create_role_binding(name: str, role: str, sa: str, namespace: str = None):
    """
    Bind the specified role to the specified service account.

    :param name: Name of binding we are creating here
    :param role: The cluster role name to bind with.
    :param sa: The service account to bind this role to.
    :param namespace: The namespace of role and service account.  If namespace is None, then the binding will be performed in the default namespace.
    :return: `V1RoleBinding <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1RoleBinding.md>`_

    Example::

        result = create_role_binding(binding_name, role_name, sa_name)

    """
    if namespace is None:
        namespace = get_default_namespace()

    body =\
        {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'RoleBinding',
            'metadata': {
                'name': name,
                'namespace': namespace
            },
            'roleRef': {
                'apiGroup': 'rbac.authorization.k8s.io',
                'kind': 'Role',
                'name': role
            },
            'subjects': [{
                'kind': 'ServiceAccount',
                'name': sa,
                'namespace': namespace
            }]
        }
    return v1_rbac.create_namespaced_role_binding(namespace, body)


def get_role_binding(name: str, namespace: str = None):
    """
    Get cluster role binding information

    :param name: Name of cluster role binding
    :param namespace: Then namespace to get role binding from.  If None, uses the default namespace.
    :return: `V1RoleBinding <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1RoleBinding.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    return v1_rbac.read_namespaced_role_binding(name, namespace)


def role_binding_exists(name:str, namespace: str = None):
    """
    Checks for the existence of the cluster role binding.

    :param name: name of cluster role binding.
    :param namespace: Then namespace to check for role binding.  If None, uses the default namespace.
    :return: True if binding exists.
    """
    try:
        if namespace is None:
            namespace = get_default_namespace()

        result = get_role_binding(name, namespace)
        return result.metadata.name == name

    except:
        return False


def delete_role_binding(name: str, namespace: str = None):
    """
    Delete cluster role binding

    :param name: cluster role binding name
    :param namespace: Then namespace to delete role binding from.  If None, uses the default namespace.
    :return: `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if namespace is None:
        namespace = get_default_namespace()

    if role_binding_exists(name, namespace):
        return v1_rbac.delete_namespaced_role_binding(name, namespace)
    else:
        return None


###########################################################################
# Cluster Roles
###########################################################################

def list_cluster_roles():
    """
    List all cluster roles
    :return: A list of dictionary items with **name** and **created**.
    """
    return [
        {
            'name': role.metadata.name,
            'created': role.metadata.creation_timestamp
        }
        for role in v1_rbac.list_cluster_role().items
    ]


def create_cluster_role(body: dict):
    """
    Create a cluster role from an object defining the role.

    Example::

            role = {
                'apiVersion': 'rbac.authorization.k8s.io/v1',
                'kind': 'ClusterRole',
                'metadata': {'name': f'{role_name}'},
                'rules': [
                     {
                         'apiGroups': [''],
                         'resources': ['secrets'],
                         'verbs': ['create', 'delete']
                     },
                     {
                         'apiGroups': [''],
                         'resources': ['serviceaccounts'],
                         'verbs': ['get', 'patch']
                     }

                 ]
            }

            result = create_cluster_role(role)

    Result::

        {'aggregation_rule': None,
         'api_version': 'rbac.authorization.k8s.io/v1',
         'kind': 'ClusterRole',
         'metadata': {'annotations': None,
                      'cluster_name': None,
                      'creation_timestamp': datetime.datetime(2019, 10, 16, 17, 33, 28, tzinfo=tzutc()),
                      'deletion_grace_period_seconds': None,
                      'deletion_timestamp': None,
                      'finalizers': None,
                      'generate_name': None,
                      'generation': None,
                      'initializers': None,
                      'labels': None,
                      'managed_fields': None,
                      'name': 'ecr-login-role',
                      'namespace': None,
                      'owner_references': None,
                      'resource_version': '1901293',
                      'self_link': '/apis/rbac.authorization.k8s.io/v1/clusterroles/ecr-login-role',
                      'uid': '10ccdf2b-f03b-11e9-9956-025000000001'},
         'rules': [{'api_groups': [''],
                    'non_resource_ur_ls': None,
                    'resource_names': None,
                    'resources': ['secrets'],
                    'verbs': ['create', 'delete']}]}"

    :param body: The role definition object.
    :return: `V1ClusterRole <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ClusterRole.md>`_
    """
    return v1_rbac.create_cluster_role(body)


def delete_cluster_role(name: str):
    """
    Deletes the specified cluster

    :param name: Name of cluster
    :return: None if cluster role doesn't exist, otherwise returns `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_
    """
    if cluster_role_exists(name):
        return v1_rbac.delete_cluster_role(name)
    else:
        return None


def get_cluster_role(name: str):
    """
    Gets the specified cluster role.

    :param name: Name of cluster role to retrieve.
    :return: `V1ClusterRole <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ClusterRole.md>`_
    """
    return v1_rbac.read_cluster_role(name)


def cluster_role_exists(name:str):
    """
    Checks for the cluster role's existence.

    :param name: Name of cluster role to look for.
    :return: True if specified cluster role exists.
    """
    try:
        result = get_cluster_role(name)
        return result.metadata.name == name

    except:
        return False


def create_cluster_role_binding(name: str, role: str, sa: str, namespace: str = None):
    """
    Bind the specified role to the specified service account.

    :param name: Name of binding we are creating here.
    :param role: The cluster role name to bind with.
    :param sa: The service account to bind this role to.
    :param namespace: The namespace of the **service account**.  If namespace is None, then the binding will be performed on service account in the default namespace.
    :return: `V1ClusterRoleBinding <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ClusterRoleBinding.md>`_

    Example::

        result = create_cluster_role_binding(cr_bind_name, cr_name, sa_name)

    """
    if namespace is None:
        namespace = get_default_namespace()

    body =\
        {
            'apiVersion': 'rbac.authorization.k8s.io/v1',
            'kind': 'ClusterRoleBinding',
            'metadata': {'name': name},
            'roleRef': {
                'apiGroup': 'rbac.authorization.k8s.io',
                'kind': 'ClusterRole',
                'name': role
            },
            'subjects': [{
                'kind': 'ServiceAccount',
                'name': sa,
                'namespace': namespace
            }]
        }
    return v1_rbac.create_cluster_role_binding(body)


def get_cluster_role_binding(name: str):
    """
    Get cluster role binding information

    :param name: Name of cluster role binding
    :return: `V1ClusterRoleBinding <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1ClusterRoleBinding.md>`_
    """
    return v1_rbac.read_cluster_role_binding(name)


def cluster_role_binding_exists(name:str):
    """
    Checks for the existence of the cluster role binding.

    :param name: name of cluster role binding.
    :return: True if binding exists.
    """
    try:
        result = get_cluster_role_binding(name)
        return result.metadata.name == name

    except:
        return False


def delete_cluster_role_binding(name: str):
    """
    Delete cluster role binding

    :param name: cluster role binding name
    :return: None if cluster role binding doesn't exist, otherwise returns `V1Status <https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1Status.md>`_

    """
    if cluster_role_binding_exists(name):
        return v1_rbac.delete_cluster_role_binding(name)
    else:
        return None


###########################################################################
# Custom Functions
###########################################################################
#
# def create_ecr_login_role(name: str):
#     # Create service account AWS login role
#     body = \
#     { 'apiVersion': 'rbac.authorization.k8s.io/v1',
#       'kind': 'ClusterRole',
#       'metadata': { 'name': name },
#       'rules': [
#         { 'apiGroups': [''],
#           'resources': ['serviceaccounts'],
#           'verbs': ['get', 'patch'] },
#
#         { 'apiGroups': [''],
#           'resources': ['secrets'],
#           'verbs': ['create', 'delete']}
#                ]
#     }
#
#     return create_cluster_role(body)
#
# cluster_role = 'test-ecr-role'
#pprint(create_ecr_login_role(cluster_role))
#pprint(get_cluster_role(cluster_role))
#pprint(delete_cluster_role(cluster_role))



