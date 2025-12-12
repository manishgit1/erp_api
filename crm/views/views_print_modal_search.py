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
from crm.models import LeadQuotationDocuments
DB_NAME = settings.DB_NAME
import ast

logger = logging.getLogger('django')

# class PrintModalSearchListDataAPIView(APIView):
   
#    def get(self,request,format=None):
#       json_error = []
#       try:
          
          
#           lead_quotation_data = list( LeadQuotation.objects.using(DB_NAME).filter(is_void=False,status=1,is_documents_submitted=True).annotate(
#           referenceId = F('reference_id'),
#           customerName = Concat(Coalesce(F('contact__first_name'), Value(' '))
#                                ,Value(' '), 
#                                Coalesce(F('contact__middle_name'), 
#                                Value(' ')), 
#                                Value(' '),
#                                Coalesce(F('contact__last_name'), Value(' '))), 
#            mobileNumber = F('contact__mobile_number'), permanentAddress =Concat(F('contact__permanent_vdc_municipality__name'),Value(' '), F('contact__permanent_district__name')),
#            loanType = F('loan_type__name'), loanAmount = F('loan_amount')
#            ).values('referenceId','customerName', 'mobileNumber', 'permanentAddress', 'permanentAddress','loanType', 'loanAmount','remarks'))

#           if lead_quotation_data:
#             response_msg = {
#                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
#                globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
#                "datas": lead_quotation_data
#             }
#             return Response(response_msg, status=status.HTTP_200_OK)
      
#       except Exception as exc:
#         logger.error(str(exc), exc_info=True)
#         response_msg = {
#            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
#            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
#         }
#         return Response(response_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

class PrintModalSearchListDataAPIView(APIView):
    """
    API endpoint to fetch customer info and related document images
    for printing in the modal.
    """

    def get(self, request, format=None):
        try:
            data = json.loads(json.dumps(ast.literal_eval(request.GET.get('jsonData'))))
            lead_id = str(data.get('leadId', '')).strip()

            lead = LeadQuotation.objects.get(reference_id=lead_id)
        except (LeadQuotation.DoesNotExist, ValueError, KeyError) as e:
            return Response({"error": "Lead not found or invalid data"}, status=status.HTTP_404_NOT_FOUND)

        customer_data = {
            "referenceId": lead.reference_id,
            "name": lead.contact.first_name,
            "mobileNumber": lead.contact.mobile_number,
            "address": lead.contact.permanent_vdc_municipality.name,
            "amount": str(lead.loan_amount) if hasattr(lead, 'loan_amount') else None
        }

        documents = LeadQuotationDocuments.objects.filter(lead_id=lead.id)

        document_data = []
        for doc in documents:
            img_base64 = globalparameters.get_image_from_drive(DB_NAME, "lead_quotation", doc.file_name)
            if img_base64:
                document_data.append({
                    "imageValue": img_base64
                })

        response = {
           "customerJson": customer_data,
           "documentJson": document_data
        }

        return Response(response, status=status.HTTP_200_OK)

