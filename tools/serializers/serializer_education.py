from tools.models import Education
from master.serializers import BaseInfoSerializer

class EducationSerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = Education
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return Education.objects.using(db_name).create(**validated_data)

