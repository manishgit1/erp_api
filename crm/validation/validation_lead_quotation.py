import json
from master.models import ContactMaster
from master.global_validation import validate_by_reference_id, validate_decimal_value
from tools.models import LoanType, LeadSource
import datetime
from crm.models import LeadQuotation
from django.db.models import  Max
from user_auth.models import generate_uuid

def generate_quotation_number(db_name):
   max_number = LeadQuotation.objects.using(db_name).aggregate(
      Max("quotation_number")
   )["quotation_number__max"]

   if max_number:
      return int(max_number + 1)
   return 2


def validate_lead_quotation(request,db_name,pk):
   data = json.loads(request.body)

   json_error = []

   mobileNumber = str(data['mobileNumber']).strip() if 'mobileNumber' in data else ''
   global_contact = ContactMaster.objects.using(db_name).filter(is_void=False,mobile_number=mobileNumber)
   if global_contact.exists():
      pass
   else:
      json_error.append('Contact Master Data Not Found')
   if json_error:
      return None,json_error
   
   request_type = str(data['requestType']).strip() if 'requestType' in data else ''

   cic_status = str(data['cicStatus']).strip() if 'cicStatus' in data  else ''
   
   loan_type_id = str(data['loanType']).strip() if 'loanType' in data else ''
   loan_type_id,loan_type_error_list = validate_by_reference_id(loan_type_id,db_name,LoanType, 'Loan Type')
   json_error.extend(loan_type_error_list)

   lead_source_id = str(data['leadSource']).strip() if 'leadSource' in data else ''
   lead_source_id, lead_source_error_list = validate_by_reference_id(lead_source_id, db_name, LeadSource, 'Lead Source')
   json_error.extend(lead_source_error_list)

   loan_amount = str(data['loanAmount']).strip() if 'loanAmount' in data else ''
   json_error.extend(validate_decimal_value(loan_amount,'Loan Amount'))
   
   interest_rate = data['interestRate'] if 'interestRate' in data else ''

   tenure = data['tenure'] if 'tenure' in data else ''
   remarks = str(data['remarks']).strip() if 'remarks' in data else ''


   if json_error:
      return None, json_error
   reference_id = pk if pk else generate_uuid()
   
   lead_quotation_json = {
      'reference_id':reference_id,
      'contact_id': global_contact.first().id,
      'cic_status': cic_status,
      'loan_type_id': loan_type_id,
      'source_id': lead_source_id,
      'purpose_code_id': None,
      'next_follow_up_days': None,
      'follow_up_1_remarks': None,
      'follow_up_2_remarks': None,
      'follow_up_3_remarks': None,
      'follow_up_4_remarks': None,
      'net_price': None,
      'loan_amount': loan_amount,
      'tenure': int(tenure),
      'created_at': str(datetime.datetime.now()),
      'created_by': None,
      'updated_by': None,
      'updated_at': None,
      'interest_rate': interest_rate,
      'remarks': str(remarks),
      'is_void': False,
      'status': 0,
      'remarks': remarks,
      'quotation_number': generate_quotation_number(db_name)

      #TODO: update created_by after adding authentication log in 
      
   }

   return lead_quotation_json, json_error


   
   


   