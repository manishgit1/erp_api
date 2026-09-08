from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from master import globalparameters
from loan.models import LoanRequest
from loan.serializers import LoanRequestSerializer
import json
import logging
import ast
from django.db.models import Q

logger = logging.getLogger('django')

class ApprovedLoanReportAPIView(APIView):
    """
    GET endpoint to return approved loan report data.
    Expects a `jsonData` query parameter containing filters:
      - from_date   : Start date (YYYY-MM-DD)
      - to_date     : End date (YYYY-MM-DD)
      - client_name : Search string for client name
      - loan_type   : ID of the loan type
    """

    def get(self, request, *args, **kwargs):
        try:
            jsonData = request.GET.get("jsonData")
            filters = {}
            if jsonData:
                try:
                    # Use ast.literal_eval for flexibility with single/double quotes
                    filters = ast.literal_eval(jsonData)
                except (ValueError, SyntaxError):
                    try:
                        filters = json.loads(jsonData)
                    except json.JSONDecodeError:
                        return Response({
                            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                            globalparameters.RESULT_DESCRIPTION: "Invalid JSON format in jsonData",
                        }, status=status.HTTP_400_BAD_REQUEST)

            # Filter for approved loans that are not void
            queryset = LoanRequest.objects.filter(status='APPROVED', is_void=False).order_by('-created_at')

            # Apply date filters (using value_date_ad as the loan's effective date)
            from_date = filters.get('from_date') or filters.get('date') # Support 'date' as a single date or just a filter key
            to_date = filters.get('to_date')
            
            if from_date:
                queryset = queryset.filter(value_date_ad__gte=from_date)
            if to_date:
                queryset = queryset.filter(value_date_ad__lte=to_date)

            # Apply client name filter
            client_name = filters.get('client_name') or filters.get('name')
            if client_name:
                queryset = queryset.filter(
                    Q(client__first_name__icontains=client_name) |
                    Q(client__middle_name__icontains=client_name) |
                    Q(client__last_name__icontains=client_name)
                )

            # Apply loan type filter
            loan_type = filters.get('loan_type')
            if loan_type:
                queryset = queryset.filter(loan_type_id=loan_type)

            # Apply any other custom filters if provided in jsonData
            # for example, specific amount range if ever needed
            amount_min = filters.get('amount_min')
            amount_max = filters.get('amount_max')
            if amount_min:
                queryset = queryset.filter(amount__gte=amount_min)
            if amount_max:
                queryset = queryset.filter(amount__lte=amount_max)

            serializer = LoanRequestSerializer(queryset, many=True)

            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                'datas': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoanReportAPIView(APIView):
    """
    GET endpoint to return general loan report data.
    Expects a `jsonData` query parameter containing filters:
      - from_date      : Start date (YYYY-MM-DD)
      - to_date        : End date (YYYY-MM-DD)
      - name           : Search string for client name
      - loan_type      : ID of the loan type
      - payment_scheme : ID of the payment scheme
      - status         : Loan status (PENDING, APPROVED, REJECTED, DISBURSED)
    """

    def get(self, request, *args, **kwargs):
        try:
            jsonData = request.GET.get("jsonData")
            filters = {}
            if jsonData:
                try:
                    filters = ast.literal_eval(jsonData)
                except (ValueError, SyntaxError):
                    try:
                        filters = json.loads(jsonData)
                    except json.JSONDecodeError:
                        return Response({
                            globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                            globalparameters.RESULT_DESCRIPTION: "Invalid JSON format in jsonData",
                        }, status=status.HTTP_400_BAD_REQUEST)

            queryset = LoanRequest.objects.filter(is_void=False).order_by('-created_at')

            # Apply date filters
            from_date = filters.get('from_date') or filters.get('date')
            to_date = filters.get('to_date')
            if from_date:
                queryset = queryset.filter(value_date_ad__gte=from_date)
            if to_date:
                queryset = queryset.filter(value_date_ad__lte=to_date)

            # Apply client name filter
            name = filters.get('name') or filters.get('client_name')
            if name:
                queryset = queryset.filter(
                    Q(client__first_name__icontains=name) |
                    Q(client__middle_name__icontains=name) |
                    Q(client__last_name__icontains=name)
                )

            # Apply filters for FKs
            loan_type = filters.get('loan_type')
            if loan_type:
                queryset = queryset.filter(loan_type_id=loan_type)

            payment_scheme = filters.get('payment_scheme')
            if payment_scheme:
                queryset = queryset.filter(payment_scheme_id=payment_scheme)

            status_filter = filters.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)

            serializer = LoanRequestSerializer(queryset, many=True)

            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                'datas': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

