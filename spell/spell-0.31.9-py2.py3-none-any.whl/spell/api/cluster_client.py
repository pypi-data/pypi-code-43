from spell.api import base_client
from spell.api.utils import url_path_join

CLUSTER_RESOURCE_URL = "clusters"


class ClusterClient(base_client.BaseClient):

    def get_cluster(self, cluster_name):
        """Get info for a cluster given a cluster_name.

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name))
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def list_clusters(self):
        """List info for all current owner clusters."""
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner))
        self.check_and_raise(r)
        return self.get_json(r)["clusters"]

    def validate_cluster_name(self, name):
        """Throws an error if this name is an illegal name for a cluster.

        Keyword arguments:
        name -- a potential name for a cluster
        """
        r = self.request("get", url_path_join(CLUSTER_RESOURCE_URL, self.owner, "validate_name", name))
        self.check_and_raise(r)

    def create_aws_cluster(self, name, role_arn, external_id, read_policy, security_group_id, s3_bucket,
                           vpc_id, subnets, region):
        """Construct a cluster to map to a users aws cluster.

        Keyword arguments:
        name -- a display name for the cluster
        role_arn -- the aws arn of a role granting Spell necessary permissions to manage the cluster
        external_id -- needed to assume the role
        read_policy -- name of the s3 read policy associated with the IAM role
        security_group_id -- security group in the VPC with SSH and Docker port access to workers
        s3_bucket - a bucket to store run outputs in
        vpc_id - the id of vpc to setup this cluster in
        subnets - all subnets which Spell will attempt to launch machines in
            (due to aws capacity constraints more is preferable)
        region - the aws region of this vpc
        """
        payload = {
            "cluster_name": name,
            "role_arn": role_arn,
            "external_id": external_id,
            "read_policy": read_policy,
            "security_group_id": security_group_id,
            "s3_bucket": s3_bucket,
            "vpc_id": vpc_id,
            "subnets": subnets,
            "region": region,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, "aws")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def create_gcp_cluster(self, name, service_account_id, gs_bucket,
                           vpc_id, subnet, region, project, gs_access_key_id, gs_secret_access_key):
        """Construct a cluster to map to a users gcp cluster.

        Keyword arguments:
        name -- a display name for the cluster
        service_account_id -- the email of a service account granting Spell necessary permissions to manage the cluster
        gs_bucket - a bucket to store run outputs in
        vpc_id - name of network to run machines in
        subnets - a subnet in vpc_id to run machines in
        region - region in which the subnets live
        project - project that network lives in
        gs_access_key_id - gs interoperable s3 access key
        gs_secret_access_key - gs interoperable s3 access secret
        """

        payload = {
            "cluster_name": name,
            "gs_bucket": gs_bucket,
            "vpc_id": vpc_id,
            "subnet": subnet,
            "region": region,
            "project": project,
            "service_account_id": service_account_id,
            "gs_access_key_id": gs_access_key_id,
            "gs_secret_access_key": gs_secret_access_key,
        }
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, "gcp")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)
        return self.get_json(r)["cluster"]

    def set_kube_config(self, cluster_name, kube_config):
        """Submit a model-server kubeconfig to be stored as the
        active model-server cluster for the current org.

        Keyword arguments:
        cluster_name -- the name of the cluster to update
        kube_config -- a string containing a yaml kubeconfig
        """
        payload = {"kube_config": kube_config}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "kube_config")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def add_bucket(self, bucket_name, cluster_name, provider):
        """Add a bucket to SpellFS using the permissions of the specified cluster

        Keyword arguments:
        bucket_name -- the name of the bucket
        cluster_name -- the name of the cluster
        provider -- storage provider for bucket ("s3", "gs", etc.)
        """
        payload = {"bucket": bucket_name, "provider": provider}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "bucket")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def update_cluster_version(self, cluster_name, version):
        """Updates a cluster's version number in the database

        Keyword arguments:
        cluster_name -- the name of the cluster
        version -- the new version number to write to the database
        """
        payload = {"version": version}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "update_version")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def update_cluster_HMAC_key(self, cluster_name, access_key, secret):
        """Updates a cluster's HMAC key and secret in the database

        Keyword arguments:
        cluster_name -- the name of the cluster
        access_key -- the access key for the service account
        secret -- the secret associated with the access key
        """
        payload = {"access_key": access_key, "secret": secret}
        endpoint = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "update_gcp_s3_key")
        r = self.request("put", endpoint, payload=payload)
        self.check_and_raise(r)

    def delete_cluster_contents(self, cluster_name):
        """Deletes all associated Spell managed infrastructure for a cluster

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "delete_contents")
        r = self.request("put", url)
        self.check_and_raise(r)

    def is_cluster_drained(self, cluster_name):
        """Returns 200 if the cluster is drained and 400 if not

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name, "is_drained")
        r = self.request("get", url)
        self.check_and_raise(r)

    def delete_cluster(self, cluster_name):
        """Marks a cluster as deleted in the db

        Keyword arguments:
        cluster_name -- the name of the cluster
        """
        url = url_path_join(CLUSTER_RESOURCE_URL, self.owner, cluster_name)
        r = self.request("delete", url)
        self.check_and_raise(r)
