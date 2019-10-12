from .base import ErConnector
import mimetypes


class Attachment(object):

    def __init__(self, attachment_id):
        self.attachment_id = attachment_id
        self.data = get_remote_attachment(attachment_id)

    def __str__(self):
        return self.attachment_id

    def fetch(self):
        self.data = get_remote_attachment(self.attachment_id)

    def fetch_content(self):
        return get_remote_attachment_content(self.attachment_id).content

    def filename(self):
        return '{Name}'.format(
            Name=self.data.get('Name', None),
        )

    def mimetype(self):
        return '{mimetype}'.format(
            mimetype=mimetypes.guess_type(self.filename())[0]
        )

def get_remote_attachment(attachment_id):
    connector = ErConnector()
    url = 'Attachment/{Id}/'.format(Id=attachment_id)
    response = connector.send_request(
        path=url
    )
    return response

def get_remote_attachment_content(attachment_id):
    connector = ErConnector()
    url = 'Attachment/Content/{Id}/'.format(Id=attachment_id)
    response = connector.send_request(
        path=url,
        rawresponse=True
    )
    # return response object.
    return response
