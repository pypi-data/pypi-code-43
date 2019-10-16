import json
import larrydata.s3 as s3
import larrydata.utils as utils
import boto3


_client = None
# A local instance of the boto3 session to use
_session = boto3.session.Session()


def set_session(aws_access_key_id=None,
                aws_secret_access_key=None,
                aws_session_token=None,
                region_name=None,
                profile_name=None,
                session=None):
    """
    Sets the boto3 session for this module to use a specified configuration state.
    :param aws_access_key_id: AWS access key ID
    :param aws_secret_access_key: AWS secret access key
    :param aws_session_token: AWS temporary session token
    :param region_name: Default region when creating new connections
    :param profile_name: The name of a profile to use
    :param session: An existing session to use
    :return: None
    """
    global _session, _client
    _session = session if session is not None else boto3.session.Session(**utils.copy_non_null_keys(locals()))
    _client = None


def client():
    global _client, _session
    if _client is None:
        _client = _session.client('sagemaker')
    return _client


def build_pre_response(event, log_details=True, input_attribute='taskObject'):
    if log_details:
        print(event)
    source = event['dataObject'].get('source', event['dataObject'].get('source-ref'))
    if source is None:
        print('No source or source-ref value found')
        return {}
    if log_details:
        print('Task object is: {}'.format(source))
    response = {'taskInput': {}}
    response['taskInput'][input_attribute] = source
    if log_details:
        print('Response is {}'.format(json.dumps(response)))
    return response


def build_pre_response_from_object(event, log_details=True, input_attribute='taskObject', s3_resource=None):
    if log_details:
        print(event)
    source_ref = event['dataObject'].get('source-ref')
    if source_ref:
        if s3_resource:
            value = s3.read_dict(uri=source_ref, s3_resource=s3_resource)
        else:
            value = s3.read_dict(uri=source_ref)
    else:
        source = event['dataObject'].get('source')
        if source is None:
            print('No source or source-ref value found')
            return {}
        else:
            if type(source) is str:
                value = json.loads(source)
            else:
                value = source
    if log_details:
        print('Task object is: {}'.format(json.dumps(value)))
    response = {'taskInput': {}}
    response['taskInput'][input_attribute] = value
    if log_details:
        print('Response is {}'.format(json.dumps(response)))
    return response


def build_consolidation_response(event, log_details=True):
    if log_details:
        print(json.dumps(event))
    payload = get_payload(event)
    if log_details:
        print('Payload: {}'.format(json.dumps(payload)))

    consolidated_response = []
    for dataset in payload:
        responses = extract_worker_responses(dataset['annotations'])
        consolidated_response.append({
            'datasetObjectId': dataset['datasetObjectId'],
            'consolidatedAnnotation': {
                'content': {
                    event['labelAttributeName']: {
                        'responses': responses
                    }
                }
            }
        })
    if log_details:
        print('Consolidated response: {}'.format(json.dumps(consolidated_response)))
    return consolidated_response


def extract_worker_responses(annotations):
    responses = []
    for annotation in annotations:
        response = json.loads(annotation['annotationData']['content'])
        if 'annotatedResult' in response:
            response = response['annotatedResult']

        responses.append({
            'workerId': annotation['workerId'],
            'annotation': response
        })
    return responses


def get_payload(event):
    if 'payload' in event:
        return s3.read_dict(uri=event['payload']['s3Uri'])
    else:
        return event.get('test_payload', [])


def _input_config(manifest_uri, free_of_pii=False, free_of_adult_content=True):
    config = {
        'DataSource': {
            'S3DataSource': {
                'ManifestS3Uri': manifest_uri
            }
        }
    }
    content_classifiers = []
    if free_of_adult_content:
        content_classifiers.append('FreeOfAdultContent')
    if free_of_pii:
        content_classifiers.append('FreeOfPersonallyIdentifiableInformation ')
    if len(content_classifiers) > 0:
        config['DataAttributes'] = {'ContentClassifiers': content_classifiers}
    return config


def _output_config(output_uri, kms_key=None):
    config = {
        'S3OutputPath': output_uri
    }
    if kms_key:
        config['KmsKeyId'] = kms_key
    return config


def build_human_task_config(template_uri, pre_lambda_arn, consolidation_lambda_arn, title, description, workers=1,
                            public=False, reward_in_cents=None, workteam_arn=None, time_limit=300, lifetime=345600,
                            max_concurrent_tasks=None, keywords=None):
    config = {
        'UiConfig': {
            'UiTemplateS3Uri': template_uri
        },
        'PreHumanTaskLambdaArn': pre_lambda_arn,
        'TaskTitle': title,
        'TaskDescription': description,
        'NumberOfHumanWorkersPerDataObject': workers,
        'TaskTimeLimitInSeconds': time_limit,
        'TaskAvailabilityLifetimeInSeconds': lifetime,
        'AnnotationConsolidationConfig': {
            'AnnotationConsolidationLambdaArn': consolidation_lambda_arn
        }
    }
    if public:
        config['WorkteamArn'] = 'arn:aws:sagemaker:us-west-2:394669845002:workteam/public-crowd/default'
        if reward_in_cents is None:
            raise Exception('You must provide a reward amount for a public labeling job')
        else:
            config['PublicWorkforceTaskPrice'] = {
                'AmountInUsd': {
                    'Dollars': int(reward_in_cents // 100),
                    'Cents': int(reward_in_cents),
                    'TenthFractionsOfACent': round((reward_in_cents % 1) * 10)
                }
            }
    elif workteam_arn is not None:
        config['WorkteamArn'] = workteam_arn
    else:
        raise Exception('Labeling job must be public or have a workteam ARN')
    if keywords:
        config['TaskKeywords'] = keywords
    if max_concurrent_tasks:
        config['MaxConcurrentTaskCount'] = max_concurrent_tasks
    return config


def build_stopping_conditions(max_human_labeled_object_count=None, max_percentage_labeled=None):
    if max_human_labeled_object_count is None or max_percentage_labeled is None:
        return None
    else:
        config = {}
        if max_human_labeled_object_count:
            config['MaxHumanLabeledObjectCount'] = max_human_labeled_object_count
        if max_percentage_labeled:
            config['MaxPercentageOfInputDatasetLabeled'] = max_percentage_labeled
        return config


def build_algorithms_config(algorithm_specification_arn, initial_active_learning_model_arn=None, kms_key=None):
    if algorithm_specification_arn is None:
        return None
    config = {
        'LabelingJobAlgorithmSpecificationArn': algorithm_specification_arn
    }
    if initial_active_learning_model_arn:
        config['InitialActiveLearningModelArn'] = initial_active_learning_model_arn
    if kms_key:
        config['LabelingJobResourceConfig'] = {'VolumeKmsKeyId': kms_key}
    return config


def create_job(name,
               manifest_uri,
               output_uri,
               role_arn,
               task_config,
               category_config_uri=None,
               label_attribute_name=None,
               free_of_pii=False,
               free_of_adult_content=True,
               algorithms_config=None,
               stopping_conditions=None,
               sagemaker_client=client()):
    if label_attribute_name is None:
        label_attribute_name = name
    params = {
        'LabelingJobName': name,
        'LabelAttributeName': label_attribute_name,
        'InputConfig': _input_config(manifest_uri, free_of_pii, free_of_adult_content),
        'OutputConfig': _output_config(output_uri),
        'RoleArn': role_arn,
        'HumanTaskConfig': task_config
    }
    if category_config_uri:
        params['LabelCategoryConfigS3Uri'] = category_config_uri
    if algorithms_config:
        params['LabelingJobAlgorithmsConfig'] = algorithms_config
    if stopping_conditions:
        params['StoppingConditions'] = stopping_conditions
    print(params)
    print(**params)
    return sagemaker_client.create_labeling_job(**params)


def describe_job(name, sagemaker_client=client()):
    return sagemaker_client.describe_labeling_job(LabelingJobName=name)


def get_job_state(name, sagemaker_client=client()):
    response = describe_job(name, sagemaker_client)
    status = response['LabelingJobStatus']
    labeled = response['LabelCounters']['TotalLabeled']
    unlabeled = response['LabelCounters']['Unlabeled']
    return "{} ({}/{})".format(status, labeled, unlabeled + labeled)


def built_in_pre_lambda_bounding_box(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('PRE', region, 'BoundingBox')


def built_in_pre_lambda_image_multi_class(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('PRE', region, 'ImageMultiClass')


def built_in_pre_lambda_semantic_segmentation(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('PRE', region, 'SemanticSegmentation')


def built_in_pre_lambda_text_multi_class(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('PRE', region, 'TextMultiClass')


def built_in_pre_lambda_named_entity_recognition(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('PRE', region, 'NamedEntityRecognition')


def built_in_acs_lambda_bounding_box(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('ACS', region, 'BoundingBox')


def built_in_acs_lambda_image_multi_class(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('ACS', region, 'ImageMultiClass')


def built_in_acs_lambda_semantic_segmentation(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('ACS', region, 'SemanticSegmentation')


def built_in_acs_lambda_text_multi_class(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('ACS', region, 'TextMultiClass')


def built_in_acs_lambda_named_entity_recognition(region=None):
    region = _session.region_name if region is None else region
    return _built_in_lambda('ACS', region, 'NamedEntityRecognition')


def _built_in_lambda(mode, region, task):
    accounts = {
        'us-east-1': '432418664414',
        'us-east-2': '266458841044',
        'us-west-2': '081040173940',
        'ca-central-1': '918755190332',
        'eu-west-1': '568282634449',
        'eu-west-2': '487402164563',
        'eu-central-1': '203001061592',
        'ap-northeast-1':'477331159723',
        'ap-northeast-2':'845288260483',
        'ap-south-1':'565803892007',
        'ap-southeast-1':'377565633583',
        'ap-southeast-2':'454466003867'
    }
    account_id = accounts.get(region)
    if account_id:
        return 'arn:aws:lambda:{}:{}:function:{}-{}'.format(region, account_id, mode.upper(), task)
    else:
        raise Exception('Unrecognized region')
