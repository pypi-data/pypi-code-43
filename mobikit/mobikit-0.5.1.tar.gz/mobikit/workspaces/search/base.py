#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import json
import requests
from mobikit.config import config
from mobikit.utils import token_required
from mobikit.exceptions import AuthException, MobikitException
from mobikit.workspaces.base import FeedRef


@token_required
def search(keywords=None):
    """
    Function to allow a user to search for their workspaces with keywords.

    Parameters
    ----------
    keywords : str
        String of keywords

    Returns
    -------
    search_results : list<object>
    a list of workspaces
    """
    if not keywords:
        keywords = ""
    if not isinstance(keywords, str):
        raise MobikitException("pass in a string for keywords")
    headers = {"Authorization": "Token " + config.api_token}
    query_string = {"query": keywords, "page_size": 100}
    try:
        f = requests.get(config.feed_route, headers=headers, params=query_string)
        f.raise_for_status()
        search_results = []
        for feed_result in json.loads(f.content):
            feed = FeedRef.create(feed_result["id"])
            feed.load(meta_only=True)
            search_results.append(
                {
                    "workspace_id": feed.id,
                    "workspace_name": feed.name,
                    "feeds": list(feed.sources.keys()),
                }
            )
        config.logger.info(
            "your search yielded the following feeds: " + str(search_results)
        )
        return search_results
    except requests.exceptions.HTTPError as e:
        config.logger.exception(e)
        response_status = e.response.content if e.response is not None else "unknown"
        raise MobikitException(
            f"Recieved invalid response status code {response_status}."
        ) from e
    except requests.exceptions.RequestException as e:
        config.logger.exception(e)
        raise MobikitException(f"Error retrieving search results.") from e
