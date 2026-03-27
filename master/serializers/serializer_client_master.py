
from rest_framework import serializers
from master.models import ClientMaster, GlobalDistrict, GlobalProvince, GlobalVdcMunicipality
from tools.models import ClientTypeGender, NomineeRelation, LegalStatus, RegistrationAuthority

class ReferenceIdField(serializers.Field):
    """
    A field that represents a foreign key by its reference_id.
    Accepts a reference_id string on write and returns a reference_id string on read.
    """
    def to_representation(self, value):
        if value and hasattr(value, 'reference_id'):
            return value.reference_id
        return None

    def to_internal_value(self, data):
        return data

class ClientMasterSerializer(serializers.ModelSerializer):
    clientMasterFirstName = serializers.CharField(source='first_name', error_messages={'required': 'First Name is required!'})
    clientMasterMiddleName = serializers.CharField(source='middle_name', required=False, allow_null=True, allow_blank=True)
    clientMasterLastName = serializers.CharField(source='last_name', error_messages={'required': 'Last Name is required!'})
    
    clientMasterMobileNumber = serializers.CharField(source='mobile_number', required=False, allow_null=True, allow_blank=True)
    clientMasterContactNumber = serializers.CharField(source='contact_number', required=False, allow_null=True, allow_blank=True)
    
    # Address
    clientMasterPermanentMunicipality = ReferenceIdField(source='permanent_municipality')
    clientMasterPermanentDistrict = ReferenceIdField(source='permanent_district')
    clientMasterPermanentProvince = ReferenceIdField(source='permanent_province')
    clientMasterPermanentWardNo = serializers.CharField(source='permanent_ward_number', required=False, allow_null=True, allow_blank=True)
    clientMasterPermanentStreet = serializers.CharField(source='permanent_street', required=False, allow_null=True, allow_blank=True)

    clientMasterTemporaryMunicipality = ReferenceIdField(source='temp_municipality', required=False, allow_null=True)
    clientMasterTemporaryDistrict = ReferenceIdField(source='temp_district', required=False, allow_null=True)
    clientMasterTemporaryProvince = ReferenceIdField(source='temp_province', required=False, allow_null=True)
    clientMasterTemporaryWardNo = serializers.CharField(source='temp_ward_number', required=False, allow_null=True, allow_blank=True)
    clientMasterTemporaryStreet = serializers.CharField(source='temp_street', required=False, allow_null=True, allow_blank=True)


    clientMasterPermanentMunicipalityName = serializers.CharField(source='permanent_municipality.name', read_only=True)
    clientMasterPermanentDistrictName = serializers.CharField(source='permanent_district.name', read_only=True)
    clientMasterPermanentProvinceName = serializers.CharField(source='permanent_province.name', read_only=True)

    clientMasterTemporaryMunicipality = ReferenceIdField(source='temp_municipality', required=False, allow_null=True)
    clientMasterTemporaryDistrict = ReferenceIdField(source='temp_district', required=False, allow_null=True)
    clientMasterTemporaryProvince = ReferenceIdField(source='temp_province', required=False, allow_null=True)
    
    clientMasterTemporaryMunicipalityName = serializers.CharField(source='temp_municipality.name', read_only=True)
    clientMasterTemporaryDistrictName = serializers.CharField(source='temp_district.name', read_only=True)
    clientMasterTemporaryProvinceName = serializers.CharField(source='temp_province.name', read_only=True)
    # Personal
    clientMasterDateOfBirth = serializers.DateField(source='date_of_birth_ad', required=False, allow_null=True)
    clientMasterGender = ReferenceIdField(source='gender', required=False, allow_null=True)
    clientMasterNationality = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    clientMasterSalutation = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    clientMasterCitizenshipNumber = serializers.CharField(source='citizenship_number', required=False, allow_null=True, allow_blank=True)
    clientMasterCitizenshipIssuedDistrict = ReferenceIdField(source='citizenship_issued_district', required=False, allow_null=True)
    clientMasterCitizenshipIssuedDate = serializers.DateField(source='citizenship_issued_date_ad', required=False, allow_null=True)

    # Business
    clientMasterBusinessName = serializers.CharField(source='business_name', required=False, allow_null=True, allow_blank=True)
    clientMasterOrganization = serializers.CharField(source='organization_name', required=False, allow_null=True, allow_blank=True)
    clientMasterPanNumber = serializers.CharField(source='pan_number', required=False, allow_null=True, allow_blank=True)
    clientMasterVatNumber = serializers.CharField(source='vat_number', required=False, allow_null=True, allow_blank=True)
    clientMasterCompanyRegistrationNumber = serializers.CharField(source='registration_number', required=False, allow_null=True, allow_blank=True)

    referenceId = serializers.ReadOnlyField(source='reference_id')
    
    class Meta:
        model = ClientMaster
        fields = [
            'clientMasterFirstName', 'clientMasterMiddleName', 'clientMasterLastName',
            'clientMasterMobileNumber', 'clientMasterContactNumber',
            'clientMasterPermanentMunicipality', 'clientMasterPermanentDistrict', 'clientMasterPermanentProvince',
            'clientMasterPermanentWardNo', 'clientMasterPermanentStreet',
            'clientMasterTemporaryMunicipality', 'clientMasterTemporaryDistrict', 'clientMasterTemporaryProvince',
            'clientMasterTemporaryWardNo', 'clientMasterTemporaryStreet',
            'clientMasterDateOfBirth', 'clientMasterGender', 'clientMasterNationality', 'clientMasterSalutation',
            'clientMasterCitizenshipNumber', 'clientMasterCitizenshipIssuedDistrict', 'clientMasterCitizenshipIssuedDate',
            'clientMasterBusinessName', 'clientMasterOrganization', 'clientMasterPanNumber', 'clientMasterVatNumber',
            'clientMasterCompanyRegistrationNumber', 'referenceId','clientMasterPermanentMunicipalityName', 'clientMasterPermanentDistrictName', 'clientMasterPermanentProvinceName', 'clientMasterTemporaryMunicipalityName', 'clientMasterTemporaryDistrictName', 'clientMasterTemporaryProvinceName'
        ]

    def validate_clientMasterGender(self, value):
        if not value: return None
        return self._validate_entity(value, ClientTypeGender, "Invalid Gender")

    def validate_clientMasterPermanentMunicipality(self, value):
        return self._validate_entity(value, GlobalVdcMunicipality, 'Invalid Permanent Municipality')

    def validate_clientMasterPermanentDistrict(self, value):
        return self._validate_entity(value, GlobalDistrict, 'Invalid Permanent District')

    def validate_clientMasterPermanentProvince(self, value):
        return self._validate_entity(value, GlobalProvince, 'Invalid Permanent Province')

    def validate_clientMasterTemporaryMunicipality(self, value):
        if not value: return None
        return self._validate_entity(value, GlobalVdcMunicipality, 'Invalid Temporary Municipality')

    def validate_clientMasterTemporaryDistrict(self, value):
        if not value: return None
        return self._validate_entity(value, GlobalDistrict, 'Invalid Temporary District')
        
    def validate_clientMasterTemporaryProvince(self, value):
        if not value: return None
        return self._validate_entity(value, GlobalProvince, 'Invalid Temporary Province')

    def validate_clientMasterCitizenshipIssuedDistrict(self, value):
        if not value: return None
        return self._validate_entity(value, GlobalDistrict, 'Invalid Citizenship Issued District')

    def _validate_entity(self, value, model, error_msg):
        db_name = self.context.get('db_name')
        entity = model.objects.using(db_name).filter(reference_id=value).first()
        if entity:
            return entity
        raise serializers.ValidationError(error_msg)

    def create(self, validated_data):
        db_name = self.context.get('db_name')
        
        # Handle fields not in model or ignore them
        validated_data.pop('clientMasterNationality', None)
        validated_data.pop('clientMasterSalutation', None)
        
        return ClientMaster.objects.using(db_name).create(**validated_data)
