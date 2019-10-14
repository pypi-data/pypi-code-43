# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._restclient.service_context import ServiceContext


class HybridServiceContext(ServiceContext):

    def __init__(self,
                 subscription_id, resource_group_name, workspace_name, workspace_id,
                 authentication, region, **kwargs):
        self._region = region
        super(HybridServiceContext, self).__init__(subscription_id, resource_group_name,
                                                   workspace_name, workspace_id,
                                                   authentication, **kwargs)

    def _fetch_endpoints(self):
        return {'history': 'https://{}'.format(self._region)}
