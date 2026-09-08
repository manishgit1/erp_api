from rest_framework import serializers
from tools.models import RegistrationAuthority
from master.serializers import BaseInfoSerializer

class RegistrationAuthoritySerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = RegistrationAuthority
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return RegistrationAuthority.objects.using(db_name).create(**validated_data)

