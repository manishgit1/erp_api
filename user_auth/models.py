from master.models.models_contact_master import GenericIdEntity
from contextlib import nullcontext
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from django.utils import timezone


def generate_uuid():
    return str(uuid.uuid4().hex)

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(username=username)


class User(AbstractBaseUser, PermissionsMixin):
    # email = models.EmailField(unique=True, max_length=255)
    id = models.BigAutoField(primary_key=True)
    reference_id = models.CharField(max_length=100)
    username = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=128) 
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.ForeignKey('UserRole', on_delete=models.PROTECT, related_name='+', db_column='role_id', null=True, blank=True)
    # remarks = models.TextField(null=True, blank=True)
    # dob = models.DateField(null=True, blank=True)  
    last_login = models.DateTimeField(null=True, blank=True)  
    temp_session_id = models.CharField(max_length=100, null=True, blank=True) 
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now) 
    max_login_attempts = models.PositiveIntegerField(null=True, blank=True)


    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    objects = UserManager()

    class Meta:
        managed = True 
        db_table = "erp_users"  

    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return self.first_name + " " + self.last_name

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='+')
    session_id = models.CharField(unique=True)
    created_at = models.DateTimeField()
    expiry_date = models.DateTimeField()

    class Meta:
        managed=False
        db_table = "user_session"

    def save(self, *args, **kwargs):
        if self.expiry_date and timezone.is_naive(self.expiry_date):
            self.expiry_date = timezone.make_aware(self.expiry_date)

        super().save(*args, **kwargs)


class UserRole(GenericIdEntity):
   
    name = models.CharField(max_length=100)
    role_level = models.PositiveIntegerField()
    role_code = models.CharField(blank=True,null=True,max_length=200)
    description = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+',db_column='created_by')
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+',db_column='updated_by')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "roles"
        managed = False