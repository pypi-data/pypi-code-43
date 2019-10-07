#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import pandas as pd
import json
import os
import requests
import logging
from mobikit.config import config
from mobikit.exceptions import AuthException
from mobikit.utils import token_required
from mobikit.workspaces.base import FeedRef
from mobikit.exceptions import MobikitException


def add_data_source(dataframe, source_id, source_name):
    return add_data_feed(dataframe, source_id, source_name)


@token_required
def add_data_feed(dataframe, feed_id, feed_name):
    """
    Adds a feed to the workspace from a local data feed. Must be a
    pandas DataFrame.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame containing data
    feed_id : str, int
        String containing the feed id
    feed_name : str
        Name of source

    Returns
    -------
    None : None
    """
    logging.warn("This function is temporarily unavailable.")
    return

    headers = {"Authorization": "Token {}".format(config.api_token)}
    try:
        if not (isinstance(dataframe, pd.DataFrame) and _validate_feed_id(feed_id)):
            raise MobikitException("please pass in a dataframe and a valid feed_id")

        if dataframe.memory_usage(index=True).sum() >= config.upload_size_limit:
            raise MobikitException("dataframe too big! must be <250mb")

        # upload resource to s3
        resource_url = _upload_file(headers, dataframe)

        # add source to feed
        _add_source_to_feed(headers, feed_id, resource_url, feed_name)

        # check that source was added correctly
        _validate_source(headers, "derived_data", resource_url)
        config.logger.info("success! added source to datafeed: " + str(feed_id))

    except Exception as e:
        config.logger.exception(e)
        raise MobikitException("Error adding data source.") from e


# method to confirm that the feed id passed is valid
def _validate_feed_id(feed_id):
    FeedRef.create(feed_id).load(meta_only=True)
    return True


def _upload_file(headers, dataframe):
    try:
        os.makedirs("cache/", exist_ok=True)
        dataframe.to_csv("cache/dummy.csv", index=False)
        with open("cache/dummy.csv", "rb") as f:
            response = requests.post(
                config.upload_route, headers=headers, files=[("file", f)]
            )
            response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        config.logger.exception(e)
    except requests.exceptions.RequestException as e:
        config.logger.exception(e)
    except Exception as e:
        config.logger.exception(e)
    finally:
        os.remove("cache/dummy.csv")
    return response.json()["resource_url"]


def _add_source_to_feed(headers, feed_id, resource_url, feed_name):
    try:
        payload = {
            "resource": resource_url,
            "cadence": "never",
            "source_type": "derived_data",
            "dataset_id": feed_id,
            "name": feed_name,
        }
        resource = requests.post(config.source_route, headers=headers, json=payload)
        resource.raise_for_status()
        return resource.content
    except requests.exceptions.HTTPError as e:
        config.logger.exception(e)
    except requests.exceptions.RequestException as err:
        config.logger.exception(err)
    except Exception as e:
        config.logger.exception(e)


# method to validate that the source was successfully created
def _validate_source(headers, resource_type, resource_url):
    try:
        payload = {"type": resource_type, "resource": resource_url}
        resource = requests.post(config.validate_route, headers=headers, data=payload)
        resource.raise_for_status()
    except requests.exceptions.HTTPError as e:
        config.logger.exception(e)
    except requests.exceptions.RequestException as err:
        config.logger.exception(err)
    except Exception as e:
        config.logger.exception(e)
