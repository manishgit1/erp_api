import decimal
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.dateparse import parse_date

def validate_by_reference_id(reference_id,db_name,model_class,name):
   obj = model_class.objects.using(db_name).filter(is_void=False,reference_id=reference_id)
   error_list = []
   if obj.exists():
      return obj.first().id, error_list
   else:
      error_list.append('Invalid value for ' + name)
      return None, error_list
   


def validate_for_obj(reference_id,db_name,model_class,name):
   obj = model_class.objects.using(db_name).filter(is_void=False,reference_id=reference_id)
   error_list = []
   if obj.exists():
      return obj.first(), error_list
   else:
      error_list.append('Invalid value for ' + name)
      return None, error_list
         
   

def validate_decimal_value(value, name):

    try:
        error_list = []
        val = decimal.Decimal(value)
        if val < 0:
            error_list.append(name +" value cannot be negative")
        
        return error_list
    except (decimal.InvalidOperation, TypeError):
        error_list.append("Enter a valid decimal number.")
        return error_list

def validate_integer_value(value, name):
    error_list = []
    try:
        val = int(value)
        if val < 0:
            error_list.append(name + " value cannot be negative")
    except (ValueError, TypeError):
        error_list.append("Enter a valid integer for " + name)
    return error_list

def validate_boolean_value(value, name):
    error_list = []
    if isinstance(value, bool):
        return error_list
    if str(value).lower() in ['true', 'false', '1', '0', 'yes', 'no']:
        return error_list
    error_list.append("Enter a valid boolean for " + name)
    return error_list

def validate_date_value(value, name):
    error_list = []
    if not value:
        return error_list
    if parse_date(str(value)) is None:
        error_list.append("Enter a valid date (YYYY-MM-DD) for " + name)
    return error_list

def validate_email_value(value, name):
    error_list = []
    if not value:
        return error_list
    try:
        validate_email(value)
    except ValidationError:
        error_list.append("Enter a valid email address for " + name)
    return error_list

def validate_mobile_number(value, name):
    error_list = []
    if not value:
        return error_list
    if not re.match(r'^\d{10}$', str(value)):
        error_list.append("Enter a valid 10-digit mobile number for " + name)
    return error_list

   

   