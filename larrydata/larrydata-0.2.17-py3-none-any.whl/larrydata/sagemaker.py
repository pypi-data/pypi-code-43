import json
import larrydata.s3 as s3


def build_ground_truth_pre_response(event, log_details=True, input_attribute='taskObject'):
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


def build_ground_truth_pre_response_from_object(event, log_details=True, input_attribute='taskObject', s3_resource=None):
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


def build_ground_truth_consolidation_response(event, log_details=True):
    if log_details:
        print(json.dumps(event))
    payload = get_ground_truth_payload(event)
    if log_details:
        print('Payload: {}'.format(json.dumps(payload)))

    consolidated_response = []
    for dataset in payload:
        responses = get_ground_truth_worker_responses(dataset['annotations'])

        consolidated_response.append({
            'datasetObjectId': dataset['datasetObjectId'],
            'consolidatedAnnotation' : {
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


def get_ground_truth_worker_responses(annotations):
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


def get_ground_truth_payload(event):
    if 'payload' in event:
        return s3.read_dict(uri=event['payload']['s3Uri'])
    else:
        return event.get('test_payload',[])
