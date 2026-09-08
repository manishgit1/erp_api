from master.global_validation import validate_decimal_value,validate_integer_value
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from master import globalparameters
import json
import logging
import ast

logger = logging.getLogger('django')


class EMIScheduleAPIView(APIView):
    """
    GET endpoint to generate an EMI (Equated Monthly Installment) schedule.
    Expects a `jsonData` query parameter containing:
      - loanAmount  : Total loan principal
      - interestRate: Annual interest rate (percentage, e.g. 10 for 10%)
      - tenure      : Loan tenure in months
    """

    def get(self, request, *args, **kwargs):
        try:
            
            
            error_list = []
            data = {}

            try:
                data = json.loads(json.dumps(ast.literal_eval(request.GET.get("jsonData"))))

            except json.JSONDecodeError as  exc:
                logger.error(str(exc),exc_info=True)
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
                    globalparameters.RESULT_ERROR: ['Invalid JSON']
                }, status=status.HTTP_400_BAD_REQUEST)

            if not data:
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
                    globalparameters.RESULT_ERROR: ['please provide jsonData query parameter']
                }, status=status.HTTP_400_BAD_REQUEST)

            loan_amount = data['loan_amount'] if 'loan_amount' in data else ''
            interest_rate = data['interest_rate'] if 'interest_rate' in data else ''
            tenure = data['tenure'] if 'tenure' in data else ''


            if loan_amount is None:
                error_list.append('loanAmount is required')
            if interest_rate is None:
                error_list.append('interestRate is required')
            if tenure is None:
                error_list.append('tenure is required')

            error_list.extend(validate_decimal_value(loan_amount,'Loan Amount'))
            error_list.extend(validate_decimal_value(interest_rate,'Interest Rate'))
            error_list.extend(validate_integer_value(tenure,'Tenure'))

            if error_list:
                return Response({
                    globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INVALID_PARAMS,
                    globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_INVALID_PARAMS,
                    globalparameters.RESULT_ERROR: error_list
                }, status=status.HTTP_400_BAD_REQUEST)

            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)

            # Calculate EMI using reducing balance method
            # EMI = P * r * (1+r)^n / ((1+r)^n - 1)
            monthly_rate = (interest_rate / 100) / 12
            power = (1 + monthly_rate) ** tenure
            emi = round(loan_amount * monthly_rate * power / (power - 1), 2)

            # Build the EMI schedule
            schedule = []
            balance = loan_amount
            total_interest = 0.0
            total_principal = 0.0

            for month in range(1, tenure + 1):
                interest_component = round(balance * monthly_rate, 2)
                principal_component = round(emi - interest_component, 2)

                # Adjust last month for rounding
                if month == tenure:
                    principal_component = round(balance, 2)
                    emi_adjusted = round(principal_component + interest_component, 2)
                    balance = 0.0
                else:
                    emi_adjusted = emi
                    balance = round(balance - principal_component, 2)

                total_interest += interest_component
                total_principal += principal_component

                schedule.append({
                    'month': month,
                    'emi': emi_adjusted,
                    'principal': principal_component,
                    'interest': interest_component,
                    'balance': balance
                })

            response_msg = {
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_SUCCESS,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_DESCRIPTION_SUCCESS,
                'datas': {
                    'loanAmount': loan_amount,
                    'interestRate': interest_rate,
                    'tenure': tenure,
                    'emi': emi,
                    'totalInterest': round(total_interest, 2),
                    'totalPayment': round(total_principal + total_interest, 2),
                    'emiScheduleData': schedule
                }
            }

            return Response(response_msg, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(str(e), exc_info=True)
            return Response({
                globalparameters.RESULT_CODE: globalparameters.RESULT_CODE_INTERNAL_SERVER_ERROR,
                globalparameters.RESULT_DESCRIPTION: globalparameters.RESULT_INTERNAL_SERVER_ERROR
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
