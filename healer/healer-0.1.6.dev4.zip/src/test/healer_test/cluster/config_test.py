
from healer.cluster.config import *


def test_cluster_local_bind():
    print()
    perform_local_bind = ClusterConfig.cluster_local_bind()
    print(perform_local_bind)
