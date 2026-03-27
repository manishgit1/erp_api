import json
from master.global_validation import validate_decimal_value, validate_integer_value, validate_by_reference_id
from tools.models import LoanType, LoanPaymentScheme, LoanPurpose
from master.models import ClientMaster
from master import globalparameters
from user_auth.models import generate_uuid


def validate_loan_request(request,db_name,pk):
    json_error = []

    data = json.loads(request.body)
    if not data:
        json_error.append("Please provide loan request details")
        return json_error

    client_code = str(data['loanRequestClientCode']).strip() if 'loanRequestClientCode' in data else ''
    mobile_number = str(data['loanRequestMobileNumber']).strip() if 'loanRequestMobileNumber' in data else ''

    if not mobile_number:
        json_error.append("Invalid Mobile Number Provided")

    client_master = ClientMaster.objects.using(db_name).filter(client_code=client_code,mobile_number=mobile_number)
    if client_master.count() > 1:
        json_error.append("Multiple clients found with the same client code and mobile number")
        return None,json_error
    if not client_master:
        json_error.append("Client not found")
        return None,json_error
    
    client_master = client_master.first()
    
    date_ad = str(data['loanRequestDateAd']).strip() if 'loanRequestDateAd' in data else ''
    if not date_ad:
        json_error.append("Please provide loan request date")
        return None,json_error

    emi_date_ad = str(data['loanRequestDateAd']).strip() if 'loanRequestDateAd' in data else ''
    if not emi_date_ad:
        json_error.append("Please provide loan request EMI date")
        return None,json_error
    
    loan_amount = str(data['loanRequestAmount']).strip() if 'loanRequestAmount' in data else ''
    if not loan_amount:
        json_error.append("Please provide loan amount")
        return None,json_error
    else:
        json_error.extend(validate_decimal_value(loan_amount,'Loan Amount'))
    
    tenure = str(data['loanRequestTenure']).strip() if 'loanRequestTenure' in data else ''
    if not tenure:
        json_error.append("Please provide tenure")
        return None,json_error
    else:
        json_error.extend(validate_integer_value(tenure,'Tenure'))

    interest_rate = str(data['loanRequestInterestRate']).strip() if 'loanRequestInterestRate' in data else ''
    if not interest_rate:
        json_error.append("Please provide interest rate")
        return None,json_error
    else:
        json_error.extend(validate_decimal_value(interest_rate,'Interest Rate'))


    loan_type_id = str(data['loanRequestType']).strip() if 'loanRequestType' in data else ''
    if not loan_type_id:
        json_error.append("Please provide loan type")
        return None,json_error
    else:
        loan_type_id,loan_type_validation_error = validate_by_reference_id(loan_type_id,db_name,LoanType,'Loan Type')
        json_error.extend(loan_type_validation_error)
    
    loan_payment_scheme_id = str(data['loanRequestPaymentScheme']).strip() if 'loanRequestPaymentScheme' in data else ''
    if not loan_payment_scheme_id:
        json_error.append("Please provide loan payment scheme")
        return None,json_error
    else:
        loan_payment_scheme_id,loan_payment_scheme_validation_error = validate_by_reference_id(loan_payment_scheme_id,db_name,LoanPaymentScheme,'Loan Payment Scheme')
        json_error.extend(loan_payment_scheme_validation_error)

    loan_purpose_id = str(data['loanRequestPurpose']).strip() if 'loanRequestPurpose' in data else ''
    if not loan_purpose_id:
        json_error.append("Please provide loan purpose")
        return None,json_error
    else:
        loan_purpose_id,loan_purpose_validation_error = validate_by_reference_id(loan_purpose_id,db_name,LoanPurpose,'Loan Purpose')
        json_error.extend(loan_purpose_validation_error)
    

    loan_request_json = {
        'reference_id': generate_uuid() if pk is None else pk,
        'client_id': client_master.id,
        'loan_type_id': loan_type_id,
        'payment_scheme_id': loan_payment_scheme_id,
        'loan_purpose_id': loan_purpose_id,
        'amount': loan_amount,
        'tenure_months': tenure,
        'action': 'CREATED',
        'interest_rate': interest_rate,
        'date_ad': date_ad,
        'emi_date_ad': emi_date_ad,
        
    } | globalparameters.get_general_json_parameters(request)

    return loan_request_json,json_error
    