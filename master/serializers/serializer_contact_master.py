
from rest_framework import serializers
from master.models import ContactMaster, GlobalDistrict, GlobalProvince, GlobalVdcMunicipality

class GlobalContactSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name', error_messages = {'required': 'First Name is required!', 'blank': 'First Name cannot be blank!'})
    middleName = serializers.CharField(source='middle_name',required=False,allow_blank=True)
    lastName = serializers.CharField(source='last_name', error_messages = {'required': 'Last Name is required!', 'blank': 'Last Name cannot be blank!'})
    # alias = serializers.CharField(required=False, allow_null=True)
    contactNumber = serializers.CharField(source='contact_number',required=False,allow_blank=True)
    mobileNumber = serializers.CharField(source='mobile_number',error_messages = {'required': 'Mobile Number is required!', 'blank': 'Mobile Number cannot be blank!'})
    # dateOfBirthBs = serializers.CharField(source='date_of_birth_bs', error_messages = {'required': 'Date of Birth BS is required!', 'blank': 'Date of Birth BS cannot be blank!'})
    # dateOfBirthAd = serializers.DateField(source='date_of_birth_ad')
    # fatherName = serializers.CharField(source='father_name', required=False)
    # motherName = serializers.CharField(source='mother_name')
    # grandFatherName = serializers.CharField(source='grandfather_name')
    citizenshipNumber = serializers.CharField(source='citizenship_number', error_messages = {'required': 'Citizenship Number is required!', 'blank': 'Citizenship Number cannot be blank!'})
    citizenshipIssuedDateAd = serializers.DateField(source='citizenship_issued_date_ad')
    citizenshipIssuedDateBs = serializers.CharField(source='citizenship_issued_date_bs')
    citizenshipIssuedDistrictId = serializers.CharField(source='citizenship_issued_district', write_only=True)
    citizenshipIssuedDistrict = serializers.ReadOnlyField(source='citizenship_issued_district.reference_id')
   #  citizenshipIssuedDistrictName = serializers.SerializerMethodField()
   #  familySize = serializers.IntegerField(source='family_size', required=False, allow_null=True)
   #  occupation = serializers.CharField(required=False, allow_null=True)
    # tempDistrictId = serializers.CharField(source='temp_district',write_only=True)
    # tempDistrict = serializers.ReadOnlyField(source='temp_district.reference_id')
    # tempDistrictName = serializers.SerializerMethodField()
    # tempMunicipalityId = serializers.CharField(source='temp_vdc_municipality', write_only=True)
    # tempMunicipality = serializers.ReadOnlyField(source='temp_vdc_municiaplity.reference_id')
    # tempMunicipalityName = serializers.SerializerMethodField()
    # tempProvinceId = serializers.CharField(source='temp_province')
    # tempProvince = serializers.ReadOnlyField(source='temp_province.reference_id')
    # tempProvinceName = serializers.SerializerMethodField()
    permanentDistrictId = serializers.CharField(source ='permanent_district')
    permanentDistrict = serializers.ReadOnlyField(source='permanent_district.reference_id')
    permanentDistrictName = serializers.SerializerMethodField()
    permanentMunicipalityId = serializers.CharField(source='permanent_vdc_municipality')
    permanentMunicipality = serializers.ReadOnlyField(source='permanent_vdc_municipality.reference_id')
    permanentMunicipalityName =serializers.SerializerMethodField()
    permanentProvinceId = serializers.CharField(source='permanent_province')
    permanentProvince = serializers.ReadOnlyField(source='permanent_province.reference_id')
    permanentWardNo = serializers.CharField(source='permanent_ward_number', required=False, allow_blank=True)
    referenceId = serializers.ReadOnlyField(source='reference_id')
    email = serializers.CharField(required=False,allow_blank=True)   

    class Meta:
        model = ContactMaster
        fields = [  'firstName', 'middleName','referenceId',
                    'lastName', 'email', 
                    'contactNumber', 'mobileNumber',
                    'citizenshipNumber', 'citizenshipIssuedDateAd', 
                    'citizenshipIssuedDateBs',
                    'permanentDistrictId', 'permanentDistrict', 
                    'permanentMunicipalityId','permanentMunicipality', 'permanentProvinceId', 'permanentProvince', 'email',
                    'citizenshipIssuedDistrictId', 'citizenshipIssuedDistrict', 'permanentDistrictName', 'permanentMunicipalityName', 'permanentWardNo'
                  ]

       
    def validate_citizenshipIssuedDistrictId(self,value):
       db_name = self.context.get('db_name')
       citizenship_issued_district = GlobalDistrict.objects.using(db_name).filter(reference_id=value).first()
       if citizenship_issued_district is not None:
          return citizenship_issued_district
       else:
          raise serializers.ValidationError('Invalid Citizenship Issued District Provided')

    def validate_mobileNumber(self,value):
      db_name = self.context.get('db_name')
      mobile_number = ContactMaster.objects.using(db_name).filter(mobile_number=value).first()
      if mobile_number is not None:
         raise serializers.ValidationError('Mobile Number Already Exists')
      return value
    # def validate_tempDistrictId(self,value):
    #    db_name = self.context.get('db_name')
    #    temp_district = GlobalDistrict.objects.using(db_name).filter(reference_id=value).first()
    #    if temp_district is not None:
    #       return temp_district
    #    else:
    #       raise serializers.ValidationError('Invalid Temporary District Provided')
    # def validate_tempMunicipalityId(self,value):
    #    db_name = self.context.get('db_name')
    #    temp_municipality = GlobalVdcMunicipality.objects.using(db_name).filter(reference_id=value).first()
    #    if temp_municipality is not None:
    #       return temp_municipality
    #    else:
    #       raise serializers.ValidationError('Invalid Temporary Municipality Provided')
    # def validate_tempProvinceId(self,value):
    #    db_name = self.context.get('db_name')
    #    temp_province = GlobalProvince.objects.using(db_name).filter(reference_id=value).first()
    #    if temp_province is not None:
    #       return temp_province
    #    else:
    #       raise serializers.ValidationError('Invalid Temporary Province Provided')
    def validate_permanentMunicipalityId(self,value):
       db_name = self.context.get('db_name')
       permanent_municipality = GlobalVdcMunicipality.objects.using(db_name).filter(reference_id=value).first()
       if permanent_municipality is not None:
          return permanent_municipality
       else:
          raise serializers.ValidationError('Invalid Permanent Municipality Provided')
    def validate_permanentProvinceId(self,value):
       db_name = self.context.get('db_name')
       permanent_province = GlobalProvince.objects.using(db_name).filter(reference_id=value).first()
       if permanent_province is not None:
          return permanent_province
       else:
          raise serializers.ValidationError('Invalid Permanent Province Provided')
    def validate_permanentDistrictId(self,value):
       db_name = self.context.get('db_name')
       permanent_district = GlobalDistrict.objects.using(db_name).filter(reference_id=value).first()
       if permanent_district is not None:
          return permanent_district
       else:
          raise serializers.ValidationError('Invalid Permanent District Provided')
    
   #  def get_citizenshipIssuedDistrictName(self,obj):
   #      if obj.citizenship_issued_district is not None:
   #         return obj.citizenship_issued_district.name
   #      else :
   #         return ''
    
    def get_permanentDistrictName(self,obj):
        if obj.permanent_district_id is not None:
           return obj.permanent_district.name
        else :
           return ''
    
    def get_permanentMunicipalityName(self,obj):
        if obj.permanent_vdc_municipality_id is not None:
           return obj.permanent_vdc_municipality.name
        else :
           return ''
    
 
    def create(self, validated_data):
      db_name = self.context.get('db_name')
      return ContactMaster.objects.using(db_name).create(**validated_data)

   
   
    
   #  def create(self,**validated_data):
   #     return super().create(**validated_data)