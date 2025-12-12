import decimal
from django.core.exceptions import ValidationError

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

   