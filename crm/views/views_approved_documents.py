from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.conf import settings
import logging
from rest_framework import status
from master import globalparameters
from crm.validation import validate_lead_quotation
from master.global_validation import validate_for_obj
from crm.models import LeadQuotation
from django.db.models import F, Value
from django.db.models.functions import Coalesce, Concat
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


DB_NAME = settings.DB_NAME

logger = logging.getLogger('django')

class ApprovedDocumentsListDataAPIView(APIView):

   permission_classes = [IsAuthenticated]
   authentication_classes = [JWTAuthentication]

   
   def get(self,request,format=None):
      json_error = []
      try:
          lead_quotation_data = list( LeadQuotation.objects.using(DB_NAME).filter(is_void=False,status=2,is_document_approved=True,is_documents_submitted=True).annotate(
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



# class DocumentApprovalRejectApproveCreateAPIView(APIView):
   
#    @transaction.atomic
#    def post(self,request,*args,**kwargs):
#       try:
#          json_error = []

#          data = json.loads(request.body)

#          # APPROVE/REJECT
#          lead_id = str(data['leadId']).strip() if 'leadId' in data else ''
#          lead,lead_error_list = validate_for_obj(lead_id, DB_NAME, LeadQuotation, 'Lead Quotation')
#          json_error.extend(lead_error_list)

#          if json_error:
#             response_msg = {
#                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
#                globalparameters.RESULT_DESCRIPTION:  globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
#                globalparameters.RESULT_ERROR: json_error
#             }
#             return Response(response_msg, status=status.HTTP_400_BAD_REQUEST)
         
#          action = str(data['action']).strip() if 'action' in data else ''
#          remarks = str(data['remarks']).strip() if 'remarks' in data else ''
         
#          if action.upper() == 'APPROVE':
#             lead.is_document_approved = True
#             lead.is_document_rejected = False
#             lead.approval_remarks = remarks
#          elif action.upper() == 'REJECT':
#             lead.is_document_rejected = True         
#             lead.is_document_approved = False 
#             lead.reject_remarks = remarks        
#          lead.status = 2
         
#          lead.save()
         
#          success_msg = {
#             globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
#             globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_SUCCESS,
#          }
#          return Response(success_msg, status=status.HTTP_200_OK)
    
#       except Exception as e:
#          logger.error(str(e), exc_info=True)
#          error_msg = {
#             globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
#             globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
#          }
#          return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)