from django.db import models
from django.conf import settings
from master.models import GenericIdEntity, ClientMaster
from tools.models import LoanType, LoanPaymentScheme, LoanPurpose
from user_auth.models import UserRole

# Create your models here.

class LoanRequest(GenericIdEntity):
    # Foreign Keys
    client = models.ForeignKey(ClientMaster, on_delete=models.PROTECT, related_name='loan_requests')
    loan_type = models.ForeignKey(LoanType, on_delete=models.PROTECT, related_name='loan_requests')

    # Loan Details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    tenure_months = models.IntegerField()
    loan_purpose = models.ForeignKey(LoanPurpose, on_delete=models.PROTECT, related_name='+', blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Dates
    value_date_ad = models.DateField(blank=True, null=True)
    emi_date_ad = models.DateField(blank=True, null=True)
    
    # Status and Remarks
    status = models.CharField(max_length=50, default='PENDING') # PENDING, APPROVED, REJECTED, DISBURSED
    remarks = models.TextField(blank=True, null=True)
    payment_scheme = models.ForeignKey(LoanPaymentScheme, on_delete=models.PROTECT, related_name='+', blank=True, null=True)


    # Tracking
    is_void = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='created_loan_requests',
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='updated_by',
        related_name='updated_loan_requests',
        null=True,
        blank=True,
    )

    follower_role = models.ForeignKey(UserRole, on_delete=models.PROTECT, related_name='loan_requests', null=True, blank=True)

    class Meta:
        db_table = "loan_request"
        managed = False

    def __str__(self):
        return f"Loan Request for {self.client} - {self.amount}"



from django.db import models
from django.utils import timezone


class LoanRequestHistory(GenericIdEntity):

    ACTION_CHOICES = (
        ('CREATED', 'Created'),
        ('FORWARDED', 'Forwarded'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),
        ('DISBURSED', 'Disbursed'),
    )

    # Core relation
    loan_request = models.ForeignKey(
        LoanRequest,
        on_delete=models.PROTECT,
        related_name='history'
    )

    from_role = models.ForeignKey(UserRole, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    to_role = models.ForeignKey(UserRole, on_delete=models.PROTECT, related_name='+', null=True, blank=True)

    # Action + status
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    status = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    # Decision metadata
    remarks = models.TextField(null=True, blank=True)
    is_final = models.BooleanField(default=False)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='created_by', related_name='+', null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='updated_by', related_name='+', null=True, blank=True)


    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'loan_request_history'
        managed=False

    def __str__(self):
        return f"{self.loan_request_id} - {self.action}"