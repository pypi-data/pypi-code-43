import json
import logging
import multiprocessing
import os
import sys
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import boto3
import click
from botocore.exceptions import ClientError
from parallelpipe import stage


LOGGER = logging.getLogger("tileputty")
CORES = multiprocessing.cpu_count()
EXPIRES = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=365 * 10 + 2)
MVT_META = {
    "ContentType": "application/x-protobuf",
    "ContentEncoding": "gzip",
    "Expires": datetime.strftime(EXPIRES, "%a, %d-%b-%Y %H:%M:%S %Z"),
}
PNG_META = {
    "ContentType": "image/png",
    "Expires": datetime.strftime(EXPIRES, "%a, %d-%b-%Y %H:%M:%S %Z"),
}
JPG_META = {
    "ContentType": "image/jpeg",
    "Expires": datetime.strftime(EXPIRES, "%a, %d-%b-%Y %H:%M:%S %Z"),
}
JSON_META = {"ContentType": "application/json"}

S3 = boto3.client(
    "s3"
)  # TODO: figure out if there is a better way to pool connections -> one per process


@click.command()
@click.option("--bucket", default="gfw-tiles", help="AWS Bucket")
@click.option("--layer", help="Dataset Name")
@click.option("--version", help="Dataset Version ID")
@click.option("--option", default="default", help="Dataset Version ID")
@click.option("--ext", default="mvt", help="Tile Cache format")
@click.option(
    "--update_latest",
    is_flag=True,
    help="Update latest file in root folder with latest version number",
)
@click.argument("tile_cache")
def cli(tile_cache, layer, version, bucket, option, ext, update_latest):
    """ TILE_CACHE: path to local tile cache """

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)-4s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    LOGGER.addHandler(handler)

    upload_tiles(tile_cache, bucket, layer, version, option, ext, update_latest)


def upload_tiles(
    tile_cache,
    layer,
    version,
    bucket="gfw-tiles",
    option="default",
    ext="mvt",
    update_latest=False,
):
    """
    :param tile_cache: Path to local tile cache
    :param layer: Layer name
    :param version: Layer version number
    :param bucket: AWS S3 bucket name (default: gfw-tiles)
    :param option: Layer option (default: default)
    :param ext: Tile cache format (default: mvt)
    :param update_latest: Update latest file in tile cache root (default: False)
    :return: None
    """

    files = (
        os.path.join(root, f).replace("\\", "/")
        for (root, dirs, files) in os.walk(tile_cache)
        for f in files
    )

    LOGGER.info(
        "Upload tile cache to {}/{}/{} using {} processes".format(
            layer, version, option, CORES
        )
    )

    pipe = files | _stage_copy(tile_cache, bucket, layer, version, option, ext)

    for output in pipe.results():
        LOGGER.debug(output)

    if update_latest:
        _latest(bucket, layer, version)


@stage(workers=CORES)
def _stage_copy(files, bucket, tile_cache, layer, version, option, ext):
    for f in files:

        file_name = os.path.basename(f)
        prefix = ext + os.path.dirname(f).replace(tile_cache, "")
        basename, extension = os.path.splitext(file_name)

        if extension == ".pbf" or extension == ".mvt":
            fname = basename
            args = MVT_META
        elif extension == ".png":
            fname = basename
            args = PNG_META
        elif extension == ".jpg":
            fname = basename
            args = JPG_META
        elif extension == ".json":
            fname = file_name
            args = JSON_META
        else:
            fname = file_name
            args = {}

        s3_path = "{}/{}/{}/{}/{}".format(layer, version, option, prefix, fname)
        S3.upload_file(f, bucket, s3_path, ExtraArgs=args)
        yield s3_path


def _latest(bucket, layer, version):

    s3 = boto3.resource("s3")

    try:
        obj = s3.Object(bucket, "latest")
        latest = json.loads(obj.get()["Body"].read().decode("utf-8"))
    except ClientError as ex:
        if (
            ex.response["Error"]["Code"] == "NoSuchKey"
            or ex.response["Error"]["Code"] == "SSLError"
        ):
            LOGGER.warning("No latest object found - returning empty")
            latest = dict()
        else:
            raise ex

    updated = False
    for layer in latest:
        if layer["name"] == layer:
            layer["latest_version"] = version
            updated = True
            break

    if not updated:
        latest.append({"name": layer, "latest_version": version})

    S3.put_object(
        Body=json.dumps(latest),
        Bucket=bucket,
        ContentType="application/json",
        Key="latest",
    )


if __name__ == "__main__":
    cli()
