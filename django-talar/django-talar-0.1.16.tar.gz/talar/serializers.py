from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    external_id = serializers.CharField(max_length=255)
    amount = serializers.CharField(max_length=255)
    currency = serializers.CharField(max_length=255)
    continue_url = serializers.CharField(max_length=255)
    provider_code = serializers.CharField(max_length=255, required=False,
                                          allow_blank=True)


class NotifySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=256)
    timestamp = serializers.DateTimeField()
    payload = serializers.JSONField()
