from django.db import models
from master.models import GenericIdEntity
from crm.models import LeadQuotation


class LeadQuotationDocuments(GenericIdEntity):
   lead = models.ForeignKey(LeadQuotation, on_delete=models.PROTECT, related_name='+')
   file_name = models.CharField(max_length=32)
   created_at = models.DateTimeField(auto_now_add=True)
   created_by = models.IntegerField(null=True, blank=True)
   updated_at = models.DateTimeField(auto_now=True)
   updated_by = models.IntegerField(null=True, blank=True)  
   is_void = models.BooleanField(default=False)

   class Meta:
      db_table = 'lead_quotation_documents'
