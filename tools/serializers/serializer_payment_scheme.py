from tools.models import LoanPaymentScheme
from master.serializers import BaseInfoSerializer

class PaymentSchemeSerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = LoanPaymentScheme
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return LoanPaymentScheme.objects.using(db_name).create(**validated_data)

