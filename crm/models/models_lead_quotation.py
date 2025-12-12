# models.py
import uuid
from django.db import models
from django.utils import timezone
from master.models import GenericIdEntity, ContactMaster
from tools.models import LoanType, LeadSource


class LeadQuotation(GenericIdEntity):
   
    quotation_number = models.IntegerField(null=True, blank=True)
    contact = models.ForeignKey(
        ContactMaster, 
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    cic_status = models.CharField(max_length=255, blank=True, null=True)
    loan_type = models.ForeignKey(
        LoanType,  
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    source = models.ForeignKey(
        LeadSource,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    # purpose_code = models.ForeignKey(
    #     'LoanPurposeCode',  # assuming you have this model
    #     on_delete=models.PROTECT,
    #     null=True,
    #     blank=True
    # )
    next_follow_up_days = models.IntegerField(null=True, blank=True)
    follow_up_1_remarks = models.CharField(max_length=500, blank=True, null=True)
    follow_up_2_remarks = models.CharField(max_length=500, blank=True, null=True)
    follow_up_3_remarks = models.CharField(max_length=500, blank=True, null=True)
    follow_up_4_remarks = models.CharField(max_length=500, blank=True, null=True)
    net_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    loan_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tenure = models.IntegerField(null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.IntegerField(null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField(null=True, blank=True)  
    is_void = models.BooleanField(default=False)
    status = models.IntegerField(null=True, blank=True)
    remarks = models.CharField(max_length=500, blank=True, null=True)
    is_documents_submitted = models.BooleanField(default=False)
    is_document_approved = models.BooleanField(default=False)
    is_document_rejected = models.BooleanField(default=False)
    approval_remarks = models.TextField()
    reject_remarks = models.TextField()

    class Meta:
        db_table = "lead_quotation_registration"
        managed = False