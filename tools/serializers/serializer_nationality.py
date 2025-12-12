from tools.models import Nationality
from master.serializers import BaseInfoSerializer

class NationalitySerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = Nationality
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return Nationality.objects.using(db_name).create(**validated_data)

