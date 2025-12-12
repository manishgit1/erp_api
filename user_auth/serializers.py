from rest_framework import serializers
from user_auth.models import User
from rest_framework.validators import ValidationError
import re


class UserSerializer(serializers.ModelSerializer):  
    firstName = serializers.CharField(max_length=100, source='first_name')
    lastName = serializers.CharField(max_length=100, source='last_name')
    class Meta:
        model = User
        fields = ['username', 'password', 'firstName', 'lastName']


    def create(self, validated_data):  
        user = User.objects.create(
            reference_id = self.context.get('reference_id'),
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password']) 
        user.save()
        return user