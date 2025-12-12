from tools.models import DocumentType
from master.serializers import BaseInfoSerializer

class DocumentTypeSerializer(BaseInfoSerializer):
   
    class Meta(BaseInfoSerializer.Meta):
        model = DocumentType
        fields = BaseInfoSerializer.Meta.fields

    def create(self, validated_data):
      db_name = self.context.get("db_name")   
      return DocumentType.objects.using(db_name).create(**validated_data)

