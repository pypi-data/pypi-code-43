#!/usr/bin/env python
# TODO: split this into multiple modules
import os
import glob
import json
import click
import tabulate
import requests
from collections import OrderedDict

from ncapi_client.utils import AttrDict
from ncapi_client.client import Client
from ncapi_client.dataset import Dataset
from ncapi_client.model import Model
from ncapi_client.job import Job
from ncapi_client.trained_model import TrainedModel
from ncapi_client.training import Training
from ncapi_client.session import Session
from ncapi_client.prediction import Prediction


# TODO: should this be a part of the client?
def _auth_client(refresh=False):
    keys_path = os.path.join(os.environ["HOME"], ".config", "ncs", "keys.json")
    if not os.path.exists(keys_path) or refresh:
        if not os.path.exists(os.path.dirname(keys_path)):
            os.makedirs(os.path.dirname(keys_path))

        username = click.prompt("Please enter your username")
        password = click.prompt("Please enter your password", hide_input=True)
        url = click.prompt("Please enter API url", default="https://0.0.0.0:5000")

        c = Client(url, username, password)
        # TODO: switch to token auth
        # with open(keys_path, "w") as f:
        #     json.dump(dict(access_token=c.access_token, url=url), f)
        with open(keys_path, "w") as f:
            json.dump(dict(username=username, password=password, url=url), f)
        return c

    with open(keys_path, "r") as f:
        keys = json.load(f)
    # TODO: switch to tokens (!)
    # c = Client(url=keys["url"], access_token=keys["access_token"])
    c = Client(url=keys["url"], username=keys["username"], password=keys["password"])
    return c


def print_list_of_dicts(data):
    types = OrderedDict()
    for d in data:
        key = tuple(d.keys())
        types.setdefault(key, []).append(d.values())
    for header, rows in types.items():
        print(tabulate.tabulate(rows, header))


def print_dict(data):
    print(tabulate.tabulate(data.items(), ["Attribute", "Value"]))


def print_dict_of_dicts(data):
    for k, d in data.items():
        print(k)
        print("-" * len(k))
        print_dict(d)


def print_output(data):
    if not data:
        print("Output is empty")
    elif isinstance(data, list):
        if isinstance(data[0], dict):
            print_list_of_dicts(data)
        elif isinstance(data[0], str):
            print_json(data)
        else:
            raise click.ClickException("Unsupported output type")
    elif isinstance(data, dict):
        if isinstance(list(data.values())[0], dict):
            print_dict_of_dicts(data)
        else:
            print_dict(data)


def print_json(data):
    print(json.dumps(data, indent=4, sort_keys=True))


@click.group()
def cli():
    # TODO: add an option with the type of the output text / json?
    pass


@cli.command()
def auth():
    """Authenticate with your username and password."""
    _auth_client(refresh=True)


@cli.group()
def dataset():
    """Dataset management."""


@dataset.command("add")
@click.argument("name")
@click.argument("path", type=click.Path(exists=True))
@click.option("--description", type=click.Path(), required=False)
@click.option(
    "--split",
    type=click.FloatRange(0.0, 1.0),
    default=0.9,
    required=False,
    show_default=True,
)
@click.option(
    "--max-degree",
    type=click.IntRange(4, 16),
    default=10,
    required=False,
    show_default=True,
)
def dataset_add(name, path, description=None, split=None, max_degree=None):
    """Add a new NAME dataset located at local PATH."""
    c = _auth_client()

    # TODO: we should add a progress bar?
    if description:
        with open(description, "r") as fh:
            description = json.load(fh)
    ds = None
    try:
        files = []
        for ext in (".csv", ".obj", ".json", ".stl", ".npy", ".dat", ".plt"):
            files += glob.glob(f"{path}/**/*{ext}", recursive=True)
        if not files:
            print("no files at the path")
        ds = Dataset.add(c, name, files, description, split, max_degree, notebook=False)
        print_output(ds.info)
    except:
        if ds:
            ds.delete()
        raise


@dataset.command("list")
def dataset_list():
    """List all the datasets."""
    c = _auth_client()
    print_output([d.info for d in c.datasets])


@dataset.command("get")
@click.argument("uuid")
def dataset_get(uuid):
    """Get verbose info about the dataset."""
    c = _auth_client()
    print_output(Dataset(c, uuid).info)


@dataset.command("convert")
@click.argument("uuid")
@click.option("--target-format", default="npy_indiv")
def dataset_convert(uuid, target_format):
    """Convert the dataset to one of the supported formats."""
    c = _auth_client()
    print_output(Dataset(c, uuid).convert(target_format))


@dataset.command("get")
@click.argument("uuid")
def dataset_get(uuid):
    """Get verbose info about the dataset."""
    c = _auth_client()
    print_output(Dataset(c, uuid).info)


@dataset.command("schema")
@click.argument("uuid")
def dataset_schema(uuid):
    """Get the schema information about the dataset."""
    c = _auth_client()
    print_output(Dataset(c, uuid).schema)


@dataset.command("delete")
@click.argument("uuid")
def dataset_delete(uuid):
    """Deletes the dataset."""
    c = _auth_client()
    Dataset(c, uuid).delete()


@dataset.group("samples")
def dataset_samples():
    """Accessing individual dataset samples."""
    pass


@dataset_samples.command("list")
@click.argument("uuid")
def dataset_samples_list(uuid):
    """List samples of the dataset."""
    c = _auth_client()
    print_output(Dataset(c, uuid).samples)


@dataset_samples.command("get")
@click.argument("uuid")
@click.argument("sample_id")
def dataset_samples_get(uuid, samples):
    """Get (download) a given sample from the dataset."""
    c = _auth_client()
    print_output(Dataset(c, uuid).sample(sample_id))


@dataset.group("files")
def dataset_files():
    """Dataset file management."""
    pass


@dataset_files.command("list")
@click.argument("uuid")
def dataset_files_list(uuid):
    """List files in the dataset."""
    c = _auth_client()
    print_output(Dataset(c, uuid).samples)


@dataset_files.command("get")
@click.argument("uuid")
def dataset_files_get(uuid):
    """Get (download) files from the dataset."""
    pass


@dataset_files.command("add")
@click.argument("files", nargs=-1)
def dataset_files_add(uuid, files):
    """Add one or more files to a dataset."""
    pass


@dataset.group("format")
def dataset_format():
    """Dataset format management."""
    pass


@dataset_format.command("list")
@click.argument("uuid")
def dataset_format_list(uuid):
    """List available formats."""
    c = _auth_client()
    print_output(Dataset(c, uuid).formats)


@dataset_format.command("get")
@click.argument("uuid")
@click.argument("data_format")
def dataset_format_get(uuid, data_format):
    """Get verbose format info."""
    c = _auth_client()
    print_output(Dataset(c, uuid).format(data_format))


@dataset_format.command("delete")
@click.argument("uuid")
@click.argument("data_format")
def dataset_format_delete(uuid, data_format):
    """Delete a given format."""
    c = _auth_client()
    Dataset(c, uuid).format_delete(data_format)


@cli.group()
def model():
    """Model management."""
    pass


@model.command("add")
@click.argument("config_path", type=click.Path(exists=True), required=False)
@click.option("--class-name", type=str)
@click.option("--name", type=str)
def model_add(config_path, class_name, name):
    """Add a model with yaml config at CONFIG_PATH."""
    c = _auth_client()
    if config_path:
        Model.add(c, config=config_path)
    elif class_name and name:
        Model.add(c, name=name, class_name=class_name)
    else:
        raise click.ClickException(
            "you should either specify the config or name and class_name"
        )


@model.command("list")
def model_list():
    """List available models."""
    c = _auth_client()
    print_output([m.info for m in c.models])


@model.command("get")
@click.argument("uuid")
def model_get(uuid):
    """Get verbose info about the model."""
    c = _auth_client()
    print_output(Model(c, uuid).info)


@model.command("delete")
@click.argument("uuid")
def model_delete(uuid):
    """Delete a model by UUID."""
    c = _auth_client()
    Model(c, uuid).delete()


@model.command("config")
@click.argument("uuid")
def model_config(uuid):
    """Get verbose info about the model."""
    c = _auth_client()
    print_output(Model(c, uuid).config)


@cli.group()
def train():
    """Training jobs management."""
    pass


@train.command("list")
def train_list():
    """List available trainings."""
    c = _auth_client()
    print_output([t.info for t in c.trainings])


@train.command("submit")
@click.argument("model")
@click.argument("dataset")
def train_submit(model, dataset):
    """Submit a training to the queue."""
    c = _auth_client()
    print_output(Training.submit(c, model, dataset).info)


@train.command("delete")
@click.argument("uuid")
def train_delete(uuid):
    """Delete a training."""
    c = _auth_client()
    Training(c, uuid).delete()


@train.command("get")
@click.argument("uuid")
def train_get(uuid):
    """Get verbose information about a training."""
    c = _auth_client()
    print_output(Training(c, uuid).info)


@train.command("stop")
@click.argument("uuid")
def train_stop(uuid):
    """Stop a training."""
    c = _auth_client()
    Training(c, uuid).stop()


@train.command("logs")
@click.argument("uuid")
def train_logs(uuid):
    """Get full training logs."""
    c = _auth_client()
    print_json(Training(c, uuid).logs)


@train.command("checkpoints")
@click.argument("uuid")
def train_checkpoints(uuid):
    """Get a list of model checkpoints."""
    c = _auth_client()
    print_json(Training(c, uuid).checkpoints)


@train.command("restart")
@click.argument("uuid")
def train_restart(uuid):
    """Restart a training."""
    c = _auth_client()
    Training(c, uuid).restart()


@train.command("save")
@click.argument("uuid")
@click.argument("checkpoint")
@click.argument("name", required=False)
def train_save(uuid, checkpoint, name=None):
    """Saves a training checkpoint as a new trained-model."""
    c = _auth_client()
    Training(c, uuid).save(checkpoint, name=name)


@cli.group()
def trained_model():
    """Trained model management."""
    pass


@trained_model.command("list")
def trained_model_list():
    """List trained models."""
    c = _auth_client()
    print_output([tm.info for tm in c.trained_models])


@trained_model.command("add")
@click.argument("config", type=click.Path(exists=True))
@click.argument("checkpoint", type=str)
def trained_model_add(config, checkpoint):
    """Add a trained model by providing a config and checkpoints."""
    c = _auth_client()
    print_output(TrainedModel.add(c, config, checkpoint).info)


@trained_model.command("delete")
@click.argument("uuid", type=str)
def trained_model_delete(uuid):
    """Completely delete a trained model."""
    c = _auth_client()
    TrainedModel(c, uuid).delete()


@trained_model.command("get")
@click.argument("uuid", type=str)
def trained_model_get(uuid):
    """Get verbose info."""
    c = _auth_client()
    print_output(TrainedModel(c, uuid).info)


@trained_model.command("config")
@click.argument("uuid", type=str)
def trained_model_config(uuid):
    """Returns the model configuration."""
    c = _auth_client()
    print_output(TrainedModel(c, uuid).config)


@trained_model.command("download")
@click.argument("uuid", type=str)
@click.argument("dst-dir", type=click.Path(exists=True), default="./")
def trained_model_config(uuid, dst_dir):
    """Download a trained model archive and save it to DST_DIR."""
    c = _auth_client()
    archive = TrainedModel(c, uuid).download()
    with open(os.path.join(dst_dir, archive.name), "wb") as fh:
        fh.write(archive.read())


@cli.group("jobs")
def jobs():
    """Job management."""
    pass


@jobs.command("list")
def jobs_list():
    """List all the jobs."""
    c = _auth_client()
    print_output([j.info for j in c.jobs])


@jobs.command("get")
@click.argument("uuid")
def job_get(uuid):
    """Get a verbose job info."""
    c = _auth_client()
    print_output(Job(c, uuid).info)


@jobs.command("stop")
@click.argument("uuid")
def job_stop(uuid):
    """Stop a job, with a possiblity to restart."""
    c = _auth_client()
    Job(c, uuid).stop()


@jobs.command("delete")
@click.argument("uuid")
def job_delete(uuid):
    """Delete a job completely."""
    c = _auth_client()
    Job(c, uuid).delete()


@jobs.command("restart")
@click.argument("uuid")
def job_restart(uuid):
    """Restart a previously stopped job."""
    c = _auth_client()
    Job(c, uuid).restart()


@cli.group()
def predict():
    """Batch prediction."""
    pass


@predict.command("list")
def prediction_list():
    """List prediction jobs."""
    c = _auth_client()
    print_output([p.info for p in c.predictions])


@predict.command("submit")
@click.argument("trained_model")
@click.argument("dataset", required=False)
@click.option("--sample_ids", type=str, required=False)
@click.option("--sample_ids_file", type=click.File("r"), required=False)
def prediction_submit(trained_model, dataset, sample_ids=None, sample_ids_file=None):
    """Submit a prediction job for a given TRAINED MODEL and DATASET."""
    c = _auth_client()

    if sample_ids and sample_ids_file:
        raise click.BadParameter(
            "you cannot provide both sample_ids and sample_ids_file"
        )
    elif sample_ids_file:
        sample_ids = json.load(sample_ids_file)
    elif sample_ids:
        sample_ids = sample_ids.replace(" ", "").split(",")
    else:
        raise click.BadParameter(
            "please provide sample_ids or (strict) sample_ids_file"
        )

    print_output(Prediction.submit(c, trained_model, dataset, sample_ids))


@predict.command("stop")
@click.argument("uuid")
def prediction_stop(uuid):
    """Stop a prediction job."""
    c = _auth_client()
    Prediction(c, uuid).stop()


@predict.command("stop")
@click.argument("uuid")
def prediction_restart(uuid):
    """Stop a prediction job."""
    c = _auth_client()
    Prediction(c, uuid).restart()


@predict.command("delete")
@click.argument("uuid")
def prediction_delete(uuid):
    """Delete a prediction."""
    c = _auth_client()
    Prediction(c, uuid).delete()


@predict.command("get")
@click.argument("uuid")
def prediction_get(uuid):
    """Get info about the prediction"""
    c = _auth_client()
    print_output(Prediction(c, uuid).info)


@cli.group()
def eval():
    """Batch evaluation."""
    pass


@eval.command("submit")
@click.argument("model")
@click.argument("dataset")
def evaluation_submit(model, dataset):
    """Submit an evaluation job for a given MODEL and DATASET."""
    pass


@eval.command("stop")
@click.argument("uuid")
def evaluation_stop(uuid):
    """Stop an evaluation job."""
    pass


@eval.command("restart")
@click.argument("uuid")
def evaluation_restart(uuid):
    """Restart an evaluation job."""
    pass


@eval.command("delete")
@click.argument("uuid")
def evaluation_delete(uuid):
    """Delete an evaluation job."""
    pass


@eval.command("get")
@click.argument("uuid")
@click.argument("dst")
@click.argument("samples", nargs=-1)
def evaluation_get(uuid):
    """Get results of the evaluation and save them in the DST dir."""
    pass


@eval.command("get")
@click.argument("uuid")
@click.argument("dst")
@click.argument("samples", nargs=-1)
def evaluation_get_metrics(uuid):
    """Get summary metrics of the evaluation."""
    pass


@cli.group()
def session():
    """Interactive sessions management.
    NOTE: for full set of features use Python or JavaScript API"""
    pass


@session.command("list")
def session_list():
    """List of interactive sessions."""
    c = _auth_client()
    print_output([s.info for s in c.sessions])


# TODO: should we switch completely to clicke.option?
@session.command("start")
@click.argument("model")
@click.argument("dataset")
@click.argument("sample")
@click.argument("parametrizer_type")
def session_start(model, dataset, sample, parametrizer_type):
    """Start an interactive session with a given model and dataset sample."""
    c = _auth_client()
    print_output(Session.start(c, model, dataset, sample, parametrizer_type))


@session.command("delete")
@click.argument("uuid")
def session_delete(uuid):
    """Delete an existing session."""
    c = _auth_client()
    Session(c, uuid).delete()


def safe_cli():
    try:
        cli()
    except requests.HTTPError as http_error:
        try:
            message = http_error.response.json()["message"]
            click.echo(f"Error: {message}")
        except (ValueError, KeyError) as e:
            click.echo(http_error)
    except Exception as e:
        click.echo(e)


if __name__ == "__main__":
    cli()
