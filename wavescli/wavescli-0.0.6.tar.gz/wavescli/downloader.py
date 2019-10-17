import os
import urllib.parse
import urllib.request

from wavescli import awsadapter


def get_file(remote_uri, local_target_dir, basename=None):

    if remote_uri.startswith('s3://'):
        return awsadapter.get_file(remote_uri, local_target_dir, basename)

    elif remote_uri.startswith('http://') or remote_uri.startswith('https://'):

        if not basename:
            schema = urllib.parse.urlparse(remote_uri)
            basename = os.path.basename(schema.path)

        target_path = os.path.join(local_target_dir, basename)

        response = urllib.request.urlopen(remote_uri)
        with open(target_path, 'wb') as localfile:
            localfile.write(response.read())
        return target_path
    else:
        raise RuntimeError("Couldn't download the URL: {}".format(repr(remote_uri)))
