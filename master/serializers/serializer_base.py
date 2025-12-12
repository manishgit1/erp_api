from rest_framework import serializers

class BaseInfoSerializer(serializers.Serializer):
    referenceId = serializers.ReadOnlyField(source="reference_id")
    name = serializers.CharField(max_length=255)
    # nameInNepali = serializers.CharField(max_length=255, required=False, allow_blank=True)
    remarks = serializers.CharField(max_length=500, required=False, allow_blank=True)
    # remarksInNepali = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    class Meta:
        fields = [
            "referenceId",
            "name",
            "nameInNepali",
            "remarks",
            "remarksInNepali"
        ]