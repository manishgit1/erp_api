from rest_framework import serializers
from user_auth.models import User, UserRole
from rest_framework.validators import ValidationError
import re


class UserSerializer(serializers.ModelSerializer):  
    firstName = serializers.CharField(max_length=100, source='first_name')
    lastName = serializers.CharField(max_length=100, source='last_name')
    phoneNumber = serializers.CharField(max_length=20, source='phone_number', required=False, allow_blank=True)
    referenceId = serializers.CharField(source='reference_id', read_only=True)
    status = serializers.BooleanField(source='is_active', default=True)
    fullName = serializers.CharField(source='full_name', read_only=True)
    role = serializers.SlugRelatedField(slug_field='reference_id', queryset=UserRole.objects.all(), required=False, allow_null=True)
    roleName = serializers.CharField(source='role.name',read_only=True)
    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['referenceId', 'username', 'password', 'firstName', 'lastName', 'email',
        'roleName', 'phoneNumber', 'role', 'status', 'fullName', 'createdAt']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'role': {'required': False}
        }

    def get_createdAt(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M')
        return None

    

    

    def create(self, validated_data):  
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        user = User.objects.create(
            reference_id=self.context.get('reference_id'),
            role=role,
            **validated_data
        )
        if password:
            user.set_password(password) 
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class UserRoleSerializer(serializers.ModelSerializer):
    roleCode = serializers.CharField(source='role_code', allow_blank=True, required=False)
    referenceId = serializers.CharField(source='reference_id', read_only=True)
    remarks = serializers.CharField(source='description', allow_blank=True, required=False)
    isActive = serializers.BooleanField(source='is_active', required=False)

    class Meta:
        model = UserRole
        fields = ['referenceId', 'name', 'roleCode', 'remarks', 'isActive']

    def create(self, validated_data):
        db_name = self.context.get('db_name')
        return UserRole.objects.using(db_name).create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.role_level = validated_data.get('role_level', instance.role_level)
        instance.description = validated_data.get('description', instance.description)
        instance.save(using=self.context.get('db_name'))
        return instance