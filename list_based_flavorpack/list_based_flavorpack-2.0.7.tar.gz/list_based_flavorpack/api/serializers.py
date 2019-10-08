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

from rest_framework import serializers as rf_serializers
from serialbox.api.serializers import RegionSerializer
from list_based_flavorpack import models



##
# These fields will be added to the pool serializer automatically since
# they are specified in the pool_slug_fields and the pool_hyperlinked_fields
# values in the words_flavorpack.apps.WordsFlavorpackConfig module.
##
listbasedregion_set = rf_serializers.SlugRelatedField(
    many=True,
    queryset=models.ListBasedRegion.objects.all(),
    slug_field='machine_name',
    required=False
)

listbasedregion_hyperlink_set = rf_serializers.HyperlinkedRelatedField(
    many=True,
    read_only=True,
    view_name='list-based-region',
    lookup_field='machine_name',
)



class ProcessingParametersSerializer(rf_serializers.ModelSerializer):
    '''
    Default serializer for Processing Parameters
    '''
    id = rf_serializers.IntegerField(write_only=False)
    
    class Meta:
        model = models.ProcessingParameters
        fields = ('id', 'key', 'value', 'list_based_region',)


class ListBasedRegionSerializer(RegionSerializer):
    '''
    Specifies the model...
    '''
    processing_parameters = ProcessingParametersSerializer(many=True, read_only=False)
    
    class Meta(object):
        model = models.ListBasedRegion
        fields = ('id', 'pool', 'created_date', 'modified_date', 'readable_name',
                  'machine_name', 'active', 'order', 'last_number_line',
                  'number_replenishment_size', 'directory_path',
                  'processing_class_path', 'end_point', 'rule', 'authentication_info',
                  'template', 'processing_parameters')

    def create(self, validated_data):
        '''
        Creates a list-based region and its processing params.
        '''
        processing_parameters = validated_data.pop("processing_parameters")
        region = models.ListBasedRegion.objects.create(**validated_data)
        for processing_parameter in processing_parameters:
            models.ProcessingParameters.objects.create(list_based_region=region, **processing_parameter)
        return region
    
    def update(self, instance, validated_data):
        '''
        Creates a list-based region and its processing params.
        '''
        processing_parameters = validated_data.pop("processing_parameters")
        super(ListBasedRegionSerializer, self).update(instance, validated_data)
        posted_ids = set(param.get('id', None) for param in processing_parameters)
        existing_params = set(models.ProcessingParameters.objects.filter(list_based_region=instance).values_list('id', flat=True))
        ids_for_removal = existing_params - posted_ids
        objects_for_removal = models.ProcessingParameters.objects.filter(list_based_region=instance, pk__in=ids_for_removal)
        objects_for_removal.delete()
        for processing_parameter in processing_parameters:
            id = processing_parameter.get('id', None)
            if id:
                item = models.ProcessingParameters.objects.get(id=id)
                item.key = processing_parameter.get('key', item.key)
                item.value = processing_parameter.get('value', item.value)
                item.save()
            else:
                models.ProcessingParameters.objects.create(list_based_region=instance, **processing_parameter)
        return instance

class HyperlinkedListBasedRegionSerializer(ListBasedRegionSerializer):
    '''
    Addst the hyperlinked field...
    '''
    pool = rf_serializers.HyperlinkedRelatedField(view_name='pool-detail',
                                                  read_only=True,
                                                  lookup_field='machine_name')
