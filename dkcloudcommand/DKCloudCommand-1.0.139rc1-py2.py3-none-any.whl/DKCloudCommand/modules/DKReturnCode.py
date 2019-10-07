import six


# coalesce all errors from using the DataKitchen API into one simple structure
class DKReturnCode:
    DK_SUCCESS = 'success'  # value
    DK_FAIL = 'fail'  # value

    def __init__(self):
        self._status = None
        self._message = ''
        self._payload = None

    def set(self, status, message, payload=None):
        if status != self.DK_SUCCESS and status != self.DK_FAIL:
            raise ValueError('DKReturnCode.set() invalid value for status: %s' % status)
        self._status = status
        self.set_message(message)
        self._payload = payload

    def ok(self):
        return self._status == self.DK_SUCCESS

    def get_message(self):
        return self._message

    def get_payload(self):
        return self._payload

    def set_message(self, msg):
        self._message = msg if msg is not None else ''

    def __str__(self):
        return "DKReturnCode {status: %s,\n message: %s,\n payload: %s}" % (
            self._status, self._message, self._payload
        )


# wrap the error returned from the DataKitchen API
class DKAPIReturnCode:

    def __init__(self, rdict, response=None):
        if isinstance(rdict, dict) is True and 'message' in rdict:
            self.rd = rdict
        else:
            self.rd = None
        self.response = response

    # put all the logic here to dig out the error message from the API call
    def get_message(self):
        # got an rdict, look in there
        if self.rd is not None and isinstance(self.rd, dict):
            if 'message' in self.rd:
                contents = self.rd['message']
                if isinstance(contents, dict) and 'error' in contents:
                    ret = contents['error']
                    if 'issues' in contents:
                        if contents['issues'] is not None:
                            for issue in contents['issues']:
                                issueMessage = '\n%s - %s - %s' % (
                                    issue['severity'], issue['file'], issue['description']
                                )
                                ret += issueMessage
                    return ret
                elif isinstance(contents, six.string_types):
                    return contents
                else:
                    return 'TODO: figure out this case'
        # no rdict, just have the HTTP response
        if self.response is not None:
            if isinstance(self.response.text, six.string_types):
                return self.response.text
        return ''


'''
The rdict varies.  Here are some examples

{
u'status': 500,
u'message': u'Internal Server Error'
}

{
  u'message': {
    u'status': u'failed',
    u'error': u'unable to delete a branched-from-base-test-kitchen_ut_gil kitchen '
  }
}
'''
