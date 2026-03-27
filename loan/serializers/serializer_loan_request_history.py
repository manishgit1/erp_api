from rest_framework import serializers
from loan.models.models_loan_request import LoanRequestHistory

class LoanRequestHistorySerializer(serializers.ModelSerializer):
    fromRoleName = serializers.CharField(source='from_role.name', read_only=True)
    toRoleName = serializers.CharField(source='to_role.name', read_only=True)
    createdBy = serializers.CharField(source='created_by.username', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = LoanRequestHistory
        fields = ['action', 'status', 'fromRoleName', 'toRoleName', 'remarks', 'createdBy', 'createdAt']
