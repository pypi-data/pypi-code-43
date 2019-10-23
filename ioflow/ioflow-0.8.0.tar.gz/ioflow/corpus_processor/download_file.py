import os
import tempfile

import requests

import cgi
import zipfile


def download_file(url, filename=None, **kwargs):
    """
    code learned from https://stackoverflow.com/a/16696317/1979770
    """
    # create a temp file if filename is not given
    if not filename:
        filename = os.path.join(tempfile.mkdtemp(), 'corpus.data')

    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, **kwargs) as r:
        local_filename = filename
        r.raise_for_status()
        # _, params = cgi.parse_header(r.headers)
        _, params = cgi.parse_header(r.headers['Content-Disposition'])
        server_filename = params['filename']
        if 'zip' == os.path.splitext(server_filename)[-1][1:]:
            local_filename = os.path.join(os.path.dirname(filename), server_filename)
        with open(local_filename, 'wb') as f:
            chunk_size = 1 << 10  # e.g. 1024
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
        if 'zip' == os.path.splitext(server_filename)[-1][1:]:
            with zipfile.ZipFile(local_filename, 'r') as zfile:
                zfile.filelist[0].filename = 'corpus.data'
                zfile.extract(zfile.filelist[0], os.path.dirname(filename))
    return filename


if __name__ == "__main__":
    # download_file("http://10.43.13.20:25005/hdfs/download", filename='download.txt', json={"trainId": "5d01cc3bb775fa16367a2f85"})
    result = download_file("http://10.43.17.53:25005/hdfs/download", params={"trainId": "5d7756e92bcc282cb854db3e"})

    print(result)
