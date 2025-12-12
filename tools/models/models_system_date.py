from master.models import GenericIdEntity
from django.db import models

class SystemDay(GenericIdEntity):
    business_date_ad = models.DateField(unique=True)
    business_date_bs = models.CharField(max_length=20)
    is_open = models.BooleanField(default=True)
    last_closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-business_date_ad']
        db_table = 'system_day'
        managed = False

