# -*- coding:utf-8 -*-

from ..util import client, util, config, result_cache
from terminal import bold, magenta, white, blue, green, red, yellow, confirm


def delete(clusterId, groupName, instanceId, yes=False):
    arr = instanceId.split(',')

    clusterId = result_cache.get(clusterId, 'clusters')
    groupName = result_cache.get(groupName, 'groups')

    # instanceId = result_cache.get(instanceId, 'cluster_instances', True)

    t = util.parse_id_arr(arr, 'cluster_instances', True)


    if yes:
        __batch_action(clusterId, groupName, t)
    else:
        try:
            if confirm("Delete all these cluster instances:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                __batch_action(clusterId, groupName, t)
        except KeyboardInterrupt:
            print('')
            return


def __batch_action(clusterId, groupName, arr):
    for item in arr:
        __delete_cluster_instances(clusterId, groupName, item)


def __delete_cluster_instances(clusterId, groupName, instanceId):
    print(white('exec: bcs delete_cluster_instances %s %s %s' % (clusterId, groupName, instanceId)))
    client.delete_cluster_instance(clusterId, groupName, instanceId)
    print(green('done'))
