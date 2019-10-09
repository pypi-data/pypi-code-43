from paynlsdk.objects import Error


class ResponseBase(object):
    """
    Response base object for the any API call

    :param paynlsdk.objects.Error request: generic API result used to communicate about the status of the call.
        If the call itself failed, this will also contain an error id and message
    """

    def __init__(self, request: Error=None, *args, **kwargs):
        self.request = request
        return

    def is_error(self):
        return self.request is not None and not self.request.result

