import boto3
import botocore
import os
import uuid
import json
import sys
import re
import time
import textwrap
import threading
from datetime import datetime, timezone
from boto3.s3.transfer import S3Transfer
from vulcan.aws.services._session import AWSSession
from vulcan.aws import shared
from vulcan.aws._common import dump

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

shared.store['validated_templates'] = list()
LOG_GROUP = 'cfnotify'

STATUS_UPDATE_COMPLETE = ('UPDATE_COMPLETE', 'UPDATE_FAILED', 'UPDATE_ROLLBACK_FAILED',
                          'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE')
STATUS_CREATE_COMPLETE = ('CREATE_COMPLETE', 'CREATE_FAILED')
STATUS_DELETE_COMPLETE = ('DELETE_COMPLETE', 'DELETE_FAILED')
STATUS_ROLLBACK_COMPLETE = ('ROLLBACK_FAILED', 'ROLLBACK_COMPLETE')

STATUS_CF_RUN_COMPLETE = list()
STATUS_CF_RUN_COMPLETE.extend(STATUS_UPDATE_COMPLETE)
STATUS_CF_RUN_COMPLETE.extend(STATUS_CREATE_COMPLETE)
STATUS_CF_RUN_COMPLETE.extend(STATUS_DELETE_COMPLETE)
STATUS_CF_RUN_COMPLETE.extend(STATUS_ROLLBACK_COMPLETE)


class AWSCloudFormation(AWSSession):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(
            kwargs.get('profile_name'),
            kwargs.get('region_name', None)
        )
        self.stack_name = kwargs['stack_name']

        if (len(kwargs) == 2 and
                'profile_name' in kwargs and
                'stack_name' in kwargs):
            # Easy service, for lookups only
            self.easy_service = True
        elif (len(kwargs) == 3 and
              'profile_name' in kwargs and
              'stack_name' in kwargs and
              'region_name' in kwargs):
            # Easy service, for lookups only
            self.easy_service = True
        else:
            self.easy_service = False

            self.on_failure = kwargs.get('on_failure', 'ROLLBACK')

            if 'template' in kwargs and type(kwargs['template']) == str:
                self.template = kwargs['template']
            else:
                raise Exception('Missing or wrong parameter: template')

            self.includes = list()
            if 'includes' in kwargs:
                if type(kwargs['includes']) == list:
                    self.includes = kwargs['includes']
                else:
                    raise Exception('Wrong parameter type: '
                                    'includes = {}'.format(
                                        type(kwargs['includes'])))

            self.resources = list()
            if 'resources' in kwargs:
                if type(kwargs['resources']) == list:
                    self.resources = kwargs['resources']
                else:
                    raise Exception('Wrong parameter type: '
                                    'resources = {}'.format(
                                        type(kwargs['resources'])))

            if 'parameters' in kwargs:
                self.parameters = kwargs['parameters']
            else:
                self.parameters = None

            path_to_cloudformation = os.path.abspath(os.path.join(os.getcwd(), './src/cloudformation/'))
            if not os.path.exists(path_to_cloudformation):
                path_to_cloudformation = os.path.abspath(
                    os.path.join(os.getcwd(), './src/main/cloudformation/')
                )

            path_to_resources = os.path.abspath(os.path.join(os.getcwd(), './src/resources/'))
            if not os.path.exists(path_to_cloudformation):
                path_to_resources = os.path.abspath(os.path.join(os.getcwd(), './src/main/resources/'))

            self.template = os.path.abspath(os.path.join(path_to_cloudformation, self.template))
            for idx, template in enumerate(self.includes):
                if not os.path.isabs(template):
                    if template.startswith('./') or template.startswith('../'):
                        self.includes[idx] = os.path.abspath(
                            os.path.join(os.getcwd(), template))
                    else:
                        self.includes[idx] = os.path.abspath(os.path.join(path_to_cloudformation, template))

                if not os.path.isfile(self.includes[idx]):
                    raise Exception("Can't find template file"
                                    " '{}' ({})".format(
                                        template,
                                        self.includes[idx]))

            for idx, file in enumerate(self.resources):
                if not os.path.isabs(file):
                    if file.startswith('./') or file.startswith('../'):
                        self.resources[idx] = os.path.abspath(
                            os.path.join(os.getcwd(), file))
                    else:
                        self.resources[idx] = os.path.abspath(os.path.join(path_to_resources, file))

                if not os.path.isfile(self.resources[idx]):
                    raise Exception("Can't find resource file "
                                    "'{}' ({})".format(
                                        file, self.resources[idx]))

            url = urlparse(kwargs['s3_uri'])
            self.s3_bucket = url.netloc
            self.s3_key = url.path

            if self.s3_key.endswith('/'):
                self.s3_key = "%s%s" % (
                    self.s3_key, os.path.basename(self.template))

            if self.s3_key.startswith('/'):
                self.s3_key = self.s3_key[1:]

    # @property
    # def s3_uri(self):
    #   return self._s3_uri

    def exists(self):
        cloudformation = self.client('cloudformation')
        STACK_EXISTS_STATES = [
            'CREATE_COMPLETE',
            'ROLLBACK_COMPLETE',
            'UPDATE_COMPLETE',
            'UPDATE_ROLLBACK_COMPLETE'
        ]
        try:
            stack = None
            nextToken = None
            while not stack:
                resp = None
                if nextToken:
                    resp = cloudformation.describe_stacks(
                        StackName=self.stack_name, NextToken=nextToken)
                else:
                    resp = cloudformation.describe_stacks(
                        StackName=self.stack_name)

                for stack in resp['Stacks']:
                    if stack['StackStatus'] in STACK_EXISTS_STATES:
                        return True
                if 'NextToken' in stack:
                    nextToken = stack['NextToken']

            return False
        except botocore.exceptions.ClientError as err:
            err_msg = err.response['Error']['Message']
            err_code = err.response['Error']['Code']
            if err_msg != "Stack with id {} does not exist".format(self.stack_name) and \
               err_code != 'ValidationError':
                return False

    def print_outputs(self, **kwargs):
        stack_outputs = self.outputs(**kwargs)

        if len(outputs) == 0:
            print("Stack {} don't have any outputs".format(self.stack_name))
        else:
            print("Stack {} outputs:".format(self.stack_name))
            max_name_len = 0
            for output in outputs:
                max_name_len = max(max_name_len, len(output['OutputKey']))
            for output in outputs:
                print(' '.join([
                    output['OutputKey'].ljust(max_name_len) + ':',
                    output['OutputValue'],
                ]))

    def outputs(self, output_key=None, **kwargs):
        cloudformation = self.client('cloudformation')
        STACK_EXISTS_STATES = [
            'CREATE_COMPLETE',
            'ROLLBACK_COMPLETE',
            'UPDATE_COMPLETE',
            'UPDATE_ROLLBACK_COMPLETE'
        ]

        no_fail = False
        no_cache = False
        if kwargs:
            no_fail = kwargs.get('no_fail', False)
            no_cache = kwargs.get('no_cache', False)

        stack_outputs = None
        nextToken = None
        cache_key = 'cloudformation.outputs.{}.{}.{}'.format(
            self.region_name,
            self.profile_name,
            self.stack_name
        )
        if not no_cache:
            stack_outputs = self.cache(cache_key)

        if not stack_outputs:
            try:
                stack = None
                stack_outputs = list()

                paginator = cloudformation.get_paginator('describe_stacks')
                page_iterator = paginator.paginate(StackName=self.stack_name)
                break_for = False
                for page in page_iterator:
                    for stack in page['Stacks']:
                        if stack['StackStatus'] in STACK_EXISTS_STATES:
                            stack_outputs = stack.get('Outputs', list())
                            self.cache(cache_key, stack_outputs)
                            break_for = True
                            break
                    if break_for:
                        break
            except botocore.exceptions.ClientError as err:
                err_msg = err.response['Error']['Message']
                err_code = err.response['Error']['Code']
                if err_msg != "Stack with id {} does not exist".format(self.stack_name) and \
                   err_code != 'ValidationError':
                    if no_fail:
                        print("Stack with id {} does not exist".format(self.stack_name))
                    else:
                        raise Exception("Stack with id {} does not exist".format(
                            self.stack_name), sys.exc_info()[2])

        if output_key:
            print('AWSCloudFormation.output(): WARING: outputs method is deprecated, use output instead')
            for output in stack_outputs:
                if output['OutputKey'] == output_key:
                    return output['OutputValue']
            print("AWSCloudFormation.output(): " +
                  "Can't find output parameter {} in stack {} under {} profile".format(
                      output_key,
                      self.stack_name,
                      self.profile_name
                  ))

            return None
        else:
            return stack_outputs

    def output(self, output_key, **kwargs):
        stack_outputs = self.outputs(**kwargs)

        for output in stack_outputs:
            if output['OutputKey'] == output_key:
                return output['OutputValue']

        print("Can't find output parameter {} in stack {} under {} profile".format(
            output_key,
            self.stack_name,
            self.profile_name
        ))

        return None

    def validate(self, details=False):
        s3 = self.client('s3')
        for template in ([self.template] + self.includes):

            if template in shared.store['validated_templates']:
                print('Template {} has been validated already'.format(
                    template
                ))
                continue
            else:
                shared.store['validated_templates'].append(template)

            temp_filename = "temp/%s-%s" % (uuid.uuid4(),
                                            os.path.basename(template))
            print("Uploading %s to temporary location s3://%s/%s" %
                  (template, self.s3_bucket, temp_filename))
            S3Transfer(s3).upload_file(
                template,
                self.s3_bucket,
                temp_filename,
                extra_args={'ACL': 'bucket-owner-full-control'}
            )

            template_url = "https://s3.amazonaws.com/%s/%s" % (
                self.s3_bucket, temp_filename)
            print("Validating template %s" % template_url)
            resp = self.client('cloudformation').validate_template(
                TemplateURL=template_url
            )

            if details:
                print('Template {} details: {}'.format(
                    template,
                    json.dumps(resp, indent=2, separators=(',', ': '))))

            print("Removing temporary file /%s from s3" % temp_filename)
            s3.delete_object(
                Bucket=self.s3_bucket,
                Key=temp_filename,
            )

    def create(self, **kwargs):
        self._upload()

        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/%s/%s" % (
            self.s3_bucket, self.s3_key)
        print("Creating stack {}".format(stack_name))
        timestamp = datetime.now(timezone.utc)
        stack_id = None
        parameters = self._join_parameters(self.parameters, kwargs.get('parameters', None))
        try:
            resp = cloudformation.create_stack(
                StackName=stack_name,
                TemplateURL=template_url,
                Capabilities=['CAPABILITY_NAMED_IAM'],
                OnFailure=self.on_failure,
                Parameters=parameters
            )
            stack_id = resp['StackId']
        except botocore.exceptions.ParamValidationError as error:
            if str(error).startswith("Parameter validation failed:\nInvalid type for parameter"):
                res = re.search((r'Invalid type for parameter Parameters\[(\d)\].ParameterValue, '
                                r'value: None, type: (.+), valid types: (.+)'), str(error))
                param_idx = int(res.group(1))
                param_type_asis = res.group(2)
                param_type_tobe = res.group(3)

                print('Validation error:')
                print('Parameter {param_name} has invalid type/value.'.format(
                    param_name=parameters[param_idx]['ParameterKey']
                ))
                print('Expected: {expected}, Actual: {actual}/{value}'.format(
                    expected=param_type_tobe,
                    actual=param_type_asis,
                    value=parameters[param_idx]['ParameterValue']
                ))
                sys.exit(1)
            else:
                raise error
        except botocore.exceptions.ClientError as error:
            err_msg = error.response['Error']['Message']
            err_code = error.response['Error']['Code']
            if err_code == 'ValidationError':
                print('Validation error: {}'.format(err_msg))
                sys.exit(1)
            else:
                raise error

        self._print_events(stack_id, stack_name, timestamp)

        outputs = self.outputs(no_cache=True)
        if len(outputs) == 0:
            print("Stack {} don't have any outputs".format(self.stack_name))
        else:
            print("Stack {} outputs:".format(self.stack_name))
            for output in outputs:
                print('{key}: {value}'.format(
                    key=output['OutputKey'],
                    value=output['OutputValue'],
                ))

        return

    def update(self, **kwargs):
        self._upload()

        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/%s/%s" % (
            self.s3_bucket, self.s3_key)
        print("Updating stack {}".format(stack_name))
        timestamp = datetime.now(timezone.utc)
        resp = cloudformation.update_stack(
            StackName=stack_name,
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=self._join_parameters(
                self.parameters, kwargs.get('parameters', None))
        )

        self._print_events(resp['StackId'], stack_name, timestamp)

        outputs = self.outputs(no_cache=True)
        if len(outputs) == 0:
            print("Stack {} don't have any outputs".format(self.stack_name))
        else:
            print("Stack {} outputs:".format(self.stack_name))
            for output in outputs:
                print('{key}: {value}'.format(
                    key=output['OutputKey'],
                    value=output['OutputValue'],
                ))

        return

    def delete(self, **kwargs):
        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        resp = cloudformation.describe_stacks(StackName=stack_name)

        print('Deleting stack {}'.format(stack_name))
        timestamp = datetime.now(timezone.utc)
        cloudformation.delete_stack(
            StackName=resp['Stacks'][0]['StackId']
        )

        self._print_events(resp['Stacks'][0]['StackId'], stack_name, timestamp)

        cache_key = 'cloudformation.outputs.{}.{}.{}'.format(
            self.region_name,
            self.profile_name,
            self.stack_name
        )
        self.cache(cache_key, list())

        return

    def wait_complete(self, **kwargs):
        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        print('Waiting stack {} status complete'.format(stack_name))
        waiter = cloudformation.get_waiter('stack_create_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def wait_update(self, **kwargs):
        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        print('Waiting stack {} status updated'.format(stack_name))
        waiter = cloudformation.get_waiter('stack_update_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def wait_delete(self, **kwargs):
        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        print('Waiting stack {} status deleted'.format(stack_name))
        waiter = cloudformation.get_waiter('stack_delete_complete')
        waiter.wait(
            StackName=stack_name
        )

        return

    def dry_run(self, **kwargs):
        self._upload()

        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/%s/%s" % (
            self.s3_bucket, self.s3_key)

        change_set_name = 'cs{ts}'.format(ts=time.strftime('%Y%m%d%H%M%S'))
        client_token = 'token{uuid}'.format(uuid=uuid.uuid4())

        print("Running dry_run for stack {}".format(stack_name))
        change_set = cloudformation.create_change_set(
            StackName=stack_name,
            ChangeSetName=change_set_name,
            ClientToken=client_token,
            ChangeSetType='UPDATE',
            TemplateURL=template_url,
            Capabilities=['CAPABILITY_NAMED_IAM'],
            Parameters=self._join_parameters(
                self.parameters,
                kwargs.get('parameters', None)
            )
        )
        waiter = cloudformation.get_waiter('change_set_create_complete')
        try:
            waiter.wait(
                StackName=stack_name,
                ChangeSetName=change_set_name
            )

            print('Changes to be performed:')
            next_token = None
            while True:
                args = {
                    'StackName': stack_name,
                    'ChangeSetName': change_set['Id'],
                }
                if next_token:
                    args['NextToken'] = next_token

                resp = cloudformation.describe_change_set(**args)

                for change in resp['Changes']:
                    print('{action}: {id} - {res_type}'.format(
                        action=change['ResourceChange']['Action'],
                        id=change['ResourceChange']['LogicalResourceId'],
                        res_type=change['ResourceChange']['ResourceType'],
                    ))

                if 'NextToken' not in resp:
                    break
                else:
                    next_token = resp['NextToken']

        except botocore.exceptions.WaiterError as error:
            if error.kwargs['reason'] == ('Waiter encountered a '
               'terminal failure state'):
                resp = cloudformation.describe_change_set(
                    StackName=stack_name,
                    ChangeSetName=change_set['Id'],
                )
                if resp['StatusReason'] == (
                    "The submitted information "
                    "didn't contain changes. "
                    "Submit different information "
                    "to create a change set."
                ):
                    print("No changes.")
                else:
                    raise Exception("Unknown error", None, sys.exc_info()[2])
            else:
                raise Exception("Unknown error", None, sys.exc_info()[2])
        finally:
            print('Deleting change set')
            cloudformation.delete_change_set(
                StackName=stack_name,
                ChangeSetName=change_set['Id']
            )

        return

    def estimate_cost(self, **kwargs):
        self._upload()

        cloudformation = self.client('cloudformation')

        stack_name = self.stack_name
        if 'stack_name' in kwargs:
            stack_name = kwargs.get('stack_name')

        template_url = "https://s3.amazonaws.com/{}/{}".format(
            self.s3_bucket, self.s3_key)
        print("Estimating template s3://{}/{}".format(
            self.s3_bucket, self.s3_key
        ))
        resp = cloudformation.estimate_template_cost(
            TemplateURL=template_url,
            Parameters=self._join_parameters(
                self.parameters, kwargs.get('parameters', None))
        )

        print('Check URL to see your template costs estimateion:\n{}'.format(
            resp['Url']))

        return

    def _upload(self):
        print("Uploading %s to s3://%s/%s" %
              (self.template, self.s3_bucket, self.s3_key))
        S3Transfer(self.client('s3')).upload_file(
            self.template,
            self.s3_bucket,
            self.s3_key,
            extra_args={'ACL': 'bucket-owner-full-control'}
        )

        s3_key = self.s3_key
        if not s3_key.endswith('/'):
            s3_key = s3_key[:s3_key.rfind('/') + 1]

        for file in (self.includes + self.resources):
            file_s3_key = '{}{}'.format(s3_key, os.path.basename(file))

            print("Uploading %s to s3://%s/%s" %
                  (file, self.s3_bucket, file_s3_key))
            S3Transfer(self.client('s3')).upload_file(
                file,
                self.s3_bucket,
                file_s3_key,
                extra_args={'ACL': 'bucket-owner-full-control'}
            )

    def _join_parameters(self, params1, params2):
        if (params1 and type(params1) != list) or \
           (params2 and type(params2) != list):
            raise Exception("Parameters argument should be a list() or None")

        if not params1 and params2:
            return params2
        elif params1 and not params2:
            return params1
        elif params1 and params2:
            result_d = dict()
            for param in params1:
                result_d[param['ParameterKey']] = param['ParameterValue']
            for param in params2:
                result_d[param['ParameterKey']] = param['ParameterValue']

            result = list()
            for key in result_d:
                result.append({
                    'ParameterKey': key,
                    'ParameterValue': result_d[key]
                })
            return result
        else:
            return list()

    def _trunc(self, text, length):
        if len(text) > length:
            ln_before = int(length / 2) - 2 + int(length / 4)
            ln_after = length - ln_before - 2
            result = text[:ln_before] + '..' + text[-ln_after:]
            return result
        else:
            return text.ljust(length)

    def _print_events(self, root_stack_id, root_stack_name, start_ts):
        cloudformation = self.client('cloudformation')

        stack_ids = [root_stack_id]
        stack_data_template = {
            'event_ids_shown': set(),
            'stack_name': root_stack_name
        }
        stack_data = {
            root_stack_id: stack_data_template.copy()
        }

        paginator = cloudformation.get_paginator('describe_stack_events')

        stacks_running = 0
        while(stacks_running < len(stack_ids)):
            for stack_id in stack_ids:
                try:
                    resp_iterator = paginator.paginate(StackName=stack_id)
                    for page in resp_iterator:
                        for event in page['StackEvents']:
                            phResId = event.get('PhysicalResourceId', None)
                            if event['EventId'] not in stack_data[stack_id]['event_ids_shown'] and \
                               event['Timestamp'] > start_ts:
                                if 'AWS::CloudFormation::Stack' == event['ResourceType'] and \
                                   phResId and \
                                   phResId not in stack_ids:
                                    stack_ids.append(phResId)
                                    stack_data[phResId] = stack_data_template.copy()
                                    stack_data[phResId]['stack_name'] = event['LogicalResourceId']

                                stack_data[stack_id].get('event_ids_shown').add(event['EventId'])

                                logical_resource_id = event['LogicalResourceId']

                                if 'AWS::CloudFormation::Stack' == event['ResourceType'] and \
                                   event['StackId'] == phResId:
                                    logical_resource_id = stack_data[stack_id]['stack_name']

                                print(' / '.join((
                                    event['Timestamp'].strftime('%H:%m:%S'),
                                    self._trunc(stack_data[stack_id]['stack_name'], 16),
                                    self._trunc(logical_resource_id, 24),
                                    event['ResourceType'].replace('AWS::', '').ljust(30),
                                    event['ResourceStatus'].ljust(28),
                                    event.get('ResourceStatusReason', ''),
                                )))

                                if 'AWS::CloudFormation::Stack' == event['ResourceType'] and \
                                   event['ResourceStatus'] in STATUS_CF_RUN_COMPLETE:
                                    print('Stopping events printing on status {}'.format(
                                        event['ResourceStatus']
                                    ))
                                    stacks_running = stacks_running + 1
                except botocore.exceptions.ClientError as err:
                    err_msg = err.response['Error']['Message']
                    err_code = err.response['Error']['Code']
                    if err_msg == 'Rate exceeded' and err_code == 'Throttling':
                        print('Rate exceeded. Forcing timeout.')
                        time.sleep(1)
                    else:
                        print('Msg: {}, Code: {}'.format(err_msg, err_code))
                        raise Exception(err)
