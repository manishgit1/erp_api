from email.policy import default
from rest_framework import generics, status
from rest_framework.response import Response
from loan.models import LoanRequest, RequestWorkflow, RoleTransactionLimit, LoanRequestHistory, LoanLedger
from loan.serializers import LoanRequestSerializer
from crm.models import LeadQuotation, LeadQuotationDocuments

from rest_framework.views import APIView
from master import globalparameters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from loan.validations import validate_loan_request
from django.conf import settings
from django.db import connections
import json
import logging
from django.db.models import F, Value, Q, Case, When, BooleanField
from django.db.models.functions import Coalesce,Concat
from datetime import datetime
from django.db import transaction

logger = logging.getLogger('django')

DB_NAME = settings.DB_NAME

class LoanRequestCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self,request,*args,**kwargs):
        try:
          _ =globalparameters.validation_for_authentication_parameters(request)
          json_error = []

          loan_request_json, validation_error_json = validate_loan_request(request,DB_NAME,pk=None)
          json_error.extend(validation_error_json)

          if json_error:
            error_message = {
              globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_INVALID_PARAMS,
              globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
              globalparameters.RESULT_ERROR : json_error
            }
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

          query = "SELECT * FROM insert_loan_request(%s,%s)"
          params = [json.dumps(loan_request_json,default=str),False]

          response = globalparameters.execute_raw_sql(request,query,params,DB_NAME)
          return response

        except Exception as e:
          logger.error(str(e), exc_info=True)
          error_msg = {
             globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
             globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
          }

          return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self,request,format=None):
      try:
        _ =globalparameters.validation_for_authentication_parameters(request)
        json_error = []

        loan_request = LoanRequest.objects.using(DB_NAME).filter(is_void=False)

        if not loan_request:
          json_error.append("Loan Request not found")
          error_message = {
            globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_DATA_NOT_FOUND,
            globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_DATA_NOT_FOUND,
            globalparameters.RESULT_ERROR : json_error
          }
          return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        
        # loan_request = loan_request.first()

        loan_data = []

        for loan in loan_request:

          loan_json = {
              'referenceId': loan.reference_id,
              'clientName': loan.client.full_name,
              'clientCode': loan.client.client_code,
              'mobileNumber': loan.client.mobile_number,
              'permanentAddress': loan.client.permanent_address,
              'loanType': loan.loan_type.name,
              'loanPurpose': loan.loan_purpose.name,
              'loanAmount': loan.amount,
              'tenureMonths': loan.tenure_months,
              'interestRate': loan.interest_rate,
              'valueDateAd': loan.value_date_ad,
              'emiDateAd': loan.emi_date_ad,
              'status': loan.status,
              'remarks': loan.remarks,
              'createdBy': loan.created_by.full_name,
              'createdAt': loan.created_at,
              'updatedBy': loan.updated_by.full_name,
              'updatedAt': loan.updated_at,
              'isVoid': loan.is_void,
              'canApprove': (loan.follower_role_id == request.user.role_id) if loan.follower_role_id else False,
              'canEdit': (loan.follower_role_id == request.user.role_id) if loan.follower_role_id else False,
          }
          loan_data.append(loan_json)
        return Response(loan_data,status=status.HTTP_200_OK)

      except Exception as e:
        logger.error(str(e), exc_info=True)
        error_msg = {
           globalparameters.RESULT_CODE : globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
           globalparameters.RESULT_DESCRIPTION : globalparameters.RESULT_INTERNAL_SERVER_ERROR
        }

        return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


      

class PendingLoanRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            loan_request_data = list(LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='PENDING').annotate(
                referenceId=F('reference_id'),
                # clientName=F('client__full_name'),
                clientName=Concat(
                    Coalesce(F('client__first_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__middle_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__last_name'), Value(''))
                ),
                clientCode=F('client__client_code'),
                mobileNumber=F('client__mobile_number'),
                permanentAddress=Concat(
                    Coalesce(F('client__permanent_municipality__name'), Value('')),
                    Value('-'),
                    Coalesce(F('client__permanent_ward_number'), Value('')),
                    Value(', '),
                    Coalesce(F('client__permanent_district__name'), Value(''))
                ),
                loanType=F('loan_type__name'),
                loanPurpose=F('loan_purpose__name'),
                loanAmount=F('amount'),
                tenureMonths=F('tenure_months'),
                interestRate=F('interest_rate'),
                valueDateAd=F('value_date_ad'),
                emiDateAd=F('emi_date_ad'),
                createdBy=F('created_by__username'),
                createdAt=F('created_at'),
                updatedBy=F('updated_by__username'),
                updatedAt=F('updated_at'),
                canApprove=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                canEdit=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
            ).values('referenceId', 'clientName', 'clientCode', 'mobileNumber', 'permanentAddress', 'loanType', 'loanPurpose', 'loanAmount', 'tenureMonths', 'interestRate', 'valueDateAd', 'emiDateAd', 'status', 'remarks', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'canApprove', 'canEdit'))

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": loan_request_data
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RevertedLoanRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            loan_request_data = list(LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='REVERTED').annotate(
                referenceId=F('reference_id'),
                clientName=Concat(
                    Coalesce(F('client__first_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__middle_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__last_name'), Value(''))
                ),
                clientCode=F('client__client_code'),
                mobileNumber=F('client__mobile_number'),
                permanentAddress=Concat(
                    Coalesce(F('client__permanent_municipality__name'), Value('')),
                    Value('-'),
                    Coalesce(F('client__permanent_ward_number'), Value('')),
                    Value(', '),
                    Coalesce(F('client__permanent_district__name'), Value(''))
                ),
                loanType=F('loan_type__name'),
                loanPurpose=F('loan_purpose__name'),
                loanAmount=F('amount'),
                tenureMonths=F('tenure_months'),
                interestRate=F('interest_rate'),
                valueDateAd=F('value_date_ad'),
                emiDateAd=F('emi_date_ad'),
                createdBy=F('created_by__username'),
                createdAt=F('created_at'),
                updatedBy=F('updated_by__username'),
                updatedAt=F('updated_at'),
                canApprove=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                canEdit=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
            ).values('referenceId', 'clientName', 'clientCode', 'mobileNumber', 'permanentAddress', 'loanType', 'loanPurpose', 'loanAmount', 'tenureMonths', 'interestRate', 'valueDateAd', 'emiDateAd', 'status', 'remarks', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'canApprove', 'canEdit'))

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": loan_request_data
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RejectedLoanRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            loan_request_data = list(LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='REJECTED').annotate(
                referenceId=F('reference_id'),
                clientName=Concat(
                    Coalesce(F('client__first_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__middle_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__last_name'), Value(''))
                ),
                clientCode=F('client__client_code'),
                mobileNumber=F('client__mobile_number'),
                permanentAddress=Concat(
                    Coalesce(F('client__permanent_municipality__name'), Value('')),
                    Value('-'),
                    Coalesce(F('client__permanent_ward_number'), Value('')),
                    Value(', '),
                    Coalesce(F('client__permanent_district__name'), Value(''))
                ),
                loanType=F('loan_type__name'),
                loanPurpose=F('loan_purpose__name'),
                loanAmount=F('amount'),
                tenureMonths=F('tenure_months'),
                interestRate=F('interest_rate'),
                valueDateAd=F('value_date_ad'),
                emiDateAd=F('emi_date_ad'),
                status=F('status'),
                remarks=F('remarks'),
                createdBy=F('created_by__full_name'),
                createdAt=F('created_at'),
                updatedBy=F('updated_by__full_name'),
                updatedAt=F('updated_at'),
                canApprove=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                canEdit=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
            ).values('referenceId', 'clientName', 'clientCode', 'mobileNumber', 'permanentAddress', 'loanType', 'loanPurpose', 'loanAmount', 'tenureMonths', 'interestRate', 'valueDateAd', 'emiDateAd', 'status', 'remarks', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'canApprove', 'canEdit'))

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": loan_request_data
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ApprovedLoanRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            loan_request_data = list(LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='APPROVED').annotate(
                referenceId=F('reference_id'),
                clientName=Concat(
                    Coalesce(F('client__first_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__middle_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__last_name'), Value(''))
                ),
                clientCode=F('client__client_code'),
                mobileNumber=F('client__mobile_number'),
                permanentAddress=Concat(
                    Coalesce(F('client__permanent_municipality__name'), Value('')),
                    Value('-'),
                    Coalesce(F('client__permanent_ward_number'), Value('')),
                    Value(', '),
                    Coalesce(F('client__permanent_district__name'), Value(''))
                ),
                loanType=F('loan_type__name'),
                loanPurpose=F('loan_purpose__name'),
                loanAmount=F('amount'),
                tenureMonths=F('tenure_months'),
                interestRate=F('interest_rate'),
                valueDateAd=F('value_date_ad'),
                emiDateAd=F('emi_date_ad'),
                createdBy=F('created_by__username'),
                createdAt=F('created_at'),
                updatedBy=F('updated_by__username'),
                updatedAt=F('updated_at'),
                canApprove=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                canEdit=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
            ).values('referenceId', 'clientName', 'clientCode', 'mobileNumber', 'permanentAddress', 'loanType', 'loanPurpose', 'loanAmount', 'tenureMonths', 'interestRate', 'valueDateAd', 'emiDateAd', 'status', 'remarks', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'canApprove', 'canEdit'))

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": loan_request_data
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DisbursedLoanRequestListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            loan_request_data = list(LoanRequest.objects.using(DB_NAME).filter(is_void=False, status='DISBURSED').annotate(
                referenceId=F('reference_id'),
                clientName=Concat(
                    Coalesce(F('client__first_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__middle_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__last_name'), Value(''))
                ),
                clientCode=F('client__client_code'),
                mobileNumber=F('client__mobile_number'),
                permanentAddress=Concat(
                    Coalesce(F('client__permanent_municipality__name'), Value('')),
                    Value('-'),
                    Coalesce(F('client__permanent_ward_number'), Value('')),
                    Value(', '),
                    Coalesce(F('client__permanent_district__name'), Value(''))
                ),
                loanType=F('loan_type__name'),
                loanPurpose=F('loan_purpose__name'),
                loanAmount=F('amount'),
                tenureMonths=F('tenure_months'),
                interestRate=F('interest_rate'),
                valueDateAd=F('value_date_ad'),
                emiDateAd=F('emi_date_ad'),
                createdBy=F('created_by__username'),
                createdAt=F('created_at'),
                updatedBy=F('updated_by__username'),
                updatedAt=F('updated_at'),
                canApprove=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                canEdit=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
            ).values('referenceId', 'clientName', 'clientCode', 'mobileNumber', 'permanentAddress', 'loanType', 'loanPurpose', 'loanAmount', 'tenureMonths', 'interestRate', 'valueDateAd', 'emiDateAd', 'status', 'remarks', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'canApprove', 'canEdit'))

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": loan_request_data
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ApproveRejectRevertLoanRequest(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @transaction.atomic(using=DB_NAME)
    def post(self,request,*args,**kwargs):
        _ = globalparameters.validation_for_authentication_parameters(request)

        json_error = []
        data = json.loads(request.body)

        approval_status = str(data['approvalStatus']).strip().lower() if 'approvalStatus' in data else ''
        loan_request_id = str(data['loanRequestId']).strip() if 'loanRequestId' in data else ''
        remarks = str(data['remarks']).strip() if 'remarks' in data else ''

        if not approval_status:
            json_error.append("Approval status is required")
        if not loan_request_id:
            json_error.append("Loan Request id is required")
        if not remarks:
            json_error.append("Remarks is required")
        
        if json_error:
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
                "errors": json_error
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            loan_request = LoanRequest.objects.using(DB_NAME).get(reference_id=loan_request_id)
            loan_request.remarks = remarks
            # loan_request.updated_by = request.user
            loan_request.updated_at = datetime.now()

            if approval_status == 'approved':
                role_limit = RoleTransactionLimit.objects.using(DB_NAME).filter(
                    role_id=request.user.role_id,
                    is_active=True,
                    is_void=False
                ).first()

                action = 'APPROVED'
                to_role_id = None

                if role_limit and loan_request.amount <= role_limit.limit_amount:
                    loan_request.status = 'APPROVED'
                    loan_request.follower_role_id = None
                else:
                    next_workflow = RequestWorkflow.objects.using(DB_NAME).filter(
                        initiator_role_id=request.user.role_id,
                        is_active=True,
                        is_void=False
                    ).first()

                    if next_workflow:
                        loan_request.follower_role_id = next_workflow.follower_role_id
                        loan_request.status = 'PENDING'
                        action = 'FORWARDED'
                        to_role_id = next_workflow.follower_role_id
                    else:
                        loan_request.status = 'APPROVED'
                        loan_request.follower_role_id = None
            
            elif approval_status == 'rejected':
                loan_request.status = 'REJECTED'
                loan_request.follower_role_id = None
                action = 'REJECTED'
                to_role_id = None
            
            elif approval_status == 'reverted':
                loan_request.status = 'REVERTED'
                # Revert back to creator
                loan_request.follower_role_id = loan_request.created_by.role_id
                action = 'RETURNED'
                to_role_id = loan_request.created_by.role_id
            
            elif approval_status == 'disbursed':
                loan_request.status = 'DISBURSED'
                loan_request.follower_role_id = None
                action = 'DISBURSED'
                to_role_id = None

                # Create Ledger Entry
                client = loan_request.client
                ledger_name = f"{client.first_name} {client.last_name} - Loan Ledger"
                ledger_code = f"{client.client_code}-{loan_request.reference_id}"

                LoanLedger.objects.using(DB_NAME).create(
                    loan_request=loan_request,
                    client=client,
                    ledger_name=ledger_name,
                    ledger_code=ledger_code,
                    transaction_date=datetime.now().date(),
                    particulars=f"Loan Disbursed - Ref: {loan_request.reference_id}",
                    debit_amount=loan_request.amount,
                    credit_amount=0,
                    balance_amount=loan_request.amount,
                    transaction_type='DISBURSEMENT',
                    created_by_id=request.user.id
                )
            
            else:
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                    globalparameters.RESULT_DESCRIPTION: "Invalid approval status",
                }, status=status.HTTP_400_BAD_REQUEST)

            loan_request.save()

            # Save History
            LoanRequestHistory.objects.using(DB_NAME).create(
                loan_request=loan_request,
                from_role_id=request.user.role_id,
                to_role_id=to_role_id,
                action=action,
                status=loan_request.status,
                remarks=remarks,
                created_by_id=request.user.id,
                updated_by_id=request.user.id
            )

            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "data": {
                    "loanRequestId": loan_request.reference_id,
                    "status": loan_request.status,
                    "remarks": loan_request.remarks,
                    "updatedBy": loan_request.updated_by.username if loan_request.updated_by else '',
                    "updatedAt": loan_request.updated_at
                }
            }, status=status.HTTP_200_OK)
        except LoanRequest.DoesNotExist:
            logger.error("Loan request not found", exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_ERROR_CODE,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_ERROR,
                "errors": ["Loan request not found"]
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanRequestFindByIdAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            
            loan = LoanRequest.objects.using(DB_NAME).filter(reference_id=pk, is_void=False).annotate(
                referenceId=F('reference_id'),
                clientName=Concat(
                    Coalesce(F('client__first_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__middle_name'), Value('')),
                    Value(' '),
                    Coalesce(F('client__last_name'), Value(''))
                ),
                clientCode=F('client__client_code'),
                mobileNumber=F('client__mobile_number'),
                permanentAddress=Concat(
                    Coalesce(F('client__permanent_municipality__name'), Value('')),
                    Value('-'),
                    Coalesce(F('client__permanent_ward_number'), Value('')),
                    Value(', '),
                    Coalesce(F('client__permanent_district__name'), Value(''))
                ),
                loanType=F('loan_type__reference_id'),
                loanPurpose=F('loan_purpose__reference_id'),
                paymentScheme=F('payment_scheme__reference_id'),
                loanAmount=F('amount'),
                tenureMonths=F('tenure_months'),
                interestRate=F('interest_rate'),
                valueDateAd=F('value_date_ad'),
                emiDateAd=F('emi_date_ad'),
                createdBy=F('created_by__username'),
                createdAt=F('created_at'),
                updatedBy=F('updated_by__username'),
                updatedAt=F('updated_at'),
                canApprove=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                canEdit=Case(
                    When(follower_role_id=request.user.role_id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
            ).values('referenceId', 'clientName', 'clientCode', 'mobileNumber', 'permanentAddress', 'loanType', 'loanPurpose', 'paymentScheme', 'loanAmount', 'tenureMonths', 'interestRate', 'valueDateAd', 'emiDateAd', 'status', 'remarks', 'createdBy', 'createdAt', 'updatedBy', 'updatedAt', 'canApprove', 'canEdit').first()

            if not loan:
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: "Loan request not found",
                }, status=status.HTTP_404_NOT_FOUND)

            # Fetch document images
            loan_request_obj = LoanRequest.objects.using(DB_NAME).filter(reference_id=pk).first()
            document_images = []
            if loan_request_obj and loan_request_obj.client and loan_request_obj.client.global_contact_id:
                lead_quotation = LeadQuotation.objects.using(DB_NAME).filter(
                    contact_id=loan_request_obj.client.global_contact_id, 
                    is_void=False
                ).first()
                
                if lead_quotation:
                    lead_documents = LeadQuotationDocuments.objects.using(DB_NAME).filter(
                        lead_id=lead_quotation.id, 
                        is_void=False
                    )
                    for doc in lead_documents:
                        img_base64 = globalparameters.get_image_from_drive(DB_NAME, 'lead_quotation', doc.file_name)
                        if img_base64:
                            document_images.append({
                                'imageValue': img_base64
                            })

            loan['documentImages'] = document_images

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": loan
            }
            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            error_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }
            return Response(error_msg, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanRequestTimelineAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk, format=None):
        try:
            _ = globalparameters.validation_for_authentication_parameters(request)
            
            history = LoanRequestHistory.objects.using(DB_NAME).filter(
                loan_request__reference_id=pk
            ).order_by('created_at')

            if not history.exists():
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_DATA_NOT_FOUND,
                    globalparameters.RESULT_DESCRIPTION: "No history found for this loan request",
                }, status=status.HTTP_404_NOT_FOUND)

            # serializer = LoanRequestHistorySerializer(history, many=True)
            history_data = []
            for item in history:
                history_data.append({
                    "action": item.action,
                    "status": item.status,
                    "fromRoleName": item.from_role.name if item.from_role else '',
                    "toRoleName": item.to_role.name if item.to_role else '',
                    "remarks": item.remarks,
                    "createdBy": item.created_by.username if item.created_by else '',
                    "createdAt": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else ''
                })

            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                "datas": history_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

