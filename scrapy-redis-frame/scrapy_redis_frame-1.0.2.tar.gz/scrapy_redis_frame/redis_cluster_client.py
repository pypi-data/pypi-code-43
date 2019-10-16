from rediscluster import RedisCluster


def get_redis_cluster(**kwargs):
    return RedisCluster(startup_nodes=kwargs.pop('host_list'), decode_responses=False, password=kwargs.pop('password'))
