# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Parse, reorganize and present data drift calculation results."""

import glob
import os
import shutil
import tempfile
import warnings
from datetime import datetime, timedelta
from collections import OrderedDict

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from azureml.data import _dataset_diff as dsd
from azureml.datadrift._logging._telemetry_logger import _TelemetryLogger
from azureml.datadrift._utils.constants import (
    DATADRIFT_TYPE_DATASET, DATADRIFT_TYPE_MODEL, RUN_TYPE_KEY, RUN_TYPE_ADHOC,
    HAS_DRIFT, COLUMN_NAME, DATETIME, DEBUG_DATASHIFT_MCC_ALL,
    DEBUG_DATASHIFT_MCC_TEST, DEBUG_DATASHIFT_MCC_TRAIN, DRIFT_THRESHOLD,
    FIGURE_FEATURE_IMPORTANCE_TITLE, FIGURE_FEATURE_IMPORTANCE_Y_LABEL,
    METRIC_COLUMN_METRICS, METRIC_DATASET_METRICS,
    METRIC_DATASHIFT_FEATURE_IMPORTANCE, METRIC_DATASHIFT_MCC_ALL,
    METRIC_DATASHIFT_MCC_TEST, METRIC_DATASHIFT_MCC_TRAIN,
    METRIC_SCHEMA_VERSION_DFT, METRIC_SCHEMA_VERSION_KEY,
    METRIC_STATISTICAL_DISTANCE_ENERGY, METRIC_STATISTICAL_DISTANCE_WASSERSTEIN,
    METRIC_TYPE, METRIC_TYPE_COLUMN, METRIC_TYPE_DATASET, MODEL_NAME, MODEL_VERSION,
    OUTPUT_METRIC_DRIFT_COEFFICIENT, OUTPUT_METRIC_DRIFT_CONTRIBUTION,
    PIPELINE_START_TIME, RUN_ID, SCORING_DATE, SERVICE, SERVICE_NAME, DUMMY_SERVICE,
    TGT_DST_START_DATE, TGT_DST_END_DATE,
    KEY_NAME_Drift_TYPE, KEY_NAME_SERVICE, KEY_NAME_BASE_DATASET_ID, KEY_NAME_TARGET_DATASET_ID)

from azureml.datadrift._utils.parameter_validator import ParameterValidator

module_logger = _TelemetryLogger.get_telemetry_logger(__name__)


def all_outputs(logger, data_store, workspaceid, services, drift_type,
                datadrift_id, baseline_dataset_id, target_dataset_id, model_name, model_version,
                start_time, end_time, run_id=None, daily_latest_only=True):
    """Get a tuple of the drift results and metrics in a given time window.

        .. remarks::
            Given there are three run types, adhoc run, scheduled run and backfill run. This attribute will be used
            to retrieve corresponding results in different ways:

            * To retrieve adhoc run results, there is only one way: run_id should be a valid guid run id.
            * To retrieve scheduled runs and backfill runs' results, there are two different ways: assign a valid guid
                run id to run_id, or assign specific start_time and/or end_time while keeping run_id as None;
            * If run_id and start_time/end_time are not None in the same invoking, parameter validation exception
                will be thrown.

            The get_output attribute can be used to retrieve all outputs or partial outputs of scheduled runs in a
            specific time range between 'start_tzime' and 'end_time' (boundary included). User can also limited to
            results of an individual adhoc 'run_id'.

            * Principle for filtering is "overlapping": as long as there is an overlap between the actual result time
                (scoring date for model based drift, target dataset's [start date, end date] for dataset based drift)
                and the given [start_time, end_time], that result will be picked up.

            * Given there are multiple types of data drift instance, the result contents could be various.
                For example, for model based results, it will look like:

        .. code-block:: python

            # results : [{'drift_type': 'ModelBased' or 'DatasetBased', 'service_name': 'service1',
            #             'result':[{'has_drift': True, 'datetime': '2019-04-03', 'drift_threshold': 0.3,
            #                        'model_name': 'modelName', 'model_version': 2}]}]
            # metrics : [{'drift_type': 'ModelBased' or 'DatasetBased', 'service_name': 'service1',
            #             'metrics': [{'schema_version': '0.1', 'datetime': '2019-04-03',
            #                          'model_name': 'modelName', 'model_version': 2,
            #                          'dataset_metrics': [{'name': 'datadrift_coefficient', 'value': 0.3453}],
            #                          'column_metrics': [{'feature1': [{'name': 'datadrift_contribution',
            #                                                            'value': 288.0},
            #                                                           {'name': 'wasserstein_distance',
            #                                                            'value': 4.858040000000001},
            #                                                           {'name': 'energy_distance',
            #                                                            'value': 2.7204799576545313}]}]}]}]

            While for dataset based results, it will look like:

        .. code-block:: python

            # results : [{'drift_type': 'ModelBased' or 'DatasetBased',
            #             'result':[{'has_drift': True, 'drift_threshold': 0.3,
            #                        'start_date': '2019-04-03', 'end_date': '2019-04-04',
            #                        'base_dataset_id': '4ac144ef-c86d-4c81-b7e5-ea6bbcd2dc7d',
            #                        'target_dataset_id': '13445141-aaaa-bbbb-cccc-ea23542bcaf9'}]}]
            # metrics : [{'drift_type': 'ModelBased' or 'DatasetBased',
            #             'metrics': [{'schema_version': '0.1',
            #                          'start_date': '2019-04-03', 'end_date': '2019-04-04',
            #                          'baseline_dataset_id': '4ac144ef-c86d-4c81-b7e5-ea6bbcd2dc7d',
            #                          'target_dataset_id': '13445141-aaaa-bbbb-cccc-ea23542bcaf9'
            #                          'dataset_metrics': [{'name': 'datadrift_coefficient', 'value': 0.53459}],
            #                          'column_metrics': [{'feature1': [{'name': 'datadrift_contribution',
            #                                                            'value': 288.0},
            #                                                           {'name': 'wasserstein_distance',
            #                                                            'value': 4.858040000000001},
            #                                                           {'name': 'energy_distance',
            #                                                            'value': 2.7204799576545313}]}]}]}]

    :param logger:
    :param drift_type:
    :param baseline_dataset_id:
    :param target_dataset_id:
    :param model_name:
    :param model_version:
    :param start_time:
    :param end_time:
    :param run_id:
    :param daily_latest_only: flag of whether dedup to pick only latest results.
    :return:
    """
    metrics_got = _get_metrics(logger, data_store, workspaceid, drift_type, datadrift_id,
                               services, model_name, model_version, daily_latest_only)

    # Check if metrics exist
    if not metrics_got or len(metrics_got) == 0:
        error_msg = "Metrics do not exist for "
        if drift_type == DATADRIFT_TYPE_DATASET:
            error_msg += "base dataset: {} and target dataset: {}".format(baseline_dataset_id, target_dataset_id)
        elif drift_type == DATADRIFT_TYPE_MODEL:
            error_msg += "model: {} with version: {}".format(model_name, model_version)
        logger.error(error_msg)
        raise NameError(error_msg)
    else:
        logger.debug("Found {} records.".format(len(metrics_got)))

    # Filter based on input params
    if run_id:
        metrics_valid = [m for m in metrics_got if _properties(m.get_extended_properties())[RUN_ID] == run_id]

        logger.debug("Filtered in {} records for run id {}.".format(len(metrics_valid), run_id))
    # if run_id is None, pick only scheduled runs' results
    else:
        metrics_schedulerun = [m for m in metrics_got
                               if _properties(m.get_extended_properties())[RUN_TYPE_KEY] != RUN_TYPE_ADHOC]
        logger.debug("Filtered in {} records of schedule runs.".format(len(metrics_schedulerun), run_id))

        # Filter in given time range, only for schedule runs, if input run_id only, then no need to check time range.
        if drift_type == DATADRIFT_TYPE_DATASET:
            metrics_valid = [m for m in metrics_schedulerun
                             if (start_time <=
                                 _properties(m.get_extended_properties())[TGT_DST_START_DATE] <= end_time or
                                 start_time <=
                                 _properties(m.get_extended_properties())[TGT_DST_END_DATE] <= end_time)]
        elif drift_type == DATADRIFT_TYPE_MODEL:
            metrics_valid = [m for m in metrics_schedulerun
                             if start_time <= _properties(m.get_extended_properties())[SCORING_DATE] <= end_time]
        else:
            metrics_valid = metrics_schedulerun
        logger.debug("Filtered in {} records between [{}, {}].".format(len(metrics_valid), start_time, end_time))

    return _build_results(drift_type, metrics_valid), _build_metrics(drift_type, metrics_valid)


def _get_metrics(logger, data_store, workspaceid, drift_type, datadrift_id,
                 services, model_name, model_version, daily_latest_only=True):
    local_temp_root = os.path.join(tempfile.gettempdir(), workspaceid)
    os.makedirs(local_temp_root, exist_ok=True)

    # metrics will be a list of object DiffMetric, it has a member 'name' of the measurement and corresponding 'value',
    # as for detailed information such as date, model, service or base/target dataset, they are in extended properties.
    metrics = []

    # For dedup. Considering there could be mixed results from scheduled run and adhoc run on each date, should find
    # latest pipeline start time for each date and:
    #
    #   for model based drift, model name/version are always the same for a specific data drift detector but service
    #   could bedifferent, so it's per service per date. The date is the 'scoring_date' in extended properties.
    #
    #   for dataset based drift, there is actually no 'service' so it's just per date. The date is the 'start_date'
    #   in extended properties.
    #
    # Moreover, to make codes aligned, fake a service name for dataset based drift by using is drift id.
    # then both model based and dataset based drift latest pipeline times are all per service per date.
    latest_pipeline_times = {}

    if drift_type == DATADRIFT_TYPE_DATASET:
        _download_from_blob_metrics(logger, local_temp_root, metrics, latest_pipeline_times,
                                    data_store, drift_type, datadrift_id, model_name, model_version, service=None)
    # Only model based drift needs check all services.
    elif drift_type == DATADRIFT_TYPE_MODEL:
        all_services = services
        for s in all_services:
            _download_from_blob_metrics(logger, local_temp_root, metrics, latest_pipeline_times,
                                        data_store, drift_type, datadrift_id, model_name, model_version, s)

    # dedup data based on pipeline start time.
    # NOTICE:
    #  It's possible there will be multiple results in same target date folder, thus dedup is needed.
    #  (target date marked by 'scoring_date' for model based drift and 'start_date' for dataset based drift)
    #
    #  The principle of dedup is to pick the latest results. The latest one can be tell from latest pipeline start time
    #  on scoring date (model based drift) or target dataset start_date (dataset based drift).
    if daily_latest_only is True:
        metrics = [m for m in metrics
                   if m.extended_properties[PIPELINE_START_TIME] == latest_pipeline_times
                   [m.extended_properties[KEY_NAME_SERVICE] if drift_type == DATADRIFT_TYPE_MODEL else datadrift_id]
                   [m.extended_properties[SCORING_DATE if drift_type == DATADRIFT_TYPE_MODEL else TGT_DST_START_DATE]]]

        logger.debug("{} records left by picking only latest run for each day..".format(len(metrics)))

    # Refine metrics and be compatible for old data:
    #   1. Assign default schema version (0.1) if unavailable in old data
    #   2. Refresh data drift coefficient key if unavailable and put mcc pairs in extended property
    mcc_train_value = 0.0
    mcc_all_value = 0.0
    for m in metrics:
        if m.name == METRIC_DATASHIFT_MCC_TRAIN:
            mcc_train_value = m.value
            metrics.remove(m)
        if m.name == METRIC_DATASHIFT_MCC_ALL:
            mcc_all_value = m.value
            metrics.remove(m)

    for m in metrics:
        if hasattr(m, METRIC_SCHEMA_VERSION_KEY) is False:
            m.schema_version = METRIC_SCHEMA_VERSION_DFT
            if m.name == METRIC_DATASHIFT_MCC_TEST:
                ep = _properties(m.get_extended_properties())
                m.name = OUTPUT_METRIC_DRIFT_COEFFICIENT
                ep[DEBUG_DATASHIFT_MCC_TEST] = m.value
                ep[DEBUG_DATASHIFT_MCC_TRAIN] = mcc_train_value
                ep[DEBUG_DATASHIFT_MCC_ALL] = mcc_all_value
            if m.name == METRIC_DATASHIFT_FEATURE_IMPORTANCE:
                m.name = OUTPUT_METRIC_DRIFT_CONTRIBUTION

    # tempfile.gettempdir() always points to same folder with same guid
    # thus empty temp folder to ensure new contents will be downloaded in each running.
    shutil.rmtree(local_temp_root, ignore_errors=True)

    logger.debug("Return {} records from raw diff result.".format(len(metrics)))
    return metrics


def _download_from_blob_metrics(logger, local_temp_root, target_metrics, latest_pipeline_times,
                                data_store, drift_type, datadrift_id, model_name, model_version, service):
    metrics_rel_path = _get_metrics_path(model_name, model_version, service,
                                         drift_type=drift_type, datadrift_id=datadrift_id,
                                         datastore=data_store)

    # Considering there could be mixed results from scheduled run and adhoc run on each date, should find
    # latest pipeline start time for each date and:
    #
    #   for model based drift, model name/version are always the same for a specific data drift detector but service
    #   could bedifferent, so it's per service per date. The date is the 'scoring_date' in extended properties.
    #
    #   for dataset based drift, there is actually no 'service' so it's just per date. The date is the 'start_date'
    #   in extended properties.
    #
    # Moreover, to make codes aligned, fake a service name for dataset based drift by using is drift id.
    # then both model based and dataset based drift latest pipeline times are all per service per scoring/start date.
    if drift_type == DATADRIFT_TYPE_MODEL:
        service_name = service
    elif drift_type == DATADRIFT_TYPE_DATASET:
        service_name = datadrift_id

    latest_pipeline_times[service_name] = {}

    data_store.download(target_path=local_temp_root, prefix=metrics_rel_path, show_progress=False)

    metrics_list = glob.glob(os.path.join(
        local_temp_root, *"{}/**/*.json".format(metrics_rel_path).split("/")), recursive=True)

    count = 0
    for f in metrics_list:
        with open(f, 'r') as metrics_json:
            data = metrics_json.read()
            metric = _decode_metric(data)

            target_metrics += metric
            count += len(metric)

            # find the latest pipeline start time
            for m in metric:
                if drift_type == DATADRIFT_TYPE_DATASET:
                    target_date = m.extended_properties[TGT_DST_START_DATE]
                elif drift_type == DATADRIFT_TYPE_MODEL:
                    target_date = m.extended_properties[SCORING_DATE]

                if target_date not in latest_pipeline_times[service_name]:
                    latest_pipeline_times[service_name][target_date] = datetime.min

                if PIPELINE_START_TIME in m.extended_properties \
                        and m.extended_properties[PIPELINE_START_TIME] > \
                        latest_pipeline_times[service_name][target_date]:
                    latest_pipeline_times[service_name][target_date] = m.extended_properties[PIPELINE_START_TIME]

    logger.debug("Downloaded {} records in diff result under path {}.".format(count, metrics_rel_path))


# this attribute is also use in server side. (datadrift_run.py, _generate_script.py, msdcuration_run.py ...)
# To be compatible, set default value of drift type as None, then SDK will be able to know if invocation is from
# older version '_generate_script.py'. If yes, it will fall back to model_name/model_version/service style path.
# Otherwise, it will always go to datadrift_id path.
def _get_metrics_path(model_name=None, model_version=None, service=None,
                      target_date=None, drift_type=None, datadrift_id=None, datastore=None):
    """Get the metric path for a given model version, instance target date and frequency of diff.

    :param model_name: Model name
    :type model_name: str
    :param model_version: Model version
    :type model_version: int
    :param service: Service name
    :type service: str
    :param service: datastore instance
    :type service: AbstractDatastore
    :param target_date: Diff instance start time. If none datetime portion is ommitted.
    :type target_date: datetime.datetime
    :return: Relative paths to metric on datastore (model base and general)
    :rtype: str
    """
    # by default reach general output folder
    metrics_output_path = "datadrift/metrics/{}/".format(datadrift_id)

    # validate folder exists in blob storage
    general_output_folder_exist = True
    if datastore:
        blobs = datastore.blob_service.list_blobs(container_name=datastore.container_name, prefix=metrics_output_path)
        blobs = datastore._filter_conflicting_blobs(blobs)
        if len(blobs) == 0:
            general_output_folder_exist = False
    # if general output path doesn't exist or folder is empty, or drift type is None,
    # fall back to traditional model based folders.
    if not drift_type or drift_type == DATADRIFT_TYPE_MODEL or general_output_folder_exist is False:
        metrics_output_path = "DataDrift/Metrics/{}/{}/{}/".format(model_name, model_version, service)

    if target_date is not None:
        metrics_output_path += "{}/".format(target_date.strftime('%Y/%m/%d'))

    return metrics_output_path


def _extended_property_datetime_from_str(extended_property):
    datetime_string_formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]
    datetime_keys = [SCORING_DATE, PIPELINE_START_TIME, TGT_DST_START_DATE, TGT_DST_END_DATE]
    for k in datetime_keys:
        if k in extended_property and isinstance(extended_property[k], str):
            for fmr in datetime_string_formats:
                try:
                    extended_property[k] = datetime.strptime(extended_property[k], fmr)
                    break
                except ValueError:
                    pass
    return extended_property


def _decode_metric(json):
    """ decode json into Metric object.

    :param json:
    :return:
    """
    decoded_metric = dsd.DiffMetric._list_from_json(json)

    for dm in decoded_metric:
        _properties(dm.extended_properties)

    return decoded_metric


def _properties(diff_extended_properties_got):
    """For dataset based results, DiffMetric attribute retruns a dict with information listed directly there,
    and retrieving can be done with return_dict['key']:
    However for model based result, it returns in a different way, all values are in a sub-dict and retrieving
    has to be done like return_dict['extended_property'']['key']
    here expand the model based sub dic to align with behavior of dataset based extended properties.

    :param diff_extended_properties_got:
    :return:
    """
    if 'extended_properties' in diff_extended_properties_got:
        for k, v in diff_extended_properties_got['extended_properties'].items():
            diff_extended_properties_got[k] = v
        del diff_extended_properties_got['extended_properties']

    return _extended_property_datetime_from_str(diff_extended_properties_got)


def _build_single_result_content(drift_type, value, extended_properties):
    """Build a result dict.

    :param value: dataset level drift
    :param extended_properties: extended properties includes information such as scoring time, dataset id...
    :return: result dict.
    """
    result_content = {HAS_DRIFT: value > extended_properties[DRIFT_THRESHOLD],
                      DRIFT_THRESHOLD: extended_properties[DRIFT_THRESHOLD]}

    # TODO: move strings to constants before check in
    if drift_type == DATADRIFT_TYPE_DATASET:
        result_content[TGT_DST_START_DATE] = extended_properties[TGT_DST_START_DATE]
        result_content[TGT_DST_END_DATE] = extended_properties[TGT_DST_END_DATE]
        result_content[KEY_NAME_BASE_DATASET_ID] = extended_properties[KEY_NAME_BASE_DATASET_ID]
        result_content[KEY_NAME_TARGET_DATASET_ID] = extended_properties[KEY_NAME_TARGET_DATASET_ID]
    elif drift_type == DATADRIFT_TYPE_MODEL:
        result_content[DATETIME] = extended_properties[SCORING_DATE]
        result_content[MODEL_NAME] = extended_properties[MODEL_NAME]
        result_content[MODEL_VERSION] = extended_properties[MODEL_VERSION]

    return result_content


def _build_results(drift_type, raw_metrics):
    """Generate all results for queried time window or run id of some a datadriftdetector.

    :param raw_metrics: origin data diff calculation results.
    :return: a list of result dict.
    """
    results = []

    for metric in raw_metrics:
        ep = _properties(metric.get_extended_properties())
        if metric.name == OUTPUT_METRIC_DRIFT_COEFFICIENT:
            # Overall drift coefficient; add to results return object
            create_new_component = True

            for r in results:
                # only model based will enter here to check if service already exist in final output
                if drift_type == DATADRIFT_TYPE_MODEL and r[SERVICE_NAME] == ep[KEY_NAME_SERVICE]:
                    # Service already in dict; add metric to result list
                    create_new_component = False
                    res = r["result"]
                    res.append(_build_single_result_content(drift_type, metric.value, ep))

            if create_new_component:
                res = {KEY_NAME_Drift_TYPE: drift_type}

                # add service name if it's model based
                if drift_type == DATADRIFT_TYPE_MODEL:
                    res[SERVICE_NAME] = ep[KEY_NAME_SERVICE]

                # attach result content
                result_list = []
                result_list.append(_build_single_result_content(drift_type, metric.value, ep))
                res["result"] = result_list

                results.append(res)
    return results


def _create_metric_dict(drift_type, metric):
    """Create metrics dictionary.

    :param metric: Metric object
    :type metric: azureml.contrib.datadrift._datadiff.Metric
    :return: Dictionary of metrics delineated by service
    :rtype: dict()
    """
    ep = _properties(metric.get_extended_properties())
    _metric = {'name': metric.name, 'value': metric.value}

    # general items
    metric_dict = {METRIC_SCHEMA_VERSION_KEY: metric.schema_version} if hasattr(metric, 'schema_version') else {}

    # drift type sensitive items
    if drift_type == DATADRIFT_TYPE_DATASET:
        metric_dict[TGT_DST_START_DATE] = ep[TGT_DST_START_DATE]
        metric_dict[TGT_DST_END_DATE] = ep[TGT_DST_END_DATE]
        metric_dict[KEY_NAME_BASE_DATASET_ID] = ep[KEY_NAME_BASE_DATASET_ID]
        metric_dict[KEY_NAME_TARGET_DATASET_ID] = ep[KEY_NAME_TARGET_DATASET_ID]
    elif drift_type == DATADRIFT_TYPE_MODEL:
        metric_dict[DATETIME] = ep[SCORING_DATE]
        metric_dict[MODEL_NAME] = ep[MODEL_NAME]
        metric_dict[MODEL_VERSION] = ep[MODEL_VERSION]

    # detail metrics
    # Use user friendly key without postfix such as "(Test)"
    if metric.name == METRIC_DATASHIFT_MCC_TEST:
        _metric['name'] = OUTPUT_METRIC_DRIFT_COEFFICIENT

    if ep[METRIC_TYPE] == METRIC_TYPE_DATASET:
        if METRIC_DATASET_METRICS not in metric_dict:
            metric_dict[METRIC_DATASET_METRICS] = []
        metric_dict[METRIC_DATASET_METRICS].append(_metric)

    elif ep[METRIC_TYPE] == METRIC_TYPE_COLUMN:
        column_dict = {ep[COLUMN_NAME]: [_metric]}
        # TODO: refine results returned from get_output for a special case after adding this protection:
        # if whole result json doesn't contain 'dataset' level drift result
        # then the 'results' from get_output will be empty while metrics still contains column level numbers.
        if METRIC_COLUMN_METRICS not in metric_dict:
            metric_dict[METRIC_COLUMN_METRICS] = []
        metric_dict[METRIC_COLUMN_METRICS].append(column_dict)

    return metric_dict


def _check_if_is_expected_metric(drift_type, output_metric, metric):
    """Check if the metric is in expectation for same model/version or baseline/target datasets.

    :param output_metric: metric with final outputs
    :param metric: metric records content from data diff results
    :return: bool
    """
    ep = _properties(metric.get_extended_properties())

    is_exected_metric = (len(ep) > 0)

    if is_exected_metric and drift_type == DATADRIFT_TYPE_DATASET:
        is_exected_metric &= (output_metric[TGT_DST_START_DATE] == ep[TGT_DST_START_DATE])
        is_exected_metric &= (output_metric[TGT_DST_END_DATE] == ep[TGT_DST_END_DATE])
        is_exected_metric &= (output_metric[KEY_NAME_BASE_DATASET_ID] == ep[KEY_NAME_BASE_DATASET_ID])
        is_exected_metric &= (output_metric[KEY_NAME_TARGET_DATASET_ID] == ep[KEY_NAME_TARGET_DATASET_ID])
    elif is_exected_metric and drift_type == DATADRIFT_TYPE_MODEL:
        is_exected_metric &= (output_metric[DATETIME] == ep[SCORING_DATE])
        is_exected_metric &= (output_metric[MODEL_NAME] == ep[MODEL_NAME])
        is_exected_metric &= (output_metric[MODEL_VERSION] == ep[MODEL_VERSION])

    return is_exected_metric


def _build_metrics(drift_type, raw_metrics):
    """Build output dict.

    :param raw_metrics: origin data diff calculation results.
    :return: output metric list.
    """
    output_metrics = []

    for metric in raw_metrics:
        ep = _properties(metric.get_extended_properties())

        # Add to metrics return object
        create_new_component = True
        for m in output_metrics:
            if (drift_type == DATADRIFT_TYPE_MODEL and m[SERVICE_NAME] == ep[KEY_NAME_SERVICE]) \
                    or drift_type == DATADRIFT_TYPE_DATASET:
                create_new_component = False
                met_metric_exists = False
                for output_metric in m['metrics']:
                    if _check_if_is_expected_metric(drift_type, output_metric, metric):
                        _metric = {'name': metric.name, 'value': metric.value}
                        met_metric_exists = True
                        # Add to already existing metric dictionary
                        if ep[METRIC_TYPE] == METRIC_TYPE_DATASET:
                            if METRIC_DATASET_METRICS not in output_metric:
                                output_metric[METRIC_DATASET_METRICS] = []
                            output_metric[METRIC_DATASET_METRICS].append(_metric)

                        elif ep[METRIC_TYPE] == METRIC_TYPE_COLUMN:
                            column_in_metrics = False
                            if METRIC_COLUMN_METRICS not in output_metric:
                                output_metric[METRIC_COLUMN_METRICS] = []
                            for c_metric in output_metric[METRIC_COLUMN_METRICS]:
                                if ep[COLUMN_NAME] in c_metric:
                                    column_in_metrics = True
                                    column = c_metric[ep[COLUMN_NAME]]
                                    column.append(_metric)
                            if not column_in_metrics:
                                # Create column dict in column_metrics
                                column_dict = {ep[COLUMN_NAME]: [_metric]}
                                output_metric[METRIC_COLUMN_METRICS].append(column_dict)
                if not met_metric_exists:
                    # Add new metric in metrics list
                    metric_dict = _create_metric_dict(drift_type, metric)
                    m['metrics'].append(metric_dict)

        if create_new_component:
            # Add metrics service dict
            metrics_list = []
            metric_dict = _create_metric_dict(drift_type, metric)
            metrics_list.append(metric_dict)

            metrics_component = {KEY_NAME_Drift_TYPE: drift_type}
            if drift_type == DATADRIFT_TYPE_MODEL:
                metrics_component[SERVICE_NAME] = ep[KEY_NAME_SERVICE]
            metrics_component['metrics'] = metrics_list
            output_metrics.append(metrics_component)
    return output_metrics


def show(logger, data_store, workspaceid, workspace_name, services, drift_type, datadrift_id,
         baseline_dataset_id, target_dataset_id, model_name, model_version,
         start_time=datetime.min, end_time=datetime.max, with_details=False):
    """Show data drift trend in given time range for a given model, version and service.

    :param start_time:  Optional, start of presenting data time window in UTC, default is 0001-01-01 00:00:00
    :type start_time: datetime.datetime
    :param end_time: Optional, end of presenting data time window in UTC, default is 9999-12-31 23:59:59.999999
    :type end_time: datetime.datetime
    :param with_details: Optional, show additional graphs energy/wasserstein distance if True. Default to False.
    :type with_details: bool
    :return: diction of all figures. Key is service_name
    :rtype: dict()
    """
    start_time_valid = ParameterValidator.validate_datetime(start_time)
    end_time_valid = ParameterValidator.validate_datetime(end_time)

    metrics = _get_metrics(logger, data_store, workspaceid, drift_type, datadrift_id,
                           services, model_name, model_version)

    if len(metrics) == 0:
        raise FileNotFoundError("DataDrift results are unavailable.")

    metrics_services = set()
    if drift_type == DATADRIFT_TYPE_DATASET:
        metrics_services.add(DUMMY_SERVICE)         # to align with model based contents levels, won't be used.
    elif drift_type == DATADRIFT_TYPE_MODEL:
        for m in metrics:
            metrics_services.add(_properties(m.get_extended_properties())[KEY_NAME_SERVICE])

    # build metrics for graph showing of each service in valid date range
    # the graph is per service; In side each graph, there might be sub plots for different measurements.
    # considering the order in dict is not guaranteed, organize all contents with date key and sort by date
    # general data drift will be stored per day
    # detailed measurement will be sorted per measurement per column per day
    contents = {}
    found_nothing = True
    for s in metrics_services:
        if s not in contents:
            contents[s] = {}
        for m in metrics:
            metric_ep = _properties(m.get_extended_properties())
            # use target start date as index for dataset result
            if drift_type == DATADRIFT_TYPE_DATASET:
                stdate = metric_ep[TGT_DST_START_DATE]
                eddate = metric_ep[TGT_DST_END_DATE]
            # use scoring date as index for model based result
            elif drift_type == DATADRIFT_TYPE_MODEL:
                stdate = metric_ep[SCORING_DATE]
                eddate = stdate
            # filtering rules:
            # For model based drift result, filtering with scoring date.
            # For dataset based result, check if 'overlap' between target start/end date and input start/end time.
            if start_time_valid <= stdate <= end_time_valid or start_time_valid <= eddate <= end_time_valid:
                found_nothing = False
                if stdate not in contents[s]:
                    # insert also end date incase needed in future.
                    contents[s][stdate] = {'eddate': eddate}
                if metric_ep[METRIC_TYPE] == METRIC_TYPE_DATASET:
                    contents[s][stdate][m.name] = m.value
                    if drift_type == DATADRIFT_TYPE_MODEL:
                        contents[s][stdate][SERVICE] = metric_ep[SERVICE]
                if metric_ep[METRIC_TYPE] == METRIC_TYPE_COLUMN:
                    if m.name not in contents[s][stdate]:
                        contents[s][stdate][m.name] = {}
                    contents[s][stdate][m.name][metric_ep[COLUMN_NAME]] = m.value

    if found_nothing is True:
        logger.error("No available drift outputs found (from {} to {}).".format(start_time, end_time))
        raise ValueError("No available drift outputs from {} to {}".format(start_time, end_time))

    # produce figures
    figures = {}
    for c in contents:
        # sort by stdate to ensure correct order in graph
        ordered_content = OrderedDict(sorted(contents[c].items(), key=lambda t: t[0]))

        # environment information (alignment refined with extra spaces
        environment = "Workspace Name : {}           \n".format(workspace_name)
        if drift_type == DATADRIFT_TYPE_DATASET:
            environment += "Baseline Dataset Id : {}\nTarget Dataset Id : {}\n".\
                format(baseline_dataset_id, target_dataset_id)
        elif drift_type == DATADRIFT_TYPE_MODEL:
            environment += "Model Name : {}\nModel Version : {}                            \nService Name : {}".\
                format(model_name, model_version, c)

        figure = _generate_plot_figure(environment, drift_type, ordered_content, with_details)

        figures[c] = figure

    return figures


def _generate_plot_figure(environment, drift_type, ordered_content, with_details):
    """Show trends for a metrics.

    :param environment: information of workspace, model, model version and service or baseline/target dataset id.
    :type ordered_content: str
    :param drift_type: drift type
    :type drift_type: str
    :param ordered_content: all contents to present presorted by date (model based) or start date (dataset based)
    :type ordered_content: nested dict
    :param with_details: flag of show all or not
    :type with_details: bool
    :return: matplotlib.figure.Figure
    """
    stdates = list(ordered_content.keys())
    eddates = [v['eddate'] for v in list(ordered_content.values())]
    drifts_train = []
    drift_contribution = {}
    distance_energy = {}
    distnace_wasserstein = {}
    columns = []
    summary_contribute = {}
    bottoms_contribute = []
    columns_distance_e = []
    columns_distance_w = []

    for d in stdates:
        drifts_train.append(ordered_content[d][OUTPUT_METRIC_DRIFT_COEFFICIENT])
        summary_contribute[d] = 0
        bottoms_contribute.append(0)
        for c in ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION].keys():
            if c not in columns:
                columns.append(c)

    for d in stdates:
            for c in columns:
                if OUTPUT_METRIC_DRIFT_CONTRIBUTION in ordered_content[d]:
                    if c not in ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION]:
                        warnings.warn("Drift Contribution of column {} is unavailable.".format(c))
                    if c not in drift_contribution:
                        drift_contribution[c] = {}
                    if c in ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION]:
                        drift_contribution[c][d] = ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION][c]
                        summary_contribute[d] += ordered_content[d][OUTPUT_METRIC_DRIFT_CONTRIBUTION][c]
                    else:
                        # if drift coefficient is missing on that day, set its ratio to 0.
                        drift_contribution[c][d] = 0

            if with_details is True:
                # add distance for all columns, will eliminate columns without distance later.
                if c not in distance_energy:
                    distance_energy[c] = {}
                # default value is null
                distance_energy[c][d] = np.nan
                # update value if distance output is available
                if METRIC_STATISTICAL_DISTANCE_ENERGY in ordered_content[d]:
                    if c in ordered_content[d][METRIC_STATISTICAL_DISTANCE_ENERGY]:
                        distance_energy[c][d] = ordered_content[d][METRIC_STATISTICAL_DISTANCE_ENERGY][c]
                        if c not in columns_distance_e:
                            columns_distance_e.append(c)

                # add distance for all columns, will eliminate columns without distance later.
                if c not in distnace_wasserstein:
                    distnace_wasserstein[c] = {}
                # default value is null
                distnace_wasserstein[c][d] = np.nan
                # update value if distance output is available
                if METRIC_STATISTICAL_DISTANCE_WASSERSTEIN in ordered_content[d]:
                    if c in ordered_content[d][METRIC_STATISTICAL_DISTANCE_WASSERSTEIN]:
                        distnace_wasserstein[c][d] = ordered_content[d][METRIC_STATISTICAL_DISTANCE_WASSERSTEIN][c]
                        if c not in columns_distance_w:
                            columns_distance_w.append(c)

    # sum up daily coefficient
    daily_summary_contribution = list(summary_contribute.values())
    columns_contribution = list(drift_contribution.keys())

    # remove columns if distance is unavailable for all days.
    distance_energy = {k: v for k, v in distance_energy.items() if k in columns_distance_e}
    distnace_wasserstein = {k: v for k, v in distnace_wasserstein.items() if k in columns_distance_w}

    # show data drift
    width = 10
    height = 8
    # by default will show both drift coefficient and drift contribution so wide always divides into 2
    wdivid = 2
    hdivid = 2 if with_details is True else 1

    if drift_type == DATADRIFT_TYPE_DATASET:
        myFmt = mdates.DateFormatter('[%Y-%m-%d, %Y-%m-%d]')
    elif drift_type == DATADRIFT_TYPE_MODEL:
        myFmt = mdates.DateFormatter('%Y-%m-%d')

    # when time range is wide and stdates are actually uncontinuous, just show stdates with drifts.
    xrange = pd.date_range(stdates[0], stdates[-1], freq='D')
    xrange = [x for x in xrange if x.date() in [y.date() for y in stdates]]

    xlabel = 'Day'
    for d in range(len(stdates)):
        gap = eddates[d] - stdates[d]
        if gap == timedelta(7):
            xlabel = 'Week of'
        elif gap > timedelta(1):
            xlabel = "{} days from".format(gap.days)

    # create canvas
    figure = plt.figure(figsize=(width * wdivid, height * hdivid))
    plt.suptitle(environment, fontsize=14)
    plt.subplots_adjust(bottom=0.1, top=0.85 if with_details is True else 0.75, hspace=0.5)
    plt.tight_layout()
    ax1 = plt.subplot(hdivid, wdivid, 1)

    # draw drift coefficient
    plt.sca(ax1)
    plt.plot_date(stdates, drifts_train, '-g', marker='.', linewidth=0.5, markersize=5)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel("Drift", fontsize=16)
    plt.xticks(xrange, rotation=15)
    ax1.set_ylim(ymin=0, ymax=1.1)
    plt.title("Drift Coefficient\n", fontsize=20)

    # draw drift contribution
    ax2 = plt.subplot(hdivid, wdivid, 2)
    colors = plt.cm.get_cmap('gist_rainbow')

    plt.sca(ax2)
    yvals = ax2.get_yticks()
    ax2.set_yticklabels(['{:,.2%}'.format(v) for v in yvals])
    # ax2.xaxis.set_major_formatter(myFmt)
    for c in columns_contribution:
        # draw bar graph
        contribution = list(drift_contribution[c].values())
        bar_ratio = [x / y for x, y in zip(contribution, daily_summary_contribution)]
        ax2.bar(stdates, height=bar_ratio, bottom=bottoms_contribute)
        bottoms_contribute = [x + y for x, y in zip(bottoms_contribute, bar_ratio)]

    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(FIGURE_FEATURE_IMPORTANCE_Y_LABEL, fontsize=16)
    plt.xticks(xrange, rotation=15)
    plt.title(FIGURE_FEATURE_IMPORTANCE_TITLE, fontsize=20)
    plt.legend(columns_contribution)

    if with_details is True:
        ax3 = plt.subplot(hdivid, wdivid, 3)
        ax4 = plt.subplot(hdivid, wdivid, 4)

        plt.sca(ax3)
        plt.yscale('log')
        # to present value 0 under logscale
        ax3.set_xscale('symlog')
        ax3.set_yscale('symlog')
        ax3.xaxis.set_major_formatter(myFmt)
        for c in columns_distance_e:
            plt.plot_date(stdates, distance_energy[c].values(),
                          c=colors(1. * columns.index(c) / len(columns)),
                          linestyle='dashed', marker='.', linewidth=0.5, markersize=5)
        plt.xlabel(xlabel, fontsize=16)
        plt.ylabel("Distance", fontsize=16)
        plt.xticks(xrange, rotation=15)
        plt.title("Energy Distance\n", fontsize=20)
        plt.legend(columns_distance_e)

        plt.sca(ax4)
        plt.yscale('log')
        # to present value 0 under logscale
        ax4.set_xscale('symlog')
        ax4.set_yscale('symlog')
        ax4.xaxis.set_major_formatter(myFmt)
        for c in columns_distance_w:
            plt.plot_date(stdates, distnace_wasserstein[c].values(),
                          c=colors(1. * columns.index(c) / len(columns)),
                          linestyle='dashed', marker='.', linewidth=0.5, markersize=5)
        plt.xlabel(xlabel, fontsize=16)
        plt.ylabel("Distance", fontsize=16)
        plt.xticks(xrange, rotation=15)
        plt.title("Wasserstein Distance\n", fontsize=20)
        plt.legend(columns_distance_w)

    return figure
