from tools.models import LoanCollateralType
from master.serializers import BaseInfoSerializer

class LoanCollateralTypeSerializer(BaseInfoSerializer):

    class Meta(BaseInfoSerializer.Meta):
        model = LoanCollateralType
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")
      return LoanCollateralType.objects.using(db_name).create(**validated_data)
