from django.db import models
from django.conf import settings
from master.models import GenericIdEntity, ClientMaster
from loan.models.models_loan_request import LoanRequest

class LoanLedger(GenericIdEntity):
    loan_request = models.ForeignKey(LoanRequest, on_delete=models.PROTECT, related_name='ledger_entries')
    client = models.ForeignKey(ClientMaster, on_delete=models.PROTECT, related_name='ledger_entries')
    
    ledger_name = models.CharField(max_length=255)
    ledger_code = models.CharField(max_length=100) # e.g. 2345HSST899
    
    transaction_date = models.DateField()
    particulars = models.TextField(blank=True, null=True)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    transaction_type = models.CharField(max_length=50) # DISBURSEMENT, REPAYMENT, INTEREST, CHARGE
    
    is_void = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='created_by',
        related_name='+',
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "loan_ledger"
        managed = False

    def __str__(self):
        return f"{self.ledger_code} - {self.ledger_name} - {self.transaction_type}"
