from rest_framework import serializers
from tools.models import LeadSource


class LeadSourceSerializer(serializers.ModelSerializer):
    referenceId = serializers.ReadOnlyField(source="reference_id")
    name = serializers.CharField(required=True) 
    nameInNepali = serializers.CharField(source="name_in_nepali", required=False, allow_blank=True, allow_null=True)
    remarks = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    remarksInNepali = serializers.CharField(source="remarks_in_nepali", required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = LeadSource
        fields = [
            "referenceId",
            "name",
            "nameInNepali",
            "remarks",
            "remarksInNepali"
        ]

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return LeadSource.objects.using(db_name).create(**validated_data)

