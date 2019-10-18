import os

from botocore.exceptions import ClientError
import click
import zipfile as zf


def _zipdir(path, zipf):
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(
                os.path.join(root, file),
                os.path.relpath(
                    os.path.join(root, file), os.path.join(path, '.')))


def make_zip(zipfile, dist_dir, additional_files):
    zipf = zf.ZipFile(zipfile, 'w', zf.ZIP_DEFLATED)
    _zipdir(dist_dir, zipf)
    for file in additional_files:
        zipf.write(file)
    zipf.close()


def _upload_file(client, file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    try:
        response = client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        click.echo(e)
        click.echo(response)
        return False
    return True
