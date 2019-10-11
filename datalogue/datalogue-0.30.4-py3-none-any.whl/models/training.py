from abc import ABC, abstractmethod
from typing import Dict, List, Set, Optional, Union
from datalogue.models.ontology import OntologyNode
from datalogue.models.organization import User
from uuid import UUID
import itertools
import pandas as pd
import datetime
from collections import namedtuple
from datalogue.errors import _enum_parse_error, DtlError
from datalogue.utils import _parse_list, _parse_string_list, SerializableStringEnum


class ModelType(SerializableStringEnum):
    cbc = "cbc"
    cfc = "cfc"
    ner = "ner"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("model type", s))


def model_type_from_str(string: str) -> Union[DtlError, ModelType]:
    return SerializableStringEnum.from_str(ModelType)(string)


class TrainingStatusType(SerializableStringEnum):
    success = "success"
    failure = "failure"
    in_progress = "in-progress"
    requested = "requested"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("training status type", s))


def training_status_type_from_str(string: str) -> Union[DtlError, TrainingStatusType]:
    return SerializableStringEnum.from_str(TrainingStatusType)(string)


class OrderList(SerializableStringEnum):
    asc = "asc"
    desc = "desc"

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("order list", s))


def order_list_from_str(string: str) -> Union[DtlError, OrderList]:
    return SerializableStringEnum.from_str(OrderList)(string)


class DataRef:
    def __init__(self, node: OntologyNode, path_list: List[List[str]]):
        self.node = node
        self.path_list = path_list


class TrainingEndReason:
    def __init__(self, reasonType: str):
        self.reason_type = reasonType

    def __eq__(self, other: 'TrainingEndReason'):
        if isinstance(self, other.__class__):
            return self.reason_type == other.reason_type
        return False
    
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["_type"] = self.reason_type
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'TrainingEndReason']:
            """
            Builds a TRainingEndReason object from a dictionary,

            :param json: dictionary parsed from json
            :return:
            """
            reasonType = json.get("_type")
            if not isinstance(reasonType, str):
                return DtlError("An '_type' field is missing")
            
            return TrainingEndReason(reasonType)

class ConfusionMatrix:
    def __init__(self, index: List[str], matrix: List[List[int]]):
        self.index = index
        self.matrix = matrix
    
    def __eq__(self, other: 'ConfusionMatrix'):
        if isinstance(self, other.__class__):
            return self.index == other.index and self.matrix == other.matrix
        return False
    
    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["index"] = self.index
        base["matrix"] = self.matrix
        return base
    
    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ConfusionMatrix']:
        """
        Builds a confusion Matrix object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """
        index = json.get("index")
        if not isinstance(index, List):
            return DtlError("An 'index' field is missing")

        matrix = json.get("matrix")
        if not isinstance(matrix, List):
            return DtlError("An 'matrix' field is missing")

        return ConfusionMatrix(index, matrix)

class MetricsDetails:
    def __init__(self, timestamp: str, metrics_type: str, epoch: int, loss: float, accuracy: float, precision: Dict[str, float], recall: Dict[str, float], f1_score: Dict[str, float], tpr: Optional[float] = None, fpr: Optional[float] = None,  conf_matrix: Optional[ConfusionMatrix] = None):
        self.tpr = tpr
        self.fpr = fpr
        self.timestamp = timestamp
        self.metrics_type = metrics_type
        self.epoch = epoch
        self.loss = loss
        self.accuracy = accuracy
        self.precision = precision
        self.recall = recall
        self.f1_score = f1_score
        self.conf_matrix = conf_matrix
    
    def __eq__(self, other: 'MetricsDetails'):
        if isinstance(self, other.__class__):
            return self.tpr == other.tpr and self.fpr == other.fpr and self.timestamp == other.timestamp and self.metrics_type == other.metrics_type and self.epoch == other.epoch and self.loss == other.loss and self.accuracy == other.accuracy and self.precision == other.precision and self.recall == other.recall and self.f1_score == other.f1_score and self.conf_matrix == other.conf_matrix
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["tpr"] = self.tpr
        base["fpr"] = self.fpr
        base["timestamp"] = self.timestamp
        base["metricsType"] = self.metrics_type
        base["epoch"] = self.epoch
        base["loss"] = self.loss
        base["accuracy"] = self.accuracy
        base["precision"] = self.precision._as_payload()
        base["recall"] = self.recall._as_payload()
        base["f1Score"] = self.f1_score._as_payload()

        if self.conf_matrix is not None:
            base["confusionMatrix"] = self.conf_matrix._as_payload()
        else:
            base["confusionMatrix"] = None
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'MetricsDetails']:
        """
        Builds a MetricsDetails object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """

        tpr = json.get("tpr")
        if not isinstance(tpr, float):
            tpr = None
        
        fpr = json.get("fpr")
        if not isinstance(fpr, float):
            fpr = None

        timestamp = json.get("timestamp")
        if not isinstance(timestamp, str):
            return DtlError("A 'timestamp' field is missing")
        
        metrics_type = json.get("type")
        if not isinstance(metrics_type, str):
            return DtlError("A 'type' field is missing")
        
        epoch = json.get("epoch")
        if not isinstance(epoch, int):
            epoch = None
        
        loss = json.get("loss")
        if not isinstance(loss, float):
            return DtlError("A 'loss' field is missing")

        accuracy = json.get("accuracy")
        if not isinstance(accuracy, float):
            return DtlError("An 'accuracy' field is missing")
        
        precision = json.get("precision")        
        if precision is None:
            return DtlError("'Precision' field is missing")
        elif not isinstance(precision, dict):
            return DtlError("'Precision' contains wrong data type it should be dictionary")
        
        recall = json.get("recall")
        if recall is None:
            return DtlError("'Recall' field is missing")
        elif not isinstance(recall, dict):
            return DtlError("'Recall' contains wrong data type it should be dict")
        
        f1_score = json.get("f1Score")
        if f1_score is None:
            return DtlError("'F1Score' field is missing")
        elif not isinstance(f1_score, dict):
            return DtlError("'F1Score' contains wrong data type it should be dict")
        
        conf_matrix = json.get("confusionMatrix")
        if conf_matrix is not None:
            conf_matrix = ConfusionMatrix._from_payload(conf_matrix)
            if isinstance(conf_matrix, DtlError):
                return conf_matrix
            
        
        return MetricsDetails(timestamp, metrics_type, epoch, loss, accuracy, precision, recall, f1_score, tpr, fpr, conf_matrix)

class Epoch:
    def __init__(self, epoch_number: int, metrics: List[MetricsDetails]):
        self.epoch_number = epoch_number
        self.metrics = metrics

    def __eq__(self, other: 'Epoch'):
        if isinstance(self, other.__class__):
            return self.epoch_number == other.epoch_number and self.metrics == other.metrics
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["epochNo"] = self.epoch_number
        base["metrics"] = list(map(lambda m: m._as_payload(), self.metrics))
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Epoch']:
        """
        Builds an Epoch object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """

        epoch_number = json.get("epochNo")
        if not isinstance(epoch_number, int):
            return DtlError("An 'epochNo' field is missing")

        metrics = json.get("metrics")
        if metrics is not None:
            metrics = _parse_list(MetricsDetails._from_payload)(metrics)
            if isinstance(metrics, DtlError):
                return metrics
        else:
            metrics = list()

        return Epoch(epoch_number, metrics)

class TrainingState:
    def __init__(self, id: UUID, ontology_id: UUID, startTime: str, endTime: str, status: str, userId: UUID, details: str, numberOfEpochs: int, modelType: str, epochs: List[Epoch], test_metrics: Optional[MetricsDetails] = None, endReason: Optional[TrainingEndReason] = None, requestedBy: Optional[User] = None):
        self.start_time = startTime
        self.end_time = endTime
        self.end_reason = endReason
        self.status = status
        self.requested_by = requestedBy
        self.user_id = userId
        self.details = details
        self.number_of_epochs = numberOfEpochs
        self.model_type = modelType
        self.epochs = epochs
        self.test_metrics = test_metrics
        self.ontology_id = ontology_id
        self.id = id

    def __eq__(self, other: 'TrainingState'):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.ontology_id == other.ontology_id and self.start_time == other.start_time and self.end_reason == other.end_reason and self.end_time == other.end_time and self.status == other.status and self.requested_by == other.requested_by and self.user_id == other.user_id and self.details == other.details and self.number_of_epochs == other.number_of_epochs and self.model_type == other.model_type and self.epochs == other.epochs and self.test_metrics == other.test_metrics
        return False

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["startTime"] = self.start_time
        base["endTime"] = self.end_time
        base["endReason"] = self.end_reason
        base["requestedBy"] = self.requested_by
        base["userId"] = self.user_id
        base["numberOfEpochs"] = self.number_of_epochs
        base["epochs"] = list(map(lambda e: e._as_payload(), self.epochs))
        base["modelType"] = self.model_type
        base["testMetrics"] = self.test_metrics
        base["ontology_id"] = self.ontology_id
        base["id"] = self.id
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'TrainingState']:
        """
        Builds a TrainingState object from a dictionary,

        :param json: dictionary parsed from json
        :return:
        """

        end_time = json.get("endTime")
        if not isinstance(end_time, str):
            end_time = None
     
        end_reason = json.get("endReason")
        if end_reason is not None:
            end_reason = TrainingEndReason._from_payload(end_reason)
            if isinstance(end_reason, DtlError):
                return end_reason
   
        epochs = json.get("epochs")
        if epochs is not None:
            epochs = _parse_list(Epoch._from_payload)(epochs)
            if isinstance(epochs, DtlError):
                return epochs
        else:
            epochs = list()

        model_type = json.get("modelType")
        if not isinstance(model_type, str):
            return DtlError("A 'modelType' field is missing")
        
        number_of_epochs = json.get("numberOfEpochs")
        if not isinstance(number_of_epochs, int):
            return DtlError("A 'numberOfEpochs' field is missing")
        
        ontology_id = json.get("ontologyId")
        if not isinstance(ontology_id, str):
            return DtlError("A 'ontologyId' field is missing")
        
        training_id = json.get("id")
        if not isinstance(training_id, str):
            return DtlError("An 'id' field is missing")
        
        start_time = json.get("startTime")
        if not isinstance(start_time, str):
            return DtlError("A 'startTime' field is missing")

        status = json.get("status")
        if not isinstance(status, str):
            return DtlError("A 'status' field is missing")

        test_metrics = json.get("testMetrics")
        if test_metrics is not None:
            test_metrics = MetricsDetails._from_payload(test_metrics)
            if isinstance(test_metrics, DtlError):
                return test_metrics
        else:
            test_metrics = None
        
        user_id = json.get("userId")
        if not isinstance(user_id, str):
            return DtlError("A 'userId' field is missing")
        
        details = json.get("details")
        if details is not None: 
            if not isinstance(details, str):
                return DtlError("A 'details' field is missing")

        return TrainingState(UUID(training_id), UUID(ontology_id), start_time, end_time, status, UUID(user_id), details, number_of_epochs, model_type, epochs, test_metrics, end_reason, None)

    def pd_dataframe_metrics(self):
        """
        Get the tuple object that contains the data frames with the metrics of the specific training.

        :return: Once the tuple is build with `metrics = TrainingState.pd_dataframe_metrics()` the object `metrics` can be accessed:
            - `metrics.description`: data frame with the general information of the training
            - `metrics.validation.metrics[<epoch_number>]`: data frame with precision, recall and f1 for all the classes for that epoch in the validation dataset
            - `metrics.validation.cm[<epoch_number>]`: data frame with confusion matrix for all the classes for that epoch in the validation dataset
            - `metrics.test.metrics`: data frame with precision, recall and f1 for all the classes for that epoch in the test dataset
            - `metrics.test.cm`: data frame with confusion matrix for all the classes for that epoch in the test dataset
            - `metrics.general`: data frame with the general metrics (loss, accuracy, tpr, fpr) for each validation epoch and test set.
        """
        return self._from_training_payload(self)

    @staticmethod
    def _get_description_of_training(training_state: 'TrainingState') -> pd.DataFrame:
        """Gets data frame with the description of training.

        :param: training_state: training state object
        :return: data frame with the description of the training (id, ontology id, model type, status, user id, number of epochs,
        start time, end time, end reason and details)
        """
        descrip = {}
        descrip['training_id'] = training_state.id
        descrip['ontology_id'] = training_state.ontology_id
        descrip['model_type'] = training_state.model_type
        descrip['status'] = training_state.status
        descrip['user_id'] = training_state.user_id
        descrip['number_of_epochs'] = training_state.number_of_epochs
        descrip['start_time'] = training_state.start_time
        descrip['end_time'] = training_state.end_time
        descrip['end_reason'] = training_state.end_reason.reason_type if training_state.end_reason is not None else None
        descrip['details'] = training_state.details
        df = pd.DataFrame.from_dict(descrip, orient='index')
        # description columns in the df
        df.columns = ['Description']

        return df

    @staticmethod
    def _create_validation_confusion_matrices_and_metrics(json_epochs: Epoch) -> tuple:
        """
        Create a tuple with the data frames with the confusion matrices and metrics from the validation set for each epoch.
        Note that the metrics are obtained from the confusion matrix and not the actual training state object.
        :param json_epochs: epochs from training state object (`training_state.epochs`)
        :return:
            1 - tuple with data frames for metrics (3 data frames with precision, recall and f1 for each epoch)
            2 - tuple with data frames for confusion matrices for each epoch
        """
        validation_metrics = {}
        recall_df = pd.DataFrame()
        precision_df = pd.DataFrame()
        f1_df = pd.DataFrame()
        dfs_epochs_cm = dict()
        for epoch_data in json_epochs:
            for epoch_data_metric in epoch_data.metrics:
                if epoch_data_metric.metrics_type == "validation":
                    cm = epoch_data_metric.conf_matrix
                    df = pd.DataFrame(cm.matrix, columns=cm.index,
                                      index=cm.index)
                    epoch = 'epoch_' + str(epoch_data_metric.epoch)
                    recall = TrainingState._create_recall_df_from_cm_as_df(df, epoch)
                    recall_df = pd.concat([recall_df, recall])
                    precision = TrainingState._create_precision_df_from_cm_as_df(df, epoch)
                    precision_df = pd.concat([precision_df, precision])
                    f1 = TrainingState._create_f1_df_from_recall_precision_as_dfs(precision_df, recall_df, epoch)
                    f1_df = pd.concat([f1_df, f1])
                    df.reset_index(level=0, inplace=True)
                    dfs_epochs_cm[epoch] = df
        validation_metrics['precision'] = precision_df
        validation_metrics['recall'] = recall_df
        validation_metrics['f1'] = f1_df
        for metric in validation_metrics.keys():
            validation_metrics[metric].reset_index(level=0, inplace=True)
        validation_metrics_tuple = TrainingState._from_dict_to_tuple(validation_metrics, 'validation_metrics')
        dfs_epochs_cm_tuple = TrainingState._from_dict_to_tuple(dfs_epochs_cm, 'confusion_matrix')
        return validation_metrics_tuple, dfs_epochs_cm_tuple

    @staticmethod
    def _create_recall_df_from_cm_as_df(df: pd.DataFrame, indexer: str) -> pd.DataFrame:
        """
        Build the data frame for the recall metrics. The recall is calculated from the confusion matrix.
        :param df: confusion matrix as data frame:
        :param indexer: row description (epochs for validation set and test for test set)
        :return: data frame with recall metrics
        """
        cols = df.columns
        res_df = pd.DataFrame(columns=cols)
        for class_name in cols:
            if df.loc[class_name, :].sum() > 0:
                res_df.loc[indexer, class_name] = df.loc[class_name, class_name] / df.loc[class_name, :].sum()
            else:
                res_df.loc[indexer, class_name] = 0
        return res_df

    @staticmethod
    def _create_precision_df_from_cm_as_df(df: pd.DataFrame, indexer: str) -> pd.DataFrame:
        """
        Build the data frame for the precision metrics. The precision is calculated from the confusion matrix.
        :param df: confusion matrix as data frame:
        :param indexer: row description (epochs for validation set and test for test set)
        :return: data frame with precision metrics
        """
        cols = df.columns
        res_df = pd.DataFrame(columns=cols)
        for class_name in cols:
            if df.loc[:, class_name].sum() > 0:
                res_df.loc[indexer, class_name] = df.loc[class_name, class_name] / df.loc[:, class_name].sum()
            else:
                res_df.loc[indexer, class_name] = 0
        return res_df

    @staticmethod
    def _create_f1_df_from_recall_precision_as_dfs(precision: pd.DataFrame, recall: pd.DataFrame, indexer: str) -> Union[pd.DataFrame, DtlError]:
        """
        Build the data frame for the f1 metrics. The f1 is calculated from the precision and recall df.
        :param precision: precision as data frame from confusion matrix:
        :param recall: recall as data frame from confusion matrix:
        :param indexer: row description (epochs for validation set and test for test set)
        :return: data frame with f1 metrics
        """
        if pd.Series(precision.columns).equals(pd.Series(recall.columns)):
            f1_df = pd.DataFrame(columns=precision.columns)
            for col in precision.columns:
                prec = precision.loc[indexer, col]
                rec = recall.loc[indexer, col]
                if prec + rec > 0:
                    f1_df.loc[indexer, col] = 2 * (prec * rec) / (prec + rec)
                else:
                    f1_df.loc[indexer, col] = 0
        else:
            return DtlError("The columns of the Precision - Recall Data Frames doesn't match")
        return f1_df

    @staticmethod
    def _create_test_cm_and_metrics(json_test: MetricsDetails) -> tuple:
        """
        Build data frames with confusion matrix and metrics for the test set.
        :param json_test: json test metrics from training state object (`training_state.test_metrics`)
        :return:
            1 - data frame with confusion matrix
            2 - data frame with test metrics
        """
        cm = json_test.conf_matrix
        df = pd.DataFrame(cm.matrix, columns=cm.index,
                          index=cm.index)
        recall = TrainingState._create_recall_df_from_cm_as_df(df, 'temp_index')
        precision = TrainingState._create_precision_df_from_cm_as_df(df, 'temp_index')
        f1_df = TrainingState._create_f1_df_from_recall_precision_as_dfs(precision, recall, 'temp_index')

        # rename indices
        recall.index = ['recall_test_set']
        precision.index = ['precision_test_set']
        f1_df.index = ['f1_test_set']

        df.reset_index(level=0, inplace=True)

        test_metrics = pd.concat([recall, precision, f1_df])
        test_metrics.reset_index(level=0, inplace=True)
        return df, test_metrics

    @staticmethod
    def _extract_general_metrics(json_file: MetricsDetails) -> pd.DataFrame:
        """Extract the general metrics from validation and test, in a row df.
        :param: json_file: Metrics details. For validation `training_state.epochs[<epoch_num>].metrics[1]` and
        for test set `training_state.test_metrics`
        :return: data frame with the metrics for that validation epoch/test set
        """
        columns = ['loss', 'accuracy', 'tpr', 'fpr', 'timestamp']
        # define the index
        if json_file.metrics_type == 'validation':
            ind = '_'.join([json_file.metrics_type, 'epoch', str(json_file.epoch)])
        elif json_file.metrics_type == 'test':
            ind = json_file.metrics_type
        else:
            print('Metrics not in validation or testing...')

        df = pd.DataFrame(index=[ind], columns=columns)
        # build the df with the columns and one index to later concatenate
        for col in columns:
            df.loc[ind, col] = getattr(json_file, col)
        return df

    @staticmethod
    def _build_gen_metrics(training_state: 'TrainingState') -> pd.DataFrame:
        """Creates the df with all the gen metrics.
        :param: training_state: training_state object
        :return: df with all the general metrics
        """
        list_dfs = []

        for i in range(len(training_state.epochs)):
            temp_df = TrainingState._extract_general_metrics(training_state.epochs[i].metrics[1])
            list_dfs.append(temp_df)

        if training_state.test_metrics:
            temp_df = TrainingState._extract_general_metrics(training_state.test_metrics)
            list_dfs.append(temp_df)

        if len(list_dfs) > 0:
            df = pd.concat(list_dfs)
            df.reset_index(level=0, inplace=True)

        return df

    @staticmethod
    def _build_list_with_gral_metrics(res_object, metric):
        """
        Builds the precision, recall and f1 general metrics to be added to 'general'
        :param: res_object: dictionary object obtained in previous calculations
        :return: res_object: with metrics added as columns in res_object['general']
        """
        list_metrics = getattr(res_object['validation']['metrics'], metric).iloc[:, 1:].mean(axis=1).tolist()
        list_metrics.append(float(res_object['test']['metrics'].loc[
                                res_object['test']['metrics']['index'] == metric + '_test_set'
                            ].iloc[:, 1:].mean(axis=1)))
        return list_metrics


    @staticmethod
    def _from_dict_to_tuple(dic, name):
        """Build a tuple from a dictionary"""
        return namedtuple(name, dic.keys())(*dic.values())

    @staticmethod
    def _from_training_payload(training_state: 'TrainingState') -> tuple:
        """
        Build a tuple with all the metrics in data frames
        :param training_state: training state object
        :return: a tuple containing:
            - `description`: data frame with the general information of the training
            - `validation.metrics[<epoch_number>]`: data frame with precision, recall and f1 for all the classes for that epoch in the validation dataset
            - `validation.cm[<epoch_number>]`: data frame with confusion matrix for all the classes for that epoch in the validation dataset
            - `test.metrics`: data frame with precision, recall and f1 for all the classes for that epoch in the test dataset
            - `test.cm`: data frame with confusion matrix for all the classes for that epoch in the test dataset
            - `general`: data frame with the general metrics (loss, accuracy, tpr, fpr) for each validation epoch and test set.
        """
        res_object = dict()

        res_object['description'] = TrainingState._get_description_of_training(training_state)
        if res_object['description'].loc['end_reason', 'Description'] == 'Successful':
            res_object['validation'] = dict()
            res_object['test'] = dict()
            res_object['validation']['metrics'], res_object['validation'][
                'cm'] = TrainingState._create_validation_confusion_matrices_and_metrics(training_state.epochs)
            res_object['test']['cm'], res_object['test']['metrics'] = TrainingState._create_test_cm_and_metrics(
                training_state.test_metrics)
            res_object['general'] = TrainingState._build_gen_metrics(training_state)
            # add columns precision, recall and f1 to general metrics from previous df's
            for metric in ['precision', 'recall', 'f1']:
                res_object['general'][metric] = TrainingState._build_list_with_gral_metrics(res_object, metric)

            # build tuples
            res_object['validation'] = TrainingState._from_dict_to_tuple(res_object['validation'], 'validation')
            res_object['test'] = TrainingState._from_dict_to_tuple(res_object['test'], 'test')
        else:
            if training_state.status == 'Ended' and res_object['description'].loc['end_reason', 'Description'] != 'Successful':
                message_not_success = f"The current training has ended not being successful. Reason: {res_object['description'].loc['end_reason', 'Description']}"
            else:
                message_not_success = f"At {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}, the current training has not ended. The status is : {training_state.status}"
            res_object['validation'] = message_not_success
            res_object['general'] = message_not_success
            res_object['test'] = message_not_success
        res_object = TrainingState._from_dict_to_tuple(res_object, 'all_metrics')
        return res_object


class Training:
    def __init__(self, id: UUID, states: List[TrainingState]):
        self.id = id
        self.states = states

    def _as_payload(self) -> dict:
        """
        Dictionary representation of the object
        :return:
        """
        base = dict()
        base["id"] = self.id
        base["states"] = list(map(lambda s: s._as_payload(), self.states))
        return base
    
    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "Training"]:
        id = payload.get("trainingId")
        states = payload.get("states")

        if states is not None:
            states = _parse_list(TrainingState._from_payload)(states)
            if isinstance(states, DtlError):
                return states
        else:
            states = list()
        return Training(id=id, states=states)
