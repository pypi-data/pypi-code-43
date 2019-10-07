# -*- coding: utf-8 -*-
import click

from spell.cli.commands.cluster_aws import create_aws, eks_init, add_s3_bucket, update_aws_cluster
from spell.cli.commands.cluster_gcp import create_gcp, gke_init, add_gs_bucket, update_gcp_cluster
from spell.cli.utils import cluster_utils, tabulate_rows, HiddenOption
from spell.cli.exceptions import api_client_exception_handler, ExitException


@click.group(name="cluster", short_help="Manage external clusters",
             help="Manage external clusters on Spell\n\n"
                  "With no subcommand, display all your external clusters",
             invoke_without_command=True)
@click.pass_context
def cluster(ctx):
    """
    List all external clusters for current owner
    """
    if not ctx.invoked_subcommand:
        spell_client = ctx.obj["client"]
        cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])
        clusters = spell_client.list_clusters()
        if len(clusters) == 0:
            click.echo("There are no external clusters to display.")
            return
        data = [(c['name'], c['cloud_provider'], c['storage_uri']) for c in clusters]
        tabulate_rows(data, headers=["NAME", "PROVIDER", "STORAGE_URI"])


@click.command(name="add-bucket",
               short_help="Adds a cloud storage bucket to SpellFS")
@click.pass_context
@click.option("--bucket", "bucket_name", help="Name of bucket")
@click.option("--cluster-name", default=None, help="Name of cluster to add bucket permissions to")
@click.option("-p", "--profile", "profile", default=u"default",
              help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
                   "You will be prompted to confirm the Key and Region are correct before continuing. "
                   "This key will be used to adjust IAM permissions of the role associated with the cluster "
                   "that the bucket is being added to.")
def add_bucket(ctx, bucket_name, cluster_name, profile):
    """
    This command adds a cloud storage bucket (S3 or GS) to SpellFS, which enables interaction with the bucket objects
    via ls, cp, and mounts. It will also updates the permissions of that bucket to allow Spell read access to it
    """
    cluster = deduce_cluster(ctx, cluster_name)

    cluster_type = cluster['cloud_provider']
    if cluster_type == 'AWS':
        ctx.invoke(add_s3_bucket, bucket_name=bucket_name, cluster=cluster, profile=profile)
    elif cluster_type == 'GCP':
        if profile != 'default':
            click.echo("--profile is not a valid option for adding a gs bucket")
            return
        ctx.invoke(add_gs_bucket, bucket_name=bucket_name, cluster=cluster)
    else:
        raise Exception("Unknown cluster with provider {}, exiting.".format(cluster_type))


def deduce_cluster(ctx, cluster_name):
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    clusters = spell_client.list_clusters()
    if len(clusters) == 0:
        click.echo("No clusters defined, please run `spell cluster init aws` or `spell cluster init gcp`")
        return
    while len(clusters) != 1:
        if cluster_name is not None:
            clusters = [c for c in clusters if c['name'] == cluster_name]
        if len(clusters) == 0:
            click.echo("No clusters with the name {}, please try again.")
            return
        elif len(clusters) > 1:  # two or more clusters
            cluster_names = [c['name'] for c in clusters]
            cluster_name = click.prompt("You have multiple clusters defined. Please select one.",
                                        type=click.Choice(cluster_names)).strip()
    cluster = clusters[0]

    return cluster


@click.command(name="update",
               short_help="Makes sure your Spell cluster is fully up to date and able to support the latest features")
@click.pass_context
@click.option("--cluster-name", default=None, help="Name of cluster to update")
@click.option("-p", "--profile", "profile", default=u"default",
              help="This AWS profile will be used to get your Access Key ID and Secret as well as your Region. "
                   "You will be prompted to confirm the Key and Region are correct before continuing. "
                   "This key will be used to adjust IAM permissions of the role associated with the cluster "
                   "that the bucket is being added to.")
def update(ctx, cluster_name, profile):
    """
    This command makes sure your Spell cluster is fully up to date and able to support the latest features
    """
    cluster = deduce_cluster(ctx, cluster_name)

    cluster_type = cluster['cloud_provider']
    if cluster_type == 'AWS':
        ctx.invoke(update_aws_cluster, cluster=cluster, profile=profile)
    elif cluster_type == 'GCP':
        if profile != 'default':
            click.echo("--profile is not a valid option for adding a gs bucket")
            return
        ctx.invoke(update_gcp_cluster, cluster=cluster)
    else:
        raise Exception("Unknown cluster with provider {}, exiting.".format(cluster_type))


@click.command(name="init-model-server",
               short_help="Sets up a GKE/EKS cluster to host model servers")
@click.pass_context
@click.option("-c", "--cluster", "cluster_name", type=str,
              help="The spell cluster name of the cluster that you would like to configure this "
                   "model serving cluster to work with. If it's not specified, it will default to "
                   "the ONE cluster the current owner has, or fail if the current owner has more than one cluster.")
@click.option("--model-serving-cluster", type=str, default="spell-model-serving",
              help="Name of the newly created GKE/EKS cluster")
@click.option("--auth-api-url", cls=HiddenOption, type=str,
              help="URL of the spell API server used by Ambassador for authentication. "
                   "This must be externally accessible")
@click.option("--nodes-min", type=int, default=1,
              help="Minimum number of nodes in the model serving cluster (default 1)")
@click.option("--nodes-max", type=int, default=2,
              help="Minimum number of nodes in the model serving cluster (default 2)")
@click.option("--node-disk-size", type=int, default=50,
              help="Size of disks on each node in GB (default 50GB)")
def init_model_server(ctx, cluster_name, model_serving_cluster, auth_api_url,
                      nodes_min, nodes_max, node_disk_size):
    """
    Deploy a GKE or EKS cluster for model serving
    by auto-detecting the cluster provider.
    """
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])
    with api_client_exception_handler():
        cluster = cluster_utils.get_spell_cluster(spell_client, ctx.obj["owner"], cluster_name)
    if cluster['cloud_provider'] == 'AWS':
        eks_init(ctx, cluster, auth_api_url, model_serving_cluster,
                 nodes_min, nodes_max, node_disk_size)
    elif cluster['cloud_provider'] == 'GCP':
        gke_init(ctx, cluster, auth_api_url, model_serving_cluster,
                 nodes_min, nodes_max, node_disk_size)
    else:
        raise ExitException("Unsupported cloud provider: {}".format(cluster['cloud_provider']))


@cluster.group(name="init", short_help="Create a cluster",
               help="Create a new aws/gcp cluster for your org account\n\n"
                    "Set up a cluster to use machines in your own AWS/GCP account")
@click.pass_context
def init(ctx):
    pass


# register generic subcommands
cluster.add_command(add_bucket)
cluster.add_command(update)
# register gke/eks subcommands
cluster.add_command(init_model_server)

# register init subcommands
init.add_command(create_aws)
init.add_command(create_gcp)
