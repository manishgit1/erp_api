from django.utils.translation.template import blankout
from django.db import models
from master.models import GenericIdEntity, GlobalDistrict, GlobalProvince, GlobalVdcMunicipality,ContactMaster
from tools.models import NomineeRelation, LegalStatus, RegistrationAuthority,ClientTypeGender

class ClientMaster(GenericIdEntity):
 
    client_code = models.CharField(max_length=50)
    
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15)
    contact_number = models.CharField(max_length=15,blank=True,null=True)
    gender = models.ForeignKey(ClientTypeGender,on_delete=models.PROTECT,blank=True,null=True)
    date_of_birth_ad = models.DateField(blank=True, null=True)
    date_of_birth_bs = models.CharField(max_length=10, blank=True, null=True)
    grandfather_name = models.CharField(max_length=100, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)

    identity_number = models.CharField(max_length=50, blank=True, null=True)
    citizenship_number = models.CharField(max_length=50, blank=True, null=True)
    identity_issued_district = models.ForeignKey(GlobalDistrict, related_name='+', on_delete=models.PROTECT, blank=True, null=True)
    citizenship_issued_district = models.ForeignKey(GlobalDistrict, related_name='+', on_delete=models.PROTECT, blank=True, null=True)
    identity_issued_date_ad = models.DateField(blank=True, null=True)
    identity_issued_date_bs = models.CharField(max_length=10, blank=True, null=True)
    citizenship_issued_date_ad = models.DateField(blank=True, null=True)
    citizenship_issued_date_bs = models.CharField(max_length=10, blank=True, null=True)

    permanent_municipality = models.ForeignKey(GlobalVdcMunicipality, related_name='+', on_delete=models.PROTECT, blank=True, null=True)
    permanent_ward_number = models.CharField(max_length=10, blank=True, null=True)
    permanent_street = models.CharField(max_length=255, blank=True, null=True)
    permanent_district = models.ForeignKey(GlobalDistrict, related_name='+', on_delete=models.PROTECT, blank=True, null=True)
    permanent_province = models.ForeignKey(GlobalProvince, related_name='+', on_delete=models.PROTECT, blank=True, null=True)

    temp_municipality = models.ForeignKey(GlobalVdcMunicipality, related_name='+', on_delete=models.PROTECT, blank=True, null=True)
    temp_ward_number = models.CharField(max_length=10, blank=True, null=True)
    temp_street = models.CharField(max_length=255, blank=True, null=True)
    temp_district = models.ForeignKey(GlobalDistrict, related_name='+', on_delete=models.PROTECT, blank=True, null=True)
    temp_province = models.ForeignKey(GlobalProvince, related_name='+', on_delete=models.PROTECT, blank=True, null=True)

    nominee_name = models.CharField(max_length=255, blank=True, null=True)
    nominee_relation = models.ForeignKey(NomineeRelation, on_delete=models.PROTECT, blank=True, null=True)
    nominee_phone_number = models.CharField(max_length=20, blank=True, null=True)
    nominee_date_of_birth_ad = models.DateField(blank=True, null=True)
    nominee_date_of_birth_bs = models.CharField(max_length=10, blank=True, null=True)

    business_name = models.CharField(max_length=100, blank=True, null=True)
    # legal_status = models.ForeignKey('legal_status', on_delete=models.SET_NULL, blank=True, null=True)
    legal_status = models.ForeignKey(LegalStatus,on_delete=models.PROTECT,blank=True,null=True)
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    # registration_authority = models.ForeignKey('registration_authority', on_delete=models.SET_NULL, blank=True, null=True)
    registration_authority = models.ForeignKey(RegistrationAuthority,on_delete=models.PROTECT,blank=True,null=True)
    registration_number = models.CharField(max_length=50, blank=True, null=True)
    pan_number = models.CharField(max_length=50, blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)

    global_contact = models.ForeignKey(ContactMaster,on_delete=models.PROTECT,blank=True,null=True)

    is_void = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.IntegerField(blank=True, null=True,db_column='created_by')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_by = models.IntegerField(blank=True, null=True,db_column='updated_by')
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "client_master"
        managed = False


    @property
    def full_name(self):
        """Returns the full name of the client."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(filter(None, parts))

    @property
    def permanent_address(self):
        """Returns the permanent address of the client."""
        return f"{self.permanent_municipality.name} - {self.permanent_ward_number}, {self.permanent_district.name}, {self.permanent_province.name}"

    @property
    def temporary_address(self):
        """Returns the temporary address of the client."""
        return f"{self.temp_municipality.name} - {self.temp_ward_number}, {self.temp_district.name}, {self.temp_province.name}"
