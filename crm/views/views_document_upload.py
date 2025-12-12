from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import logging
from rest_framework import status
from master import globalparameters
from crm.models import LeadQuotation, LeadQuotationDocuments
from crm.validation import validate_lead_quotation
from master.models import generate_uuid
import datetime
import json
from master.global_validation import validate_by_reference_id, validate_for_obj
DB_NAME = settings.DB_NAME

logger = logging.getLogger('django')

class DocumentUploadCreateAPIView(APIView):
   
   @transaction.atomic
   def post(self,request,*args,**kwargs):
      try:
         json_error = []

         data = json.loads(request.body)
         
         lead_id = str(data['leadId']).strip() if 'leadId' in data else ''
         lead,lead_error_list = validate_for_obj(lead_id, DB_NAME, LeadQuotation, 'Lead Quotation')
         json_error.extend(lead_error_list)
         # if lead_id:
         #    lead_documents = LeadQuotationDocuments.objects.using(DB_NAME).create(
         #          reference_id = generate_uuid(),
         #          file_name=file_name
         #    )
         #    lead_documents.lead_id = lead_id
         #    lead_documents.created_at = datetime.datetime.now()
         #    lead_documents.save()
         if json_error:
            response_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
               globalparameters.RESULT_DESCRIPTION:  globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
               globalparameters.RESULT_ERROR: json_error
            }
            return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
         lead.status = 1
         lead.is_documents_submitted = True
         lead.save()
         
         success_msg = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
         }
         return Response(success_msg, status=status.HTTP_200_OK)
    
      except Exception as e:
         logger.error(str(e), exc_info=True)
         error_msg = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }
         return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      

class DocumentUploadUploadAPIView(APIView):
   
   @transaction.atomic
   def post(self,request,*args,**kwargs):
      try:
         json_error = []

         data = json.loads(request.body)
         image_value  = str(data['fileData']).strip() if 'fileData' in data else ''
         if  image_value:
            file_name = generate_uuid()
            globalparameters.save_image_to_drive(image_value, DB_NAME, 'lead_quotation',file_name)

            lead_id = str(data['leadId']).strip() if 'leadId' in data else ''
            lead_id,lead_error_list = validate_by_reference_id(lead_id, DB_NAME, LeadQuotation, 'Lead Quotation')
            if lead_id:
               lead_documents = LeadQuotationDocuments.objects.using(DB_NAME).create(
                     reference_id = generate_uuid(),
                     file_name=file_name
               )
               lead_documents.lead_id = lead_id
               lead_documents.created_at = datetime.datetime.now()
               lead_documents.save()
         else:
            json_error.append("Empty or Invalid Image Provided!")
         if json_error:
            response_msg = {
               globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
               globalparameters.RESULT_DESCRIPTION:  globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
               globalparameters.RESULT_ERROR: json_error
            }
            return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
         
         success_msg = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
            "fileName": file_name
         }
         return Response(success_msg, status=status.HTTP_200_OK)
    
      except Exception as e:
         logger.error(str(e), exc_info=True)
         error_msg = {
            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
            globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
         }
         return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)