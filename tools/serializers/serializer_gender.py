from rest_framework import serializers
from tools.models import ClientTypeGender
from master.serializers import BaseInfoSerializer

class GenderSerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = ClientTypeGender
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return ClientTypeGender.objects.using(db_name).create(**validated_data)

