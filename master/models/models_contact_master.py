from django.db import models
from uuid import uuid4
# Create your models here.

def generate_uuid():
  return str(uuid4().hex)

class GenericIdEntity(models.Model):
  id = models.BigAutoField(primary_key=True, unique=True, blank=False, null=False)
  reference_id = models.CharField(max_length=32, default=generate_uuid())

  class Meta:
    abstract = True
 

class GenericEntity(GenericIdEntity):
  name = models.CharField(max_length=100)
  name_in_nepali = models.CharField(max_length=100)

  alias = models.CharField(max_length=100)

  remarks = models.CharField(max_length=200, blank=True, null=True)
  remarks_in_nepali = models.CharField(max_length=200, blank=True, null=True)
  is_void = models.BooleanField(default=False)
  created_by = models.ForeignKey("user_auth.User",db_column='created_by', on_delete=models.PROTECT, related_name='+')
  created_at = models.DateTimeField()
  updated_by = models.ForeignKey("user_auth.User",db_column='updated_by', on_delete=models.PROTECT, related_name='+')
  updated_at = models.DateTimeField() 


  class Meta:
    abstract = True



class GlobalProvince(GenericIdEntity):

  name = models.CharField(max_length=100)
  alias = models.CharField(max_length=100)
  
  class Meta:
    db_table = 'global_province'
    managed = False


class GlobalDistrict(GenericIdEntity):
  name = models.CharField(max_length=100)
  alias = models.CharField(max_length=100)
  province = models.ForeignKey(GlobalProvince, on_delete=models.PROTECT)

  class Meta:
    db_table = 'global_district'
    managed = False 
 

class GlobalVdcMunicipality(GenericIdEntity):
  name = models.CharField(max_length=100)
  alias = models.CharField(max_length=100)
  district = models.ForeignKey(GlobalDistrict, on_delete=models.PROTECT)

  class Meta:
    db_table  = 'global_vdc_municipality'


  
class ContactMaster(GenericIdEntity):
   first_name = models.CharField(max_length=100)
   middle_name = models.CharField(max_length=100, blank=True, null=True)
   last_name = models.CharField(max_length=100)
   # alias = models.CharField(max_length=100, blank=True, null=True)
   mobile_number = models.CharField(max_length=30)
   contact_number = models.CharField(max_length=30, blank=True, null=True)
   email = models.CharField(max_length=50, blank=True,null=True)

   # date_of_birth_ad = models.DateField()
   # date_of_birth_bs = models.CharField(max_length=100)
   # father_name = models.CharField(max_length=100)
   # mother_name = models.CharField(max_length=100, blank=True, null=True)
   # grandfather_name = models.CharField(max_length=100)
   citizenship_number = models.CharField(max_length=100)
   citizenship_issued_date_ad = models.DateField()
   citizenship_issued_date_bs = models.CharField(max_length=100)
   citizenship_issued_district = models.ForeignKey(GlobalDistrict, on_delete=models.PROTECT, related_name='+')
  #  family_size = models.PositiveIntegerField()
  #  occupation = models.CharField(max_length=100)
   permanent_district = models.ForeignKey(GlobalDistrict, on_delete=models.PROTECT, related_name='+')
   permanent_province = models.ForeignKey(GlobalProvince, on_delete=models.PROTECT, related_name='+')
   permanent_vdc_municipality = models.ForeignKey(GlobalVdcMunicipality, on_delete=models.PROTECT, related_name='+')
   permanent_ward_number = models.CharField(max_length=100,blank=True,null=True)
   # temp_district = models.ForeignKey(GlobalDistrict, on_delete=models.PROTECT, related_name='+')
   # temp_province = models.ForeignKey(GlobalProvince, on_delete=models.PROTECT, related_name='+')
   # temp_vdc_municipality = models.ForeignKey(GlobalVdcMunicipality, on_delete=models.PROTECT, related_name='+')

   created_by = models.ForeignKey("user_auth.User",db_column='created_by', on_delete=models.PROTECT, related_name='+')
   created_at = models.DateTimeField()
   updated_by = models.ForeignKey("user_auth.User",db_column='updated_by', on_delete=models.PROTECT, related_name='+')
   updated_at = models.DateTimeField()
   is_void = models.BooleanField(default=False)

   
     

   class Meta:
     db_table = 'global_client_contact'
     managed = False