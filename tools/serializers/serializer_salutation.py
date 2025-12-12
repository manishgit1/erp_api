from tools.models import Salutation
from master.serializers import BaseInfoSerializer

class SalutationSerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = Salutation
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return Salutation.objects.using(db_name).create(**validated_data)

