from django.db import models
from master.models import GenericIdEntity

class LoanCollateralType(GenericIdEntity):
    name = models.CharField(max_length=255)
    remarks = models.TextField(blank=True, null=True)
    is_void = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey("user_auth.User",db_column='created_by',on_delete=models.PROTECT, related_name='+')

    class Meta:
        db_table = "loan_collateral_type"
