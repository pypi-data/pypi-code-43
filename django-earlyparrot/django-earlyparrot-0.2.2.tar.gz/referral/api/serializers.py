from rest_framework import serializers

from ..models import Campaign


class CampaignSerializer(serializers.ModelSerializer):
    campaignId = serializers.CharField(source='campaign_id')
    token = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = ['name', 'campaignId', 'token']

    def get_token(self, obj):
        return obj.subscriber_set.get(user=self.context.get('request').user).token


class CampaignSubscribeSerializer(serializers.Serializer):
    rh = serializers.CharField(required=True)
    conversion = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        user_from = validated_data.get('user_from')
        rh = validated_data.get('rh')
        conversion = validated_data.get('conversion', False)

        instance.subscribe(user_from, rh, conversion)

        return validated_data
