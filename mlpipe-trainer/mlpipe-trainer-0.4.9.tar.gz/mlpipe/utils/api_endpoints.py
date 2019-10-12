"""
File for all API endpoints
API Url is read from the config.ini file via the Config module
"""
from mlpipe.schemas.training import TrainingSchema
from mlpipe.utils import Config
import requests
import bson
import json


def test_connection():
    """
    Test API connection
    :return: http response
    """
    endpoint_url = Config.get_api_url() + "test"
    response = requests.get(endpoint_url)
    return response


def create_training(training: TrainingSchema):
    """
    Create an training with an TrainingSchema
    :param training: training data as TrainingSchema
    :return: http response
    """
    endpoint_url = Config.get_api_url() + "training"
    job_token = Config.get_job_token()
    headers = {
        'content-type': 'application/json',
        'jobtoken': job_token
    }
    data = json.dumps(training.get_dict())
    response = requests.post(endpoint_url, data=data, headers=headers)
    return response


def update_training(training_id: str, training: TrainingSchema):
    """
    Update an training with an TrainingSchema
    :param training_id: mongoDB Id of the training to update
    :param training: training data as TrainingSchema
    :return: http response
    """
    endpoint_url = Config.get_api_url() + "/training/" + training_id
    job_token = Config.get_job_token()
    headers = {
        'content-type': 'application/json',
        'jobtoken': job_token
    }
    data = json.dumps(training.get_dict())
    response = requests.put(endpoint_url, data=data, headers=headers)
    return response


def update_weights(training_id: str, epoch: int, batch: int, file_path: str):
    """
    Update weights of the training with a .h5 file
    :param training_id: mongoDB Id of the training to update
    :param epoch: epoch of the weights
    :param batch: batch of the weights
    :param file_path: path to the .h5 file
    :return: http response
    """
    with open(file_path, mode='rb') as file:
        file_bytes = file.read()

    data = bson.BSON.encode({
        "epoch": epoch,
        "batch": batch,
        "weights": file_bytes
    })
    endpoint_url = Config.get_api_url() + "training/" + training_id + "/weights"
    job_token = Config.get_job_token()
    headers = {
        'content-type': 'application/octet-stream',
        'jobtoken': job_token
    }
    response = requests.put(endpoint_url, headers=headers, data=data)
    return response
