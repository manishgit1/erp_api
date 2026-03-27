from django.db import models
from master.models import GenericIdEntity

class RequestWorkflow(GenericIdEntity):
    initiator_role = models.ForeignKey('user_auth.UserRole', on_delete=models.CASCADE,related_name='+')
    follower_role = models.ForeignKey('user_auth.UserRole', on_delete=models.CASCADE,related_name='+')
    is_active = models.BooleanField(default=True)
    is_void = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "request_workflow"
        managed = False
