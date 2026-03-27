from django.db import models
from master.models import GenericIdEntity

class NomineeRelation(GenericIdEntity):
    name = models.CharField(max_length=100)
    # name_in_nepali = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    # remarks_in_nepali = models.TextField(blank=True, null=True)
    is_void = models.BooleanField(default=False)
    # created_at = models.DateTimeField()
    # created_by = models.ForeignKey("user_auth.User",db_column='created_by',on_delete=models.PROTECT, related_name='+')

    class Meta:
        db_table = "nominee_relation"
        managed=False
