#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

from mobikit.config import config
from mobikit.workspaces.exceptions import FeedTypeException
from mobikit.utils import token_required
from mobikit.workspaces.base import FeedRef, Queryable


@token_required
def load(
    workspace_id,
    feed_name=None,
    source_name=None,
    query=None,
    feed_names=None,
    source_names=None,
    queries=None,
    as_dict=True,
):
    """
    Allows user to load/query any number of feeds from a workspace.

    If the request is very large, the result will be downsized and a warning will be issued to the user

    Parameters
    ----------
    workspace_id : int
        Id of the workspace whose feeds you with to load. A workspace consists of multiple feeds.
    feed_names : list of str
        List of feed names to load data from.
    queries : dict
        Dict mapping feed names (str) to queries (mobikit.workspaces.Query).
    as_dict : boolean
        Whether the loaded dfs should be returned as dict or list.
    feed_name : str
        String containing the name of a single feed to query.
    query : mobikit.workspaces.Query
        A query to be run on the single feed specified with `feed_name`.

    Returns
    -------
    dataframe(s) : pandas.DataFrame or dict or list
        If feed_name is used to specify a single feed to load, will return a single pandas.DataFrame.
        Otherwise, will return either a dict of the form {feed_name: pandas.DataFrame}
        or a list of pandas.DataFrame, depending on the value of `as_dict`.
    """
    feed_names = feed_names or source_names or set()
    feed_name = feed_name or source_name
    queries = queries or dict()
    if feed_name:
        feed_names.add(feed_name)
        queries[feed_name] = queries.get(feed_name, None) or query

    feed = FeedRef.create(workspace_id)
    feed.load()
    if not len(feed_names):
        feed_names = set(feed.sources.keys())

    feed_dfs = {}
    for s in feed_names:
        feed_query = queries.get(s, None)
        if feed_query and isinstance(feed.get_source(s), Queryable):
            feed.sources[s].query(feed_query)
        elif feed_query:
            raise FeedTypeException(f"{s} is not queryable.")
        else:
            feed.get_source(s).load()
        feed_dfs[s] = feed.get_source(s).to_df()
    config.logger.info(f"returned {len(list(feed_dfs.keys()))} dataframes")
    if feed_name:
        return feed_dfs[feed_name]
    return feed_dfs if as_dict else list(feed_dfs.values())
