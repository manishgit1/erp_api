from rest_framework import serializers
from loan.models.models_request_workflow import RequestWorkflow
from user_auth.models import UserRole

class RequestWorkflowSerializer(serializers.ModelSerializer):
    fromRoleId = serializers.SlugRelatedField(
        slug_field='reference_id',
        queryset=UserRole.objects.all(),
        source='initiator_role'
    )
    toRoleId = serializers.SlugRelatedField(
        slug_field='reference_id',
        queryset=UserRole.objects.all(),
        source='follower_role'
    )

    fromRoleName = serializers.CharField(source='initiator_role.name',read_only=True)
    toRoleName = serializers.CharField(source='follower_role.name',read_only=True)
    referenceId = serializers.CharField(source='reference_id', read_only=True)
    workflowName = serializers.SerializerMethodField()

    isActive = serializers.BooleanField(source='is_active', read_only=True)

    class Meta:
        model = RequestWorkflow
        fields = ['referenceId', 'workflowName', 'fromRoleId', 'toRoleId', 'fromRoleName', 'toRoleName','isActive', 'remarks']

    def get_workflowName(self, obj):
        from_name = obj.initiator_role.name if obj.initiator_role else ''
        to_name = obj.follower_role.name if obj.follower_role else ''
        return f"{from_name} to {to_name}"
