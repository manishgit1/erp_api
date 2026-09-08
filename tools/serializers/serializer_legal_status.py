from tools.models import LegalStatus
from master.serializers import BaseInfoSerializer

class LegalStatusSerializer(BaseInfoSerializer):

    class Meta(BaseInfoSerializer.Meta):
        model = LegalStatus
        fields = BaseInfoSerializer.Meta.fields
