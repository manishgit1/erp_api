from tools.models import LoanPurpose
from master.serializers import BaseInfoSerializer

class LoanPurposeCodeSerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = LoanPurpose
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return LoanPurpose.objects.using(db_name).create(**validated_data)

