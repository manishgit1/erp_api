from django.db import models
from master.models import GenericIdEntity


class LeadSource(GenericIdEntity):
    name = models.CharField(max_length=255)
    name_in_nepali = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    remarks_in_nepali = models.TextField(blank=True, null=True)
    is_void = models.BooleanField(default=False)

    class Meta:
        db_table = "lead_source"
        managed=False
