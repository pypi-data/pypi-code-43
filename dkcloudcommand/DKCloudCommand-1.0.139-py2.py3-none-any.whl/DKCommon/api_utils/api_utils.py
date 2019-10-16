import os
import six


def validate_and_get_response(response):
    base_error_message = 'Call to backend failed.'
    reason_message = 'Unknown reason.'

    if response is None:
        raise Exception('%s\n%s\n' % (base_error_message, 'Response was null.'))

    rdict = get_json_response(response)
    if rdict is None:
        raise Exception('%s\n' % 'Response was an invalid format')

    if response.status_code == 200 or response.status_code == 201:
        if isinstance(rdict, dict):
            if 'status' in rdict and rdict['status'] != 'success':
                reason_message = 'Status is not success'
                if 'error' in rdict:
                    reason_message = rdict['error']
                raise Exception('%s\n' % reason_message)
        return rdict

    elif response.status_code == 400:
        if isinstance(rdict, dict) and 'message' in rdict:
            if 'status' in rdict['message'] and rdict['message']['status'] != 'success':
                reason_message = 'Status is not success'
                if 'error' in rdict['message']:
                    reason_message = rdict['message']['error']
                reason_message += get_issue_messages(rdict['message'])
                raise Exception('%s\n' % reason_message)

    elif response.status_code == 403:
        reason_message = 'Permission Denied'
        if response.text is not None:
            message = response.json().get('message')
            if message is not None:
                reason_message = message.get('error')
                raise Exception('%s\n' % reason_message)
    elif response.status_code == 412 or response.status_code == 417:
        msg_json = response.json()
        reason_message = msg_json['message']['error']['message']
        detail = msg_json['message']['error'].get('detail')
        if detail:
            if isinstance(detail, six.string_types) or isinstance(detail, six.text_type):
                reason_message += '%s%s' % (os.linesep, str(detail))
            if isinstance(detail, list):
                reason_message += '%s%s' % (os.linesep, get_issue_messages(detail))

    elif response.status_code == 502:
        reason_message = 'Server could not make a dependent connection (Code 502).'

    elif response.status_code == 504:
        reason_message = 'Server timeout (Code 504).'

    else:
        reason_message = '%s (Code %s)' % (str(response.text), response.status_code)

    raise Exception('%s\n%s\n' % (base_error_message, reason_message))


def get_json_response(response):
    if response is None or response.text is None:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def get_issue_messages(param):
    issue_messages = ''
    issues = list()

    if isinstance(param, dict) and 'issues' in param:
        issues = param['issues']

    if isinstance(param, list):
        issues = param

    for issue in issues:
        issue_messages += '\n'
        if 'severity' in issue:
            issue_messages += 'Severity: %s\n' % issue['severity']
        if 'file' in issue:
            issue_messages += 'File: %s\n' % issue['file']
        if 'description' in issue:
            issue_messages += 'Description: %s\n' % issue['description']
        issue_messages += '\n'
    return issue_messages
