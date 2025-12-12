from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import logging
from rest_framework import status
from master import globalparameters
from crm.validation import validate_lead_quotation
from crm.models import LeadQuotation
from django.db.models import F, Value
from django.db.models.functions import Coalesce, Concat
import json
DB_NAME = settings.DB_NAME

logger = logging.getLogger('django')

class InquiryFollowUpListDataAPIView(APIView):
   
   def get(self,request,format=None):
      json_error = []
      try:
          lead_quotation_data = list( LeadQuotation.objects.using(DB_NAME).filter(is_void=False,status=0,is_documents_submitted=False).annotate(
          referenceId = F('reference_id'),
          customerName = Concat(Coalesce(F('contact__first_name'), Value(' '))
                               ,Value(' '), 
                               Coalesce(F('contact__middle_name'), 
                               Value(' ')), 
                               Value(' '),
                               Coalesce(F('contact__last_name'), Value(' '))), 
           mobileNumber = F('contact__mobile_number'), permanentAddress =Concat(F('contact__permanent_vdc_municipality__name'),Value(' '), F('contact__permanent_district__name')),
           loanType = F('loan_type__name'), loanAmount = F('loan_amount')
           ).values('referenceId','customerName', 'mobileNumber', 'permanentAddress', 'permanentAddress','loanType', 'loanAmount','remarks'))

          if lead_quotation_data:
            response_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
               globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
               "datas": lead_quotation_data
            }
            return Response(response_msg, status=status.HTTP_200_OK)
      
      except Exception as exc:
        logger.error(str(exc), exc_info=True)
        response_msg = {
           globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
           globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
        }
        return Response(response_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)