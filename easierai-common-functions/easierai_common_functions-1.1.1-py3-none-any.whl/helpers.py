import os
import sys
import tempfile
import threading
import time as time_lib
import schedule
import base64
import common_functions.constants as constants
from common_functions.logger import Logger
import joblib
import datetime as dt
import configparser

import json

from sklearn.preprocessing import MinMaxScaler

import pydash as _


global config

global _logger

global minioClient

def assert_exit(condition, err_message):
    try:
        assert condition
    except AssertionError:
        sys.exit(err_message)


def list_with_values(length, value):
    l = []
    for i in range(length):
        l.append(value)

    return l

def random_file_name(prefix='', suffix='', dir=None):
    if (not dir):
        dir = os.getcwd()

    try:
        tf = tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, dir=dir)
        return tf.name
    except Exception as e:
        _logger.error('Cannot create filename ' + str(e))
        sys.exit(e)

def generate_file_name(dir=None):
    if (not dir):
        dir = os.getcwd()
    return dt.datetime.now().strftime(dir + '/' +'%Y%m%d%H%M%S')

def get_data_shape(data_type, num_features, num_samples, algorithm):
    if data_type == constants.TIMESERIES:
        shape = (num_samples, num_features)
    else:
        if algorithm == constants.LSTM or algorithm == constants.PHASED_LSTM:
            shape = (num_samples, num_features)
        else:
            shape = (num_features,)
    return shape

def importer(algorithm, inference_type=constants.ESTIMATOR, lr=0.001):
    # Keras lstm config
    if(inference_type == constants.ESTIMATOR):
        if(algorithm == constants.LSTM):
            from common_functions.models.estimation.keras_model_lstm import Predictor
            ft_range = (-1, 1)
            activation = constants.LINEAR
        elif(algorithm == constants.PHASED_LSTM):
            from common_functions.models.estimation.keras_model_phasedlstm import Predictor
            ft_range = (-1, 1)
            activation = constants.LINEAR
        elif(algorithm == constants.DENSE):
            from common_functions.models.estimation.keras_model_dense import Predictor
            ft_range = (0, 1)
            activation = constants.LINEAR
    elif(inference_type == constants.CLASSIFIER):
        if(algorithm == constants.LSTM):
            from common_functions.models.classification.keras_model_lstm import Predictor
            ft_range = (-1, 1)
            activation = constants.SOFTMAX
        elif(algorithm == constants.PHASED_LSTM):
            from common_functions.models.classification.keras_model_phasedlstm import Predictor
            ft_range = (-1, 1)
            activation = constants.SOFTMAX
        elif(algorithm == constants.DENSE):
            from common_functions.models.classification.keras_model_dense import Predictor
            ft_range = (0, 1)
            activation = constants.SOFTMAX
    else:
        _logger.error("Inference type not supported yet")
        return None
    # # -----------------------------------------------------------------------------------------------------------------

    # Imported ML class
    pred = Predictor(output_activation=activation, ft_range=ft_range, lr=lr)
    # # -----------------------------------------------------------------------------------------------------------------
    return pred

def load_model_file(eslib, id, inference_type=constants.ESTIMATOR):
        """
        Returns the document stored on Elasticsearch, which includes, among other things,
        the h5 and pkl files where we had saved the model and the scalers, respectively
        :param id: id of the entity
        :param inference_type: this param helps us to download the right model according to its features and parameters
        :return: dict with the format "extension": object
        """

        storage_folder = '../storage/'
        start_time = time_lib.clock()

        files_dict = {}
        ok, res = eslib.get_last_document_with_params(config['ELASTIC']['index_models'], id, compose_model_params_filter(inference_type==constants.CLASSIFIER))
        pred = importer(config['ML']['algorithm'], inference_type=inference_type)
        files_dict[constants.PREDICTOR] = pred
        if not ok:
            _logger.error('Error reading model from Elasticsearch - check elasticsearch logs')
            return files_dict
        if (not _.is_empty(res)):
            try:
                available_files = get_available_files_from_minio(config['ELASTIC']['index_models'], res['_source']['model_file_path'])
                for file in available_files:
                    # To get the extension, remove the stored filename and take from the dot forward
                    extension = file.replace(res['_source']['model_file_path'], "")[1:]
                    if extension == constants.JSON_EXTENSION:
                        continue
                    filename = retrieve_file_from_minio(config['ELASTIC']['index_models'], res['_source']['model_file_path'], storage_folder, extension)
                    if extension == constants.MODEL_EXTENSION:
                        pred.load_model(filename)
                        obj = pred.model
                    elif extension == constants.SCALER_EXTENSION or extension == constants.LABELENCODER_EXTENSION or extension == constants.ONEHOTENCODER_EXTENSION:
                        obj = joblib.load(filename)
                    else:
                        _logger.info('Found an unknown file extension ('+ extension + '). Continuing with the next one', {'bucket_name' :config['ELASTIC']['index_models'], 'file_path': res['_source']['model_file_path']})
                        continue
                    files_dict[extension] = obj
                
                elapsed_time = time_lib.clock() - start_time
                _logger.info('Model successfully loaded (' + id + ') - ' +
                                str(dt.datetime.fromtimestamp(res['_source']['timestamp'] / 1000.0).isoformat()) +
                                ' [' + str(elapsed_time) + ' secs]')
            except Exception as e:
                _logger.error('Error on loading model (' + id + ') - ' + str(e))
                return files_dict

        else:
            return files_dict
        return files_dict

def file_to_b64(filename, extension):
        with open(filename + '.' + extension, 'rb') as f:
            # Remove first character, to skip the b from binary types
            return str(base64.b64encode(f.read()))[1:]

def b64_to_file(data, extension):
    filename = "../storage/tmpfile." + extension
    bytes_file = base64.b64decode(data)
    with open(filename, 'wb') as f:
        f.write(bytes_file)
    return filename

def read_config_file(config_path):
    config = configparser.ConfigParser()
    assert_exit(os.path.isfile(config_path), 'Error reading the configuration file ' + config_path)
    config.read(config_path)
    return config

def check_initial_config(eslib, is_classifier):
    """
    This functions is in charge of checking if there is any model on the elastic database with the current configuration.
    """
    res = eslib.check_model_params(config['ELASTIC']['index_models'], compose_model_params_filter(is_classifier))
    if res:
        if(int(res['hits']['total']['value']) < 1):
            _logger.error('No model on the database matches the current model configuration. Please check this issue or wait for a training session')
        else:
            _logger.info('Found models with the current configuration stored in the database for the following entities: ')
            _logger.info(remove_duplicates_from_list(_.map_(res['hits']['hits'], lambda x: x['_source']['id'])))

def remove_duplicates_from_list(list_with_duplicates):
    # Transforming into a dictionary and then back to a list removes repeated items
    return list(dict.fromkeys(list_with_duplicates))

def scale_dataset(scaler, data, i, ft_range=(-1, 1), training=True):
    """
    Scale data (in np.array or list format) using MinMaxScaler and the ft_range given (default is (-1,1)
    :param data: array of data to be scaled
    :param i: feature corresponding to the scaler
    :param ft_range: tuple containing minimum and maximum values of the data already scaled
    :return: tuple of scaler and data scaled
    """
    if scaler is None:
        scaler = MinMaxScaler(feature_range=ft_range)

    if training:
        scaler = scaler.partial_fit(data)

    # transform
    data_scaled = scaler.transform(data)

    return scaler, data_scaled

def compose_model_params(is_classifier):
    model_params = {
            'data_type': config['INFERENCE']['data_type'],
            'num_previous_measures': config['INFERENCE']['num_previous_measures'],
            'time_index': config['DATA']['time_index'],
            'minio_address': config['MINIO']['minio_host'] + ':' + config['MINIO']['minio_port']
    }
    if is_classifier:
        model_params['features'] = config['DATA']['features']
        model_params['class_name'] = config['DATA']['class_name']
        model_params['num_classes'] = config['INFERENCE']['num_classes']
    else:
        model_params['inference_features'] = config['DATA']['inference_features']
        model_params['dataset_features'] = config['DATA']['dataset_features']
        model_params['num_forecasts'] = config['INFERENCE']['num_forecasts']

    return model_params

def compose_model_params_filter(is_classifier):
    filter = [
            {
                "match": {
                    "algorithm": config['ML']['algorithm']
                }
            },
            {
                "match": {
                    "model_params.data_type": config['INFERENCE']['data_type']
                }
            },
            {
                "match": {
                    "model_params.num_previous_measures": config['INFERENCE']['num_previous_measures'],
                }
            },
            {
                "match": {
                    "model_params.time_index": config['DATA']['time_index']
                }
            }
        ]
    if(is_classifier):
        filter.append({
                    "match": {
                        "model_params.features": config['DATA']['features']
                    }
                })
        filter.append({
                    "match": {
                        "model_params.class_name": config['DATA']['class_name']
                    }
                })
        filter.append({
                "match": {
                    "model_params.num_classes": config['INFERENCE']['num_classes']
                }
            })
    else:
        filter.append({
                    "match": {
                        "model_params.inference_features": config['DATA']['inference_features']
                    }
                })
        filter.append({
                    "match": {
                        "model_params.dataset_features": config['DATA']['dataset_features']
                    }
                })
        filter.append({
                "match": {
                    "model_params.num_forecasts": config['INFERENCE']['num_forecasts']
                }
            })
    return filter
    
def save_model(eslib, id, metadata, dict={}, inference_type=constants.ESTIMATOR):
    '''
    :dict: expected params in object:
        model
        scaler
        labelencoder
        onehotencoder
    '''
    try:
        filename = generate_file_name(dir='../storage')
        for extension in dict:
            item = dict[extension]
            if extension == constants.SCALER_EXTENSION:
                joblib.dump(item, filename + '.' + constants.SCALER_EXTENSION)
            elif extension == constants.MODEL_EXTENSION: 
                item.save(filename + '.' + constants.MODEL_EXTENSION)
            elif extension in [constants.ONEHOTENCODER_EXTENSION, extension == constants.LABELENCODER_EXTENSION]:
                joblib.dump(item, filename + '.' + extension)
            else:
                _logger.error('Passed an invalid extension in the dictionary ( ' + extension + '). Continuing with the next one.')
                continue
            uploaded = upload_file_to_minio(config['ELASTIC']['index_models'], filename, extension, id, config['ML']['algorithm'])
            if not uploaded:
                _logger.error('Error on uploading file to min.io filesystem(' + filename + '.' + extension + ') - ')
                return ''

    except Exception as e:
        _logger.error('Error on saving scaler & model files (' + filename + ') - ' + str(e))
        # if the files could not be saved, they cannot be indexed in elasticsearch
        return ''

    doc = {
        'timestamp': dt.datetime.now().timestamp() * 1000,
        'algorithm': config['ML']['algorithm'],
        'id': id,
        'metadata': metadata,
        'model_file_path': generate_file_path(filename, id, config['ML']['algorithm']),
        'model_params': compose_model_params(inference_type==constants.CLASSIFIER)
    }

    # Save to elastic
    ok = eslib.add_to_index(config['ELASTIC']['index_models'], doc)

    with open(filename + '.' + constants.JSON_EXTENSION, 'w') as f:
        json.dump(doc, f)
        f.close()
        uploaded = upload_file_to_minio(config['ELASTIC']['index_models'], filename, constants.JSON_EXTENSION, id, config['ML']['algorithm'])
        if not uploaded:
            _logger.error('Error on uploading metadata file to min.io filesystem(' + filename + '.' + constants.JSON_EXTENSION + ') - ')
    if not ok:
        _logger.error('Error on saving scaler & model in elasticsearch - check elasticsearch logs', doc)
    return filename

def generate_file_path(filename, id, algorithm):
    return str(id) + '/' + algorithm + '/' + filename.split('/')[-1]

def upload_file_to_minio(index, filename, extension, id, algorithm):
    try:
        if not minioClient.bucket_exists(index):
            minioClient.make_bucket(index)
            _logger.debug("Creating bucket " + index)
        minioClient.fput_object(index, generate_file_path(filename, id, algorithm) + '.' + extension, filename + '.' + extension)
    except Exception as ex:
        _logger.error(str(ex))
        return False
    return True

def retrieve_file_from_minio(index, file_path, storage_folder, extension):
    if(os.path.exists(storage_folder + file_path.split('/')[-1] + '.' + extension)):
        return storage_folder + file_path.split('/')[-1] + '.' + extension
    try:
        _logger.info('Downloading latest model files', storage_folder + file_path.split('/')[-1] + '.' + extension)
        if not minioClient.bucket_exists(index):
            _logger.error('Bucket does not exist, please train before')
            return ''
        minioClient.fget_object(index, file_path + '.' + extension, storage_folder + file_path.split('/')[-1] + '.' + extension)
        return storage_folder + file_path.split('/')[-1] + '.' + extension
    except Exception as ex:
        _logger.error(str(ex))
        return ''

def get_available_files_from_minio(index, file_path):
    iterator = minioClient.list_objects(index, recursive = True, prefix=file_path)
    filename_list = []
    for filename in iterator:
        filename_list.append(filename.object_name)
    return filename_list

# From schedule in FORK https://github.com/mrhwick/schedule
cease_continuous_run = threading.Event()

class ScheduleThread(threading.Thread):
    @classmethod
    def run(cls):
        while not cease_continuous_run.is_set():
            schedule.run_pending()
            time_lib.sleep(1)
