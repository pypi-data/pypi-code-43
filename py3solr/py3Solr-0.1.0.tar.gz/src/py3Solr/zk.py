#!win10_x64 python3.6
# coding: utf-8
# Date: 2019/10/27
# wbq813@foxmail.com
import logging
import json
import random

from .solr_error import SolrError

try:
    from kazoo.client import KazooClient, KazooState
except ImportError:
    KazooClient = KazooState = None

logger = logging.getLogger(__name__)


class ZooKeeper(object):
    # Constants used by the REST API:
    LIVE_NODES_ZKNODE = "/live_nodes"
    ALIASES = "/aliases.json"
    CLUSTER_STATE = "/clusterstate.json"
    COLLECTION_STATUS = "/collections"
    COLLECTION_STATE = "/collections/%s/state.json"
    SHARDS = "shards"
    REPLICAS = "replicas"
    STATE = "state"
    ACTIVE = "active"
    LEADER = "leader"
    BASE_URL = "base_url"
    TRUE = "true"
    FALSE = "false"
    COLLECTION = "collection"

    def __init__(self, zkServerAddress, timeout=15, max_retries=-1, kazoo_client=None):
        if KazooClient is None:
            logging.error("ZooKeeper requires the `kazoo` library to be installed")
            raise RuntimeError

        self.collections = {}
        self.liveNodes = {}
        self.aliases = {}
        self.state = None

        if kazoo_client is None:
            self.zk = KazooClient(
                zkServerAddress,
                read_only=True,
                timeout=timeout,
                command_retry={"max_tries": max_retries},
                connection_retry={"max_tries": max_retries},
            )
        else:
            self.zk = kazoo_client

        self.zk.start()

        def connectionListener(state):
            if state == KazooState.LOST:
                self.state = state
            elif state == KazooState.SUSPENDED:
                self.state = state

        self.zk.add_listener(connectionListener)

        @self.zk.DataWatch(ZooKeeper.CLUSTER_STATE)
        def watchClusterState(data, *args, **kwargs):
            if not data:
                logger.warning("No cluster state available: no collections defined?")
            else:
                self.collections = json.loads(data.decode("utf-8"))
                logger.info("Updated collections: %s", self.collections)

        @self.zk.ChildrenWatch(ZooKeeper.LIVE_NODES_ZKNODE)
        def watchLiveNodes(children):
            self.liveNodes = children
            logger.info("Updated live nodes: %s", children)

        @self.zk.DataWatch(ZooKeeper.ALIASES)
        def watchAliases(data, stat):
            if data:
                json_data = json.loads(data.decode("utf-8"))
                if ZooKeeper.COLLECTION in json_data:
                    self.aliases = json_data[ZooKeeper.COLLECTION]
                else:
                    logger.warning(
                        "Expected to find %s in alias update %s",
                        ZooKeeper.COLLECTION,
                        json_data.keys(),
                    )
            else:
                self.aliases = None
            logger.info("Updated aliases: %s", self.aliases)

        def watchCollectionState(data, *args, **kwargs):
            if not data:
                logger.warning("No cluster state available: no collections defined?")
            else:
                self.collections.update(json.loads(data.decode("utf-8")))
                logger.info("Updated collections: %s", self.collections)

        @self.zk.ChildrenWatch(ZooKeeper.COLLECTION_STATUS)
        def watchCollectionStatus(children):
            logger.info("Updated collection: %s", children)
            for c in children:
                self.zk.DataWatch(self.COLLECTION_STATE % c, watchCollectionState)

    def getHosts(self, collname, only_leader=False, seen_aliases=None):
        if self.aliases and collname in self.aliases:
            return self.getAliasHosts(collname, only_leader, seen_aliases)

        hosts = []
        if collname not in self.collections:
            raise SolrError("Unknown collection: %s" % collname)
        collection = self.collections[collname]
        shards = collection[ZooKeeper.SHARDS]
        for shardname in shards.keys():
            shard = shards[shardname]
            if shard[ZooKeeper.STATE] == ZooKeeper.ACTIVE:
                replicas = shard[ZooKeeper.REPLICAS]
                for replicaname in replicas.keys():
                    replica = replicas[replicaname]

                    if replica[ZooKeeper.STATE] == ZooKeeper.ACTIVE:
                        if not only_leader or (
                                replica.get(ZooKeeper.LEADER, None) == ZooKeeper.TRUE
                        ):
                            base_url = replica[ZooKeeper.BASE_URL]
                            if base_url not in hosts:
                                hosts.append(base_url)
        return hosts

    def getAliasHosts(self, collname, only_leader, seen_aliases):
        if seen_aliases:
            if collname in seen_aliases:
                logger.warning("%s in circular alias definition - ignored", collname)
                return []
        else:
            seen_aliases = []
        seen_aliases.append(collname)
        collections = self.aliases[collname].split(",")
        hosts = []
        for collection in collections:
            for host in self.getHosts(collection, only_leader, seen_aliases):
                if host not in hosts:
                    hosts.append(host)
        return hosts

    def getRandomURL(self, collname, only_leader=False):
        hosts = self.getHosts(collname, only_leader=only_leader)
        if not hosts:
            raise SolrError("ZooKeeper returned no active shards!")
        return "%s/%s" % (random.choice(hosts), collname)  # NOQA: B311

    def getLeaderURL(self, collname):
        return self.getRandomURL(collname, only_leader=True)
