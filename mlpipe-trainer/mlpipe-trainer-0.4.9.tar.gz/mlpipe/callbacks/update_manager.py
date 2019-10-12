from mlpipe.utils import Config
from mlpipe.callbacks.fill_training import FillTraining
from mlpipe.utils.api_endpoints import create_training, update_weights, update_training, test_connection
from tensorflow.keras.models import Model
import os


class UpdateManager(FillTraining):
    """
    Callback to update the MLPipe - Manager via its API
    """
    def __init__(
            self,
            name: str,
            keras_model: Model,
            epochs: int,
            batches_per_epoch: int,
            save_initial_weights: bool=True,
            update_frequency: int=1,
            epoch_save_condition=None):
        """
        :param name: name of the training as string
        :param keras_model: keras model that should be saved to the training
        :param epochs: integer of how many epochs the model is trained
        :param batches_per_epoch: integer on how many batches per epoch are trained
        :param save_initial_weights: boolean to determine if weights should be saved initially before training,
                                     default = True
        :param update_frequency: defines how often data is sent to the server. In case there are many many batches
                                 it is wise to increase this number. It still sends all info to the server, just
                                 not every single batch.
        :param epoch_save_condition: a function to test if the weights of the model should be saved after the epoch,
                                     the function takes an TrainingSchema as argument. It defaults to None which
                                     will save the weights after each epoch
        """
        super().__init__(name, keras_model, epochs, batches_per_epoch)
        self._epoch_save_condition = epoch_save_condition
        self._save_initial_weights = save_initial_weights
        self._update_frequency = update_frequency
        self._training_mongodb_id = None

    def _create_training(self):
        if Config.get_job_token() is None or Config.get_job_token() == "":
            print("Job Token is not set, therefore no data is transmitted, but the server connection is tested...")
            test_res = test_connection()
            if test_res.status_code == 200:
                print("Connection test: Success")
            else:
                raise ConnectionError("Connection test: Error, unable to connect!")
        else:
            json_resp = self._handle_response(create_training(self._training))
            if "_id" in json_resp:
                self._training_mongodb_id = json_resp["_id"]

    def on_train_begin(self, logs=None):
        super().on_train_begin(logs)
        self._create_training()
        if self._training_mongodb_id is not None and self._save_initial_weights:
            self._update_weights()

    def on_batch_end(self, batch, logs=None):
        super().on_batch_end(batch, logs)
        should_update = (batch % self._update_frequency) == 0
        if self._training_mongodb_id is not None and should_update:
            self._handle_response(update_training(self._training_mongodb_id, self._training))

    def on_epoch_end(self, epoch, logs=None):
        super().on_epoch_end(epoch, logs)
        if self._training_mongodb_id is not None:
            self._handle_response(update_training(self._training_mongodb_id, self._training))
            if self._epoch_save_condition is None or self._epoch_save_condition(self._training):
                self._update_weights()

    def on_train_end(self, logs=None):
        super().on_train_end(logs)
        if self._training_mongodb_id is not None:
            self._handle_response(update_training(self._training_mongodb_id, self._training))

    def _update_weights(self):
        """ save file and update weights, remove tmp h5 file afterwards """
        tmp_filename = "tmp_model_weights_save.h5"
        if self._training_mongodb_id is not None and self._training.result.model is not None:
            self._training.result.model.save(tmp_filename)
            self._handle_response(update_weights(
                self._training_mongodb_id,
                self._training.result.curr_epoch,
                self._training.result.curr_batch,
                tmp_filename
            ))
            os.remove(tmp_filename)

    @staticmethod
    def _handle_response(res):
        """
        Check for errors and return json response in case of 200 HTTP response code
        :param res: response from a HTTP request
        :return: dict of json response
        """
        if res.status_code != 200:
            if res.status_code == 404:
                raise ValueError("HTTP Response 404 (Not Found): " + res.text)
            if res.status_code == 403:
                raise ValueError("HTTP Response 403 (Forbidden): " + res.text)
            if res.status_code == 401:
                raise PermissionError("HTTP Response 401 (Not Authorized): " + res.text)
            if res.status_code == 400:
                raise ValueError("HTTP Response 400 (Validation Error): " + res.text)
            else:
                raise RuntimeError("Unkown HTTP Error: " + res.text)
        return res.json()
