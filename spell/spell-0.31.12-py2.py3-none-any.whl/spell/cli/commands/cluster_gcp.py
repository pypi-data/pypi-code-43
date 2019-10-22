# -*- coding: utf-8 -*-
import random
import subprocess
import tempfile
import os
import yaml
import time
import warnings
from packaging import version

import click

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.log import logger
from spell.cli.utils import is_installed, cluster_utils
from spell.cli.utils.kube_cluster_templates import (
    generate_gke_cluster_rbac_yaml,
    generate_cluster_ambassador_yaml,
)

INGRESS_PORTS = [22, 2376, 9999]  # SSH, Docker Daemon, and Jupyter respectively
SPELL_SERVICE_ACCOUNT = '193976455398-compute@developer.gserviceaccount.com'

required_permissions = [
    'compute.disks.create',
    'compute.disks.list',
    'compute.disks.resize',
    'compute.globalOperations.get',
    'compute.instances.create',
    'compute.instances.delete',
    'compute.instances.get',
    'compute.instances.list',
    'compute.instances.setLabels',
    'compute.instances.setMetadata',
    'compute.instances.setServiceAccount',
    'compute.subnetworks.use',
    'compute.subnetworks.useExternalIp',
    'compute.zones.list',
    'compute.regions.get',
]

cluster_version = 5


@click.command(name="gcp",
               short_help="Sets up GCP VPC as a Spell cluster")
@click.pass_context
@click.option("-n", "--name", "name", help="Name used by Spell for you to identify this GCP cluster")
def create_gcp(ctx, name):
    """
    This command creates a Spell cluster within a GCP VPC of your choosing as an external Spell cluster.
    This will let your organization run runs in that VPC, so your data never leaves
    your VPC. You set an GCS bucket of your choosing for all run outputs to be written to.
    After this cluster is set up you will be able to select the types and number of machines
    you would like Spell to create in this cluster.

    NOTE: This command uses your GCP credentials, activated by running `gcloud auth application-default login`,
    to create the necessary GCP resources for Spell to access and manage those machines. Your GCP credentials will
    need permission to set up these resources.
    """

    # suppress gcloud authentication warnings
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    # Verify the owner is the admin of an org and cluster name is valid
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])
    with api_client_exception_handler():
        spell_client.validate_cluster_name(name)

    try:
        import google.oauth2
        import google.auth
        from googleapiclient import discovery
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return

    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install google-cloud-storage` and rerun this command")
        return
    if version.parse(storage.__version__) < version.parse('1.18.0'):
        click.echo("Please `pip install --upgrade google-cloud-storage` to include HMAC functionality."
                   " Your version is {}, whereas 1.18.0 is required as a minimum".format(storage.__version__))
        return

    if not is_installed("gcloud"):
        raise ExitException("`gcloud` is required, please install it before proceeding. "
                            "See https://cloud.google.com/pubsub/docs/quickstart-cli")

    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command""")
        return

    compute_service = discovery.build('compute', 'v1', credentials=credentials)
    iam_service = discovery.build('iam', 'v1', credentials=credentials)
    resource_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    click.echo("""This command will help you
    - Set up a Google Storage bucket to store your run outputs in
    - Setup a VPC network which Spell will spin up workers in to run your jobs
    - Create a subnet in the VPC
    - Setup a Service Account allowing Spell to spin up and down machines and access the GS bucket""")

    if name is None:
        name = click.prompt("Enter a display name for this cluster within Spell")

    # Normalize the name here
    name = name.replace("_", "-").lower()

    project_id = get_project(resource_service, project_id)
    service_account = get_service_account(iam_service, resource_service, project_id)
    if service_account is None:
        return

    bucket_name = get_bucket_name(ctx, storage, service_account, name, project_id)
    if bucket_name is None:
        return

    network_name, subnet_name, region = get_vpc(compute_service, name, project_id)

    gs_access_key_id, gs_secret_access_key = get_interoperable_s3_access_keys(
        storage,
        project_id,
        service_account['email']
    )

    with api_client_exception_handler():
        cluster = spell_client.create_gcp_cluster(name, service_account['email'], bucket_name,
                                                  network_name, subnet_name, region, project_id, gs_access_key_id,
                                                  gs_secret_access_key)
        cluster_utils.echo_delimiter()
        url = "https://web.spell.run/{}/clusters/{}".format(ctx.obj["owner"], cluster["name"])
        click.echo("Your cluster {} is initialized! Head over to the web console to create machine types "
                   "to execute your runs on - {}".format(name, url))

    spell_client.update_cluster_version(cluster["name"], cluster_version)


def gke_init(ctx, cluster, auth_api_url, gke_cluster_name, nodes_min, nodes_max, node_disk_size):
    """
    Configure an existing GKE cluster for model serving using your current
    `gcloud` credentials. You need to have both `kubectl` and `gcloud` installed.
    This command will install the necessary deployments and services to host
    model servers.
    """

    # suppress gcloud authentication warnings
    import warnings
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    try:
        import kubernetes.client
        import kubernetes.config
    except ImportError:
        raise ExitException("kubernetes (for Python) is required. "
                            "Please `pip install kubernetes` and rerun this command")

    try:
        import google.oauth2
        from googleapiclient import discovery
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return

    if not is_installed("gcloud"):
        raise ExitException("`gcloud` is required, please install it before proceeding. "
                            "See https://cloud.google.com/pubsub/docs/quickstart-cli")
    if not is_installed("kubectl"):
        raise ExitException("`kubectl` is required, please install it before proceeding")

    try:
        credentials, project = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command""")
        return

    resource_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    gcp_project_name = get_project(resource_service, project)

    # Verify valid cluster_name
    spell_client = ctx.obj["client"]
    if cluster["cloud_provider"] != "GCP":
        raise ExitException("Input cluster is using cloud provider {} and therefore cannot use GKE. "
                            "Only GCP is supported".format(cluster["cloud_provider"]))
    region = cluster["networking"]["gcp"]["region"]
    role_creds_gcp = cluster["role_credentials"]["gcp"]

    compute_service = discovery.build('compute', 'v1', credentials=credentials)
    zone = get_zone_from_region(compute_service, project, region)

    response = click.prompt("Create a GKE cluster for model serving? "
                            "You may skip this step if you have previously run it.",
                            type=click.Choice(["create", "skip"])).strip()
    if response == "create":
        create_gke_cluster(gke_cluster_name, gcp_project_name, role_creds_gcp["service_account_id"],
                           zone, nodes_min, nodes_max, node_disk_size)

    elif response == "skip":
        click.echo("Skipping GKE cluster creation, existing contexts are:")
        subprocess.check_call(("kubectl", "config", "get-contexts"))
        kube_ctx = subprocess.check_output(("kubectl", "config", "current-context")).decode('utf-8').strip()
        correct_kube_ctx = click.confirm("Is context '{}' the GKE cluster to use for model serving?".format(kube_ctx))
        if not correct_kube_ctx:
            raise ExitException("Set context to correct GKE cluster with `kubectl config use-context`")

    # Create "serving" namespace
    cluster_utils.create_serving_namespace(kubernetes.config, kubernetes.client)

    # Give Spell permissions to the cluster (via RBAC)
    cluster_utils.echo_delimiter()
    click.echo("Giving Spell RBAC permissions to GKE cluster...")
    try:
        rbac_yaml = generate_gke_cluster_rbac_yaml(role_creds_gcp["service_account_id"])
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(rbac_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--namespace", "serving", "--filename", f.name))
        click.echo("RBAC permissions granted!")
    except Exception as e:
        click.echo("ERROR: Giving Spell RBAC permissions failed. Error was: {}".format(e), err=True)

    # Add Ambassador
    cluster_utils.echo_delimiter()
    click.echo("Setting up Ambassador...")
    try:
        ambassador_yaml = generate_cluster_ambassador_yaml(auth_api_url, cloud="gke")
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(ambassador_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--namespace", "serving", "--filename", f.name))
            click.echo("Waiting for Ambassador to become available...")
            # check until ambassador ingress IP is set, timeout of 60s
            for i in range(60):
                cmd = ("kubectl", "get", "service", "ambassador", "--output",
                       """jsonpath={.status.loadBalancer.ingress[0].ip}""")
                out = subprocess.check_output(cmd)
                if len(out) > 0:
                    break
                time.sleep(1)
            else:
                click.echo("Ambassador was not set up within 60s, please rerun the command")
        click.echo("Ambassador set up!")
    except Exception as e:
        click.echo("ERROR: Setting up Ambassador failed. Error was: {}".format(e), err=True)

    # Add StatsD
    cluster_utils.add_statsd()

    # Upload config to Spell API
    cluster_utils.echo_delimiter()
    click.echo("Uploading config to Spell...")
    try:
        with tempfile.NamedTemporaryFile(mode="r", suffix=".yaml") as f:
            cmd = ("gcloud", "container", "clusters", "get-credentials", gke_cluster_name,
                   "--zone", zone,
                   "--project", gcp_project_name)
            env = os.environ.copy()
            env["KUBECONFIG"] = f.name
            p = subprocess.Popen(cmd, env=env)
            p.communicate()
            if p.returncode != 0:
                raise Exception("gcloud command had exit code {}".format(p.returncode))
            parsed_yaml = yaml.load(f, Loader=yaml.FullLoader)

        # update kubeconfig to use the custom `gcp-svc` auth-provider
        if "users" not in parsed_yaml or \
           len(parsed_yaml["users"]) != 1 or \
           "user" not in parsed_yaml["users"][0] or \
           "auth-provider" not in parsed_yaml["users"][0]["user"]:
            raise Exception("Unexpected kubeconfig yaml generated from gcloud command")
        parsed_yaml["users"][0]["user"]["auth-provider"] = {
            "name": "gcp-svc",
            "config": {"service-acct": role_creds_gcp["service_account_id"]}
        }
        yaml_str = yaml.dump(parsed_yaml, default_flow_style=False)

        with api_client_exception_handler():
            spell_client.set_kube_config(cluster["name"], yaml_str)
        click.echo("Config successfully uploaded to Spell!")
    except Exception as e:
        click.echo("ERROR: Uploading config to Spell failed. Error was: {}".format(e), err=True)

    cluster_utils.echo_delimiter()
    click.echo("Cluster setup complete!")


def get_bucket_name(ctx, storage_api, service_account, cluster_name, project_id):
    storage_client = storage_api.Client(project=project_id)

    cluster_utils.echo_delimiter()
    response = click.prompt("We recommend using an empty GS Bucket for Spell outputs. Would "
                            "you like to make a new bucket or use an existing",
                            type=click.Choice(['new', 'existing'])).strip()
    if response == "new":
        bucket_name = click.prompt(
            "Please enter a name for the GS Bucket Spell will create for run outputs",
            default=u"spell-{}".format(cluster_name.replace("_", "-").lower())).strip()
        while not all([bucket_name[0].isalnum(), bucket_name[-1].isalnum()]):
            click.echo("GCP only allows bucket names that start and end with a number or letter")
            bucket_name = click.prompt(
                "Please enter a name for the GS Bucket Spell will create for run outputs").strip()
        bucket = storage_client.create_bucket(bucket_name)
        click.echo("Created your new bucket {}!".format(bucket_name))
    else:
        req = storage_client.list_buckets()
        buckets = [bucket.name for bucket in req]
        bucket_name = click.prompt("Enter existing bucket name", type=click.Choice(buckets))
    # set bucket permissions
    bucket = storage_client.bucket(bucket_name)
    policy = bucket.get_iam_policy()
    service_account_tag = 'serviceAccount:{}'.format(service_account['email'])
    for role, value in policy.items():
        if role == 'roles/storage.admin' and service_account_tag in value:
            return bucket_name
    policy['roles/storage.admin'].add(service_account_tag)
    bucket.set_iam_policy(policy)
    return bucket_name


def get_region(compute_service, project):
    # Try fetching the default project region
    request = compute_service.projects().get(project=project)
    response = request.execute()

    items = response.get("commonInstanceMetadata", {}).get("items", [])
    region = None
    for item in items:
        if item.get('key') == 'google-compute-default-region':
            region = item.get('value')
    if region is not None:
        if click.confirm("All of this will be done within this project's region '{}' - continue?".format(region),
                         default=True):
            return region
    request = compute_service.regions().list(project=project)
    regions = []
    while request is not None:
        response = request.execute()
        for region in response['items']:
            regions.append(region['name'])
        request = compute_service.regions().list_next(previous_request=request, previous_response=response)
    return click.prompt("Please choose a region for your cluster. This might affect machine availability",
                        type=click.Choice(regions))


def get_vpc(compute_service, cluster_name, project):
    cluster_utils.echo_delimiter()
    region = get_region(compute_service, project)

    # Create VPC
    network_body = {
        'name': cluster_name,
        "autoCreateSubnetworks": False
    }

    click.echo("Creating network...")
    req = compute_service.networks().insert(project=project, body=network_body)
    response = req.execute()
    global_progress_bar(project, compute_service, response)
    click.echo("Created a new VPC/network with name {}!".format(cluster_name))

    network_url = response['targetLink']
    network_name = cluster_name
    cidr = u"10.0.0.0/16"

    # Add firewall rules
    click.echo("Creating firewall rule to allow ingress on ports {}...".format(INGRESS_PORTS))
    request = compute_service.firewalls().insert(project=project, body={
        "name": "{}-spell-api".format(cluster_name),
        "description": "Ingress from Spell API for ssh (22), docker (2376), and jupyter (9999) traffic",
        "network": network_url,
        "sourceRanges": ["0.0.0.0/0"],
        "allowed": [{
            "IPProtocol": "TCP",
            "ports": [str(port) for port in INGRESS_PORTS]
        }],
    })
    response = request.execute()
    global_progress_bar(project, compute_service, response)

    click.echo("Creating firewall rule to allow communication between instances within VPC...")
    request = compute_service.firewalls().insert(project=project, body={
        "name": "{}-internal".format(cluster_name),
        "description": "Allow traffic between all instances within VPC",
        "network": network_url,
        "sourceRanges": [cidr],
        "allowed": [
            {"IPProtocol": "TCP"},
            {"IPProtocol": "UDP"},
        ],
    })
    response = request.execute()
    global_progress_bar(project, compute_service, response)
    click.echo("Firewall rules ready!")

    # Create subnet
    subnetwork_body = {
        "name": cluster_name,
        "network": network_url,
        "ipCidrRange": cidr,
    }

    click.echo("Creating subnetwork...")
    request = compute_service.subnetworks().insert(project=project, body=subnetwork_body, region=region)
    response = request.execute()
    region_progress_bar(project, compute_service, response, region)
    subnet_name = cluster_name

    click.echo("Created a new subnet {} within network {} in region {}!".format(cluster_name, cluster_name, region))

    return network_name, subnet_name, region


def get_project(resource_service, project_id):
    cluster_utils.echo_delimiter()
    projects = resource_service.projects().list().execute()

    if project_id is None or \
        not click.confirm("All of this will be done within your project '{}' - continue?".format(project_id),
                          default=True):
        return click.prompt("Please choose a project id",
                            type=click.Choice([p['projectId'] for p in projects['projects']]))
    return project_id


def get_zone_from_region(compute_service, project, region):
    request = compute_service.regions().get(project=project, region=region)
    region_self_link = request.execute()["selfLink"]

    request = compute_service.zones().list(project=project, filter='region = "{}"'.format(region_self_link))
    response = request.execute()
    if 'items' not in response or len(response['items']) == 0:
        raise ExitException("No compute zones found for region {}".format(region))
    return response['items'][0]['name']


def get_interoperable_s3_access_keys(storage_api, project, service_account):
    storage_client = storage_api.Client(project=project)
    metadata, secret = storage_client.create_hmac_key(service_account)
    return metadata.access_id, secret


def get_service_account(iam_service, resource_service, project):
    cluster_utils.echo_delimiter()
    suffix = str(random.randint(10**6, 10**7))
    service_account_name = "spell-access-{}".format(suffix)
    service_account = iam_service.projects().serviceAccounts().create(
        name='projects/{}'.format(project),
        body={
            'accountId': service_account_name,
            'serviceAccount': {
                'displayName': "spell-access"
            }
        }
    ).execute()
    service_account_name = service_account['name']
    service_account_email = service_account['email']
    try:
        # Allow Spell service account to create keys for external service account
        policy = iam_service.projects().serviceAccounts().getIamPolicy(resource=service_account_name).execute()
        # Service account needs to have access to use itself to attach itself to an instance
        account_user_binding = {
            'role': 'roles/iam.serviceAccountUser',
            'members': ['serviceAccount:{}'.format(SPELL_SERVICE_ACCOUNT),
                        'serviceAccount:{}'.format(service_account_email)]
        }
        token_create_binding = {
            'role': 'roles/iam.serviceAccountTokenCreator',
            'members': ['serviceAccount:{}'.format(SPELL_SERVICE_ACCOUNT)]
        }
        policy['bindings'] = [account_user_binding, token_create_binding]
        policy = iam_service.projects().serviceAccounts().setIamPolicy(
            resource=service_account_name,
            body={
                'resource': service_account_name,
                'policy': policy
            }).execute()
    except Exception as e:
        raise ExitException("Unable to create and attach IAM policies. GCP error: {}".format(e))

    suffix = str(random.randint(10**6, 10**7))
    role_name = "SpellAccess_{}".format(suffix)

    create_role_request_body = {
        "roleId": role_name,
        "role": {
            "title": role_name,
            "includedPermissions": required_permissions
        }
    }

    click.echo("Creating role {} with the following permissions: \n{} \n..."
               .format(role_name, "\n".join('\t'+p for p in required_permissions)))
    request = iam_service.projects().roles().create(parent='projects/{}'.format(project), body=create_role_request_body)
    response = request.execute()
    role_id = response['name']

    click.echo("Assigning role {} to service account {}...".format(role_name, service_account_email))
    request = resource_service.projects().getIamPolicy(resource=project, body={})
    response = request.execute()

    response['bindings'].append({
        'members': ["serviceAccount:{}".format(service_account_email)],
        'role': role_id
    })

    set_iam_policy_body = {
        "policy": response
    }

    request = resource_service.projects().setIamPolicy(resource=project, body=set_iam_policy_body)
    response = request.execute()

    click.echo("Successfully set up service account {}".format(service_account_email))
    return service_account


def create_gke_cluster(cluster_name, gcp_project_name, service_account_id,
                       backplane_zone, nodes_min, nodes_max, node_disk_size):
    """Create the GKE cluster with `gcloud`"""

    try:
        cmd = [
            "gcloud", "container", "clusters", "create", cluster_name,
            "--project", gcp_project_name,
            "--zone", backplane_zone,
            "--node-locations", backplane_zone,
            "--addons=HorizontalPodAutoscaling",
            "--enable-autoscaling",
            "--enable-ip-alias",
            "--num-nodes", "1", "--min-nodes", str(nodes_min), "--max-nodes", str(nodes_max),
            "--service-account", service_account_id,
            "--disk-size", str(node_disk_size),
            "--no-enable-cloud-logging",
            "--no-enable-cloud-monitoring",
            "--labels=spell=model_serving",
            "--no-enable-basic-auth",
        ]
        click.echo("Creating the cluster. This can take a while...")
        subprocess.check_call(cmd)
        click.echo("Cluster created!")

        click.echo("Giving current gcloud user cluster-admin...")
        cmd = ["gcloud", "config", "list", "account", "--format", "value(core.account)"]
        gcloud_user = subprocess.check_output(cmd).decode('utf-8').strip()
        cmd = [
            "kubectl", "create", "clusterrolebinding", "cluster-admin-binding",
            "--clusterrole", "cluster-admin",
            "--user", gcloud_user,
        ]
        subprocess.check_call(cmd)
        click.echo("Current gcloud user {} granted cluster-admin".format(gcloud_user))

    except subprocess.CalledProcessError:
        raise ExitException("Failed to run `gcloud`. Make sure it's installed correctly and "
                            "your inputs are valid. Error details are above in the `gcloud` output.")


def is_gs_bucket_public(bucket_name):
    """
    This command checks if a gs bucket is accessible without credentials - i.e. if the bucket is public.
    """
    import requests
    PERMISSIONS = [
        'storage.objects.get',
        'storage.objects.list'
    ]
    # appropriated from https://github.com/RhinoSecurityLabs/GCPBucketBrute/blob/master/gcpbucketbrute.py#L186
    query_str = '&'.join('permissions={}'.format(p) for p in PERMISSIONS)
    requestURI = 'https://www.googleapis.com/storage/v1/b/{}/iam/testPermissions?{}'
    unauthenticated_permissions = requests.get(requestURI.format(bucket_name, query_str)).json()
    permissions = unauthenticated_permissions.get('permissions', [])
    if len(permissions) == len(PERMISSIONS):
        return True
    return False


@click.pass_context
def add_gs_bucket(ctx, bucket_name, cluster):
    """
    This command adds a cloud storage bucket to SpellFS, which enables interaction with the bucket objects
    via ls, cp, and mounts. It will also add bucket read permissions to the IAM role associated with the
    cluster.

    NOTE: This command uses your GCP credentials, configued through `gcloud auth application-default login`
    Your GCP credentials will need permission to setup these resources.
    """
    spell_client = ctx.obj["client"]
    cluster_name = cluster['name']
    # suppress gcloud authentication warnings
    import warnings
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    try:
        import google.oauth2
        import google.auth
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return

    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install google-cloud-storage` and rerun this command")
        return

    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command""")
        return

    project_id = cluster['networking']['gcp']['project']
    storage_service = storage.Client(project=project_id)

    click.echo("""This command will
    - List your buckets to generate an options menu of buckets that can be added to Spell
    - Add list and read permissions for that bucket to the service account associated with the cluster
    - Ensure that the service account is able to read this bucket.""")

    # Get all buckets
    bucket_names = [bucket.name for bucket in storage_service.list_buckets()]

    # Prompt for bucket name
    if bucket_name is None:
        for bucket in bucket_names:
            click.echo("- {}".format(bucket))
        bucket_name = click.prompt("Please choose a bucket")

    # Check if bucket is public if the bucket name is not one of the returned
    bucket_is_public = False
    if bucket_name not in bucket_names:
        b = storage_service.lookup_bucket(bucket_name)
        if b is None or not b.exists():
            click.echo("GS Bucket {} doesn't exist".format(bucket_name))
            return

        if not is_gs_bucket_public(bucket_name):
            click.echo(
                "Bucket {} is not publicly accessible and is not part of project {}".format(bucket_name, project_id)
            )
            return
        bucket_is_public = True

    # Skip IAM role management logic if bucket is public
    if bucket_is_public:
        click.echo("Bucket {} is public, no IAM updates required.".format(bucket_name))
        with api_client_exception_handler():
            spell_client.add_bucket(bucket_name, cluster['name'], "gs")
        click.echo("Bucket {} has been added to cluster {}!".format(bucket_name, cluster_name))
        return

    bucket = storage_service.lookup_bucket(bucket_name)
    # Add bucket read permissions to policy
    policy = bucket.get_iam_policy()
    service_account_email = cluster['role_credentials']['gcp']['service_account_id']
    service_account_tag = 'serviceAccount:{}'.format(service_account_email)
    policy['roles/storage.objectViewer'].add(service_account_tag)
    bucket.set_iam_policy(policy)

    # Register new bucket to cluster in API
    with api_client_exception_handler():
        spell_client.add_bucket(bucket_name, cluster_name, "gs")
    click.echo("Bucket {} has been added to cluster {}!".format(bucket_name, cluster_name))


@click.pass_context
def update_gcp_cluster(ctx, cluster):
    """
    This command idempotently makes sure that any updates needed since you ran `cluster init gcp` are available.
    """
    spell_client = ctx.obj["client"]
    # suppress gcloud authentication warnings

    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    try:
        import google.oauth2
        import google.auth
        from googleapiclient import discovery
        from googleapiclient.errors import HttpError
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return
    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install google-cloud-storage` and rerun this command")
        return
    if version.parse(storage.__version__) < version.parse('1.18.0'):
        click.echo("Please `pip install --upgrade google-cloud-storage` to include HMAC functionality."
                   " Your version is {}, while 1.18.0 is required as a minimum".format(storage.__version__))
        return
    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command""")
        return

    cloud_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    project_id = cluster['networking']['gcp']['project']
    policy = cloud_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    service_account_id = cluster['role_credentials']['gcp']['service_account_id']

    for binding in policy['bindings']:
        for member in binding['members']:
            if member.endswith(service_account_id):
                role_name = binding['role']

    iam_service = discovery.build('iam', 'v1', credentials=credentials)
    role = iam_service.projects().roles().get(name=role_name).execute()

    need_to_add = list(set(required_permissions) - set(role['includedPermissions']))
    need_to_remove = set(role['includedPermissions']) - set(required_permissions)
    if len(need_to_add) > 0 or len(need_to_remove) > 0:
        click.echo("Your cluster needs to be updated to have the most recent set of role permissions.\n")
        if len(need_to_add) > 0:
            answer = click.confirm("Role {} is currently missing these permissions:\n{}\n"
                                   "Is it ok to add these permissions?".format(role_name, "\n".join(
                                       ["- " + s for s in need_to_add])))
            if not answer:
                raise ExitException("You will not have the ability to use all of the most up to "
                                    "date Spell features until you update your cluster")

            role['includedPermissions'] = role['includedPermissions'] + need_to_add
            iam_service.projects().roles().patch(name=role_name, body=role).execute()
            # refresh role for removal step
            role = iam_service.projects().roles().get(name=role_name).execute()
            click.echo("Successfully updated role {}".format(role_name))
        if len(need_to_remove):
            answer = click.confirm("Role {} currently has unnecessary permissions:\n{}\n"
                                   "Is it ok to remove these permissions?".format(role_name, "\n".join(
                                       ["- " + s for s in need_to_remove])))
            if not answer:
                raise ExitException("You will not have the ability to use all of the most up to "
                                    "date Spell features until you update your cluster")

            role['includedPermissions'] = [perm for perm in role['includedPermissions'] if perm not in need_to_remove]
            iam_service.projects().roles().patch(name=role_name, body=role).execute()
            click.echo("Successfully updated role {}".format(role_name))

    # verify that S3 key is of service account, not user, fetch otherwise
    storage_client = storage.Client(project=project_id)
    key_id = cluster['role_credentials']['gcp']['gs_access_key_id']
    service_account_email = cluster['role_credentials']['gcp']['service_account_id']
    hmac_keys = storage_client.list_hmac_keys(service_account_email=service_account_email)
    hmac_key_ids = [metadata.access_id for metadata in hmac_keys if metadata.state == "ACTIVE"]
    if len(hmac_key_ids) == 0 or key_id not in set(hmac_key_ids):
        answer = click.confirm("Spell previously used the user-specific S3 Interoperable Access Keys for Google Storage"
                               " access, but now uses the more secure HMAC key of the service account."
                               " Is it ok to create these keys and update your cluster?")
        if answer:
            gs_access_key_id, gs_secret_access_key = get_interoperable_s3_access_keys(
                storage,
                project_id,
                service_account_email
            )
            spell_client.update_cluster_HMAC_key(cluster["name"], gs_access_key_id, gs_secret_access_key)

    # Add firewall rule for internal traffic
    current_version = cluster[u'version']
    if current_version < 5:
        click.echo("Ensuring firewall rules are up to date...")

        compute_service = discovery.build('compute', 'v1', credentials=credentials)

        region = cluster[u'networking'][u'gcp'][u'region']
        subnet_name = cluster[u'networking'][u'gcp'][u'subnet']
        request = compute_service.subnetworks().get(project=project_id, region=region, subnetwork=subnet_name)
        subnet = request.execute()

        cidr = subnet[u'ipCidrRange']
        network_url = subnet[u'network']
        rule_name = "{}-internal".format(cluster[u'name'])
        body = {
            "name": rule_name,
            "description": "Allow traffic between all instances within VPC",
            "network": network_url,
            "sourceRanges": [cidr],
            "allowed": [
                {"IPProtocol": "TCP"},
                {"IPProtocol": "UDP"},
            ],
        }

        request = compute_service.firewalls().insert(project=project_id, body=body)
        try:
            response = request.execute()
            global_progress_bar(project_id, compute_service, response)
            click.echo("Firewall rules updated!")
        # If this rule already exists update it because due to a bug in version 4
        # the source IPs are incorrect
        except HttpError as err:
            if err.resp.status != 409:
                raise

            request = compute_service.firewalls().update(
                project=project_id, firewall=rule_name, body=body)
            response = request.execute()
            global_progress_bar(project_id, compute_service, response)

    spell_client.update_cluster_version(cluster["name"], cluster_version)

    click.echo("Congratulations, your cluster {} is up to date".format(cluster["name"]))


def delete_gcp_cluster(ctx, cluster):
    """
    Deletes an GCP cluster, including the Spell Cluster, Machine Types,
    Model Servers, VPC, IAM role, and IAM policies associated with this cluster.
    """

    # suppress gcloud authentication warnings
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    # Verify the owner is the admin of an org and cluster name is valid
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        import google.oauth2
        import google.auth
        from google.api_core.exceptions import NotFound
        from googleapiclient import discovery
        from googleapiclient.errors import HttpError
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return

    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install google-cloud-storage` and rerun this command")
        return
    if version.parse(storage.__version__) < version.parse('1.18.0'):
        click.echo("Please `pip install --upgrade google-cloud-storage` to include HMAC functionality."
                   " Your version is {}, whereas 1.18.0 is required as a minimum".format(storage.__version__))
        return

    if not is_installed("gcloud"):
        raise ExitException("`gcloud` is required, please install it before proceeding. "
                            "See https://cloud.google.com/pubsub/docs/quickstart-cli")

    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to delete the cluster, and rerun this command""")
        return

    compute_service = discovery.build('compute', 'v1', credentials=credentials)
    iam_service = discovery.build('iam', 'v1', credentials=credentials)
    resource_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    click.echo("""This command will help you delete your Spell cluster. It will
    - Delete the VPC network which Spell created to spin up workers in
    - Delete all subnets in the VPC
    - Delete the IAM Service Account and roles allowing Spell to spin up and down
      machines and access the GS bucket
    - IF EXISTS Delete Model Server GKE cluster
    - OPTIONALLY Delete the Google Storage bucket used to store your run outputs
      (you will be prompted to choose to keep or delete the bucket)""")
    if not click.confirm("Are you SURE you want to delete the spell cluster {}?".format(cluster["name"])):
        return

    project_id = get_project(resource_service, project_id)

    # Delete Machine Types and Model Servers on cluster first
    with api_client_exception_handler():
        click.echo("Sending message to Spell to remove all Machine Types "
                   "from the cluster {}...".format(cluster["name"]))
        spell_client.delete_cluster_contents(cluster["name"])

    # Delete associated GKE cluster if it exists
    if cluster["has_kube_config"]:
        delete_gke_cluster(project_id)

    # Block until cluster is drained. This is necessary because the API will fail to
    # drain if we delete the IAM role before the machine types are marked as drained
    cluster_utils.block_until_cluster_drained(spell_client, cluster["name"])

    # Delete Firewalls
    delete_firewall(compute_service, project_id, "{}-spell-api".format(cluster['name']))
    delete_firewall(compute_service, project_id, "{}-internal".format(cluster['name']))

    # Delete Subnets
    try:
        subnet_name = cluster['name']
        region = cluster["networking"]["gcp"]["region"]
        click.echo("Deleting subnetwork {}...".format(subnet_name))
        response = compute_service.subnetworks().delete(
                    project=project_id, region=region, subnetwork=subnet_name).execute()
        region_progress_bar(project_id, compute_service, response, region)
        click.echo("Deleted subnetwork {}".format(subnet_name))
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("subnetwork {} is already deleted".format(subnet_name))
        else:
            raise ExitException("Error attempting to delete subnetwork {}. "
                                "Err was {}".format(subnet_name, err))

    # Delete VPC
    try:
        vpc_name = cluster['networking']['gcp']['vpc']
        click.echo("Deleting VPC {}...".format(vpc_name))
        response = compute_service.networks().delete(project=project_id, network=vpc_name).execute()
        global_progress_bar(project_id, compute_service, response)
        click.echo("VPC {} deleted".format(vpc_name))
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("VPC {} is already deleted".format(vpc_name))
        else:
            raise ExitException("Error attempting to delete VPC {}. "
                                "Err was {}".format(vpc_name, err))

    # Delete Role
    iam_policies = resource_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    binding_to_remove = None
    for binding in iam_policies['bindings']:
        if "serviceAccount:{}".format(cluster['role_credentials']['gcp']['service_account_id']) in binding['members']:
            binding_to_remove = binding
            break
    if binding_to_remove is None:
        click.echo("Could not find role to delete, skipping")
    else:
        role_name = binding_to_remove['role']
        click.echo("Found role {} to delete, deleting".format(role_name))
        try:
            response = iam_service.projects().roles().delete(name=role_name).execute()
        except HttpError as err:
            if "already deleted" in err._get_reason():
                click.echo("Role {} is already deleted".format(role_name))
            else:
                raise ExitException("Error attempting to delete role {}. "
                                    "Err was {}".format(role_name, err))
        # Delete binding
        click.echo("Deleting binding for role {}...".format(role_name))
        iam_policies['bindings'].remove(binding_to_remove)
        set_iam_policy_body = {
            "policy": iam_policies
        }
        resource_service.projects().setIamPolicy(resource=project_id, body=set_iam_policy_body).execute()
        click.echo("Deleted binding for role {}".format(role_name))

    # Delete Service Account
    try:
        service_acct_name = "projects/{}/serviceAccounts/{}".format(
            project_id, cluster['role_credentials']['gcp']['service_account_id'])
        iam_service.projects().serviceAccounts().delete(name=service_acct_name).execute()
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("Service account {} is already deleted".format(service_acct_name))
        else:
            raise ExitException("Error attempting to delete service account {}. "
                                "Err was {}".format(service_acct_name, err))

    # Optionally delete the output bucket
    bucket_name = cluster['storage_uri']
    if click.confirm("Delete bucket {}? WARNING: This will delete all the data in the bucket".format(bucket_name)):
        try:
            storage_client = storage.Client(project=project_id)
            bucketObj = storage_client.get_bucket(bucket_name)
            bucketObj.delete(force=True)
            click.echo("Deleted bucket {}".format(bucket_name))
        except NotFound as err:
            click.echo("Bucket {} is already deleted!".format(bucket_name))
        except Exception as err:
            raise ExitException("Failed to delete bucket {}."
                                "Err was {}".format(bucket_name, err))

    # Last step is to mark the cluster as deleted
    with api_client_exception_handler():
        spell_client.delete_cluster(cluster["name"])
        click.echo("Successfully deleted cluster on Spell")


def delete_firewall(compute_service, project_id, firewall_name):
    from googleapiclient.errors import HttpError
    try:
        click.echo("Deleting Firewall {}...".format(firewall_name))
        response = compute_service.firewalls().delete(project=project_id, firewall=firewall_name).execute()
        global_progress_bar(project_id, compute_service, response)
        click.echo("Deleted Firewall {}".format(firewall_name))
    except HttpError as err:
        if err.resp.status == 404:
            click.echo("Firewall {} is already deleted".format(firewall_name))
        else:
            raise ExitException("Error attempting to delete Firewall {}. "
                                "Err was {}".format(firewall_name, err))


def delete_gke_cluster(project_id):
    try:
        cluster_utils.echo_delimiter()
        click.echo("Detected an associated Model Server GKE Cluster. Listing out the known GKE clusters:")
        cmd = ["gcloud", "container", "clusters", "list", "--project", project_id]
        subprocess.check_call(cmd)
        if click.confirm("Would you like to delete the associated Model Server GKE cluster "
                         "listed above? If you do NOT see it listed above, respond 'n' to skip "
                         "this step."):
            gke_name = click.prompt("What is the name of the GKE cluster? "
                                    "Please choose one of the names listed above. "
                                    "NOTE: This is the name used in GKE, NOT the name in Spell)",
                                    default=u"spell-model-serving").strip()
            click.echo("Deleting GKE cluster {}. This can take a while!".format(gke_name))
            cmd = ["gcloud", "container", "clusters", "delete", gke_name, "--project", project_id]
            subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        click.echo("Failed to run `gcloud`. Make sure it's installed correctly and "
                   "your inputs are valid. Error details are above in the `gcloud` output. "
                   "You will need to delete your GKE cluster using `gcloud` manually.")


def global_progress_bar(project, compute_service, response):
    with click.progressbar(length=100, show_eta=False) as bar:
        while response['status'] != 'DONE':
            bar.update(response['progress'])
            response = compute_service.globalOperations().get(project=project, operation=response['name']).execute()
        if 'error' in response and 'errors' in response['error']:
            first_error = response['error']['errors'][0]
            raise GcpException("Error with GCP API {}: {}".format(first_error['code'], first_error['message']))
        bar.update(100)


def region_progress_bar(project, compute_service, response, region):
    with click.progressbar(length=100, show_eta=False) as bar:
        while response['status'] != 'DONE':
            bar.update(response['progress'])
            response = compute_service.regionOperations().get(project=project,
                                                              region=region,
                                                              operation=response['name']
                                                              ).execute()
        if 'error' in response and 'errors' in response['error']:
            first_error = response['error']['errors'][0]
            raise GcpException("Error with GCP API {}: {}".format(first_error['code'], first_error['message']))
        bar.update(100)


class GcpException(click.ClickException):
    def __init__(self, message):
        super(GcpException, self).__init__(message)

    def show(self):
        logger.error(self.message)
