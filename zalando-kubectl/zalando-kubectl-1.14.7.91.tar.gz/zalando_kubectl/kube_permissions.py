import requests

_ZACK_ROLE_DOCS = "https://cloud.docs.zalando.net/reference/zack-access-roles/"


def check_cluster_permissions(cluster_url, cluster_alias, token):
    """Checks the cluster permissions of a user"""

    response = requests.post('{}/apis/authorization.k8s.io/v1/selfsubjectaccessreviews'.format(cluster_url),
                             json={"kind": "SelfSubjectAccessReview",
                                   "apiVersion": "authorization.k8s.io/v1",
                                   "spec": {"resourceAttributes": {
                                        "namespace": "default",
                                        "verb": "get",
                                        "resource": "pods"
                                       }
                                     }
                                   },
                             headers={'Authorization': 'Bearer {}'.format(token)}, timeout=20)
    response.raise_for_status()
    data = response.json()
    if not data["status"]["allowed"]:
        raise ValueError('No role found for cluster "{}".\nPlease request a ZACK role, see "{}".'
                         .format(cluster_alias, _ZACK_ROLE_DOCS))
