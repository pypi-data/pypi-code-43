'''
    Copyright 2018 SerialLab, CORP

    This file is part of ListBasedFlavorpack.

    RandomFlavorpack is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    RandomFlavorpack is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with RandomFlavorpack.  If not, see <http://www.gnu.org/licenses/>.
'''
from serialbox.api.viewsets import FormMixin
from serialbox import viewsets

from list_based_flavorpack.models import ListBasedRegion, ProcessingParameters
from list_based_flavorpack.api import serializers


class ListBasedRegionViewSet(viewsets.SerialBoxModelViewSet, FormMixin):
    queryset = ListBasedRegion.objects.all()
    lookup_field = 'machine_name'

    def get_serializer_class(self):
        '''
        Return a different serializer depending on the client request.
        '''
        ret = serializers.ListBasedRegionSerializer
        try:
            if self.request.query_params.get('related') == 'true':
                ret = serializers.HyperlinkedListBasedRegionSerializer
        except AttributeError:
            pass
        return ret


class ProcessingParametersViewSet(viewsets.SerialBoxModelViewSet, FormMixin):
    queryset = ProcessingParameters.objects.all()
    serializer_class = serializers.ProcessingParametersSerializer


    
list_based_region_list = ListBasedRegionViewSet.as_view({
    'get': 'list'
})
list_based_region_create = ListBasedRegionViewSet.as_view({
    'post': 'create'
})
list_based_region_detail = ListBasedRegionViewSet.as_view({
    'get': 'retrieve'
})
list_based_region_modify = ListBasedRegionViewSet.as_view({
    'put': 'partial_update',
    'delete': 'destroy'
})
list_based_region_form = ListBasedRegionViewSet.as_view({
    'get': 'form'
})
