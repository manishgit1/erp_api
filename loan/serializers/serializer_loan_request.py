from rest_framework import serializers
from loan.models import LoanRequest
from master.serializers import ClientMasterSerializer
from tools.serializers import LoanTypeSerializer

class LoanRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRequest
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_by', 'updated_at', 'is_void')

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['client'] = ClientMasterSerializer(instance.client).data
        response['loan_type'] = LoanTypeSerializer(instance.loan_type).data
        
        # Flattened fields for reports
        try:
            response['client_name'] = f"{instance.client.first_name} {instance.client.middle_name or ''} {instance.client.last_name}".replace('  ', ' ').strip()
        except AttributeError:
            response['client_name'] = ''
            
        try:
            response['loan_type_name'] = instance.loan_type.name if instance.loan_type else ''
        except AttributeError:
            response['loan_type_name'] = ''
        
        return response