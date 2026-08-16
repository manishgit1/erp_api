from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from master.models import ClientMaster
from crm.models import LeadQuotation
from loan.models import LoanRequest
from master import globalparameters
import logging

logger = logging.getLogger('django')
DB_NAME = settings.DB_NAME

class DashboardMetricsAPIView(APIView):
    """
    API endpoint to return dashboard metrics for loan requests, 
    document processing, and kyc registered customers.
    """
    def get(self, request, *args, **kwargs):
        try:
            # 1. Loan Request Metrics
            loan_metrics = {
                "total": LoanRequest.objects.using(DB_NAME).filter(is_void=False).count(),
                "pending": LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='PENDING').count(),
                "approved": LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='APPROVED').count(),
                "rejected": LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='REJECTED').count(),
                "disbursed": LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='DISBURSED').count(),
            }

            # 2. Document Processing Metrics (from LeadQuotation)
            doc_metrics = {
                "totalSubmitted": LeadQuotation.objects.using(DB_NAME).filter(is_void=False, is_documents_submitted=True).count(),
                "approved": LeadQuotation.objects.using(DB_NAME).filter(is_void=False, is_document_approved=True).count(),
                "rejected": LeadQuotation.objects.using(DB_NAME).filter(is_void=False, is_document_rejected=True).count(),
                "pending": LeadQuotation.objects.using(DB_NAME).filter(
                    is_void=False, 
                    is_documents_submitted=True, 
                    is_document_approved=False, 
                    is_document_rejected=False
                ).count(),
            }

            # 3. KYC Metrics
            kyc_metrics = {
                "totalRegistered": ClientMaster.objects.using(DB_NAME).filter(is_void=False).count(),
            }

            response_data = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": {
                    "loanRequests": loan_metrics,
                    "documentProcessing": doc_metrics,
                    "kycCustomers": kyc_metrics
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
