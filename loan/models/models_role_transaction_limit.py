from django.db import models
from master.models import GenericIdEntity
from user_auth.models import UserRole
from django.conf import settings

class RoleTransactionLimit(GenericIdEntity):
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, related_name='+')
    limit_amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_void = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='+',
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='updated_by',
        related_name='+',
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "role_transaction_limit"
        managed = False

    def __str__(self):
        return f"{self.role.name} - {self.limit_amount}"
