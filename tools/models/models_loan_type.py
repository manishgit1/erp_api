
from django.db import models
from django.conf import settings
from master.models import GenericIdEntity


class LoanType(GenericIdEntity):
    name = models.CharField(max_length=255)  
    name_in_nepali = models.CharField(max_length=200, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    remarks_in_nepali = models.TextField(blank=True, null=True)
    is_void = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='created_by',
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="loan_types_updated",
        on_delete=models.PROTECT,
        db_column='updated_by',
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "loan_type"
        managed = False
