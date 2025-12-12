from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import logging
from rest_framework import status
from master import globalparameters
from crm.validation import validate_lead_quotation
from django.db.models import F, Func, Value, CharField
from crm.models import LeadQuotation
from django.db.models.functions import TruncMinute
import json
DB_NAME = settings.DB_NAME

logger = logging.getLogger('django')

class LeadQuotationCreateAPIView(APIView):
   
   @transaction.atomic
   def post(self,request,*args,**kwargs):
      try:
         json_error = []
         lead_quotation_json,lead_quotation_error_list = validate_lead_quotation(request,DB_NAME,None)
         json_error.extend(lead_quotation_error_list)
         if json_error:
            response_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
               globalparameters.RESULT_DESCRIPTION:  globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
               globalparameters.RESULT_ERROR: json_error
            }
            return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
         
         query = "select * from insert_update_lead_quotation_registration(%s)"
         params = [json.dumps(lead_quotation_json)]

         return globalparameters.execute_raw_sql(request,query,params,DB_NAME)
      
      except Exception as e:
         logger.error(str(e), exc_info=True)
         error_msg = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }
         return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LeadQuotationListAPIView(APIView):
    def get(self, request, *args, **kwargs):

        quotations = (
            LeadQuotation.objects.using(DB_NAME)
            .select_related("contact", "loan_type", "source")
            .annotate(
                firstName=F("contact__first_name"),
                lastName=F("contact__last_name"),
                mobileNumber=F("contact__mobile_number"),
                loanType=F("loan_type__name"),
                loanAmount = F("loan_amount"),
                interestRate = F("interest_rate"),
                permanentMunicipality = F("contact__permanent_vdc_municipality__name"),
                permanentDistrict = F("contact__permanent_district__name"),
                createdAt = Func(
                        F('created_at'),
                        Value('YYYY-MM-DD, HH24:MI'),
                        function='to_char',
                        output_field=CharField()
                     )
            )
            .values(
                "quotation_number",
                "cic_status",
                "loanType",
                "source__name",
                "firstName",
                "lastName",
                "mobileNumber",
                "permanentMunicipality",
                "permanentDistrict",
                "loanAmount",
                "tenure",
                "interestRate",
                "createdAt",
                "created_by",
                "remarks"
            )
        )

        response_msg = {
           globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
           globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
           "datas": list(quotations)
        }

        return Response(response_msg, status=status.HTTP_200_OK)
