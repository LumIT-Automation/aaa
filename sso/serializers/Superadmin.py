from rest_framework import serializers


class SuperadminSerializer(serializers.Serializer):
    class SuperadminInnerSerializer(serializers.Serializer):
        items = serializers.ListField(
            child=serializers.CharField(max_length=64), required=False
        )

    data = SuperadminInnerSerializer(required=True)


