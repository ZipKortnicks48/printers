from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from city.models import City

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, name, password,**extra_fields):
        user = self.model(
            name=name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self,name,password,**extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(self,name,password,**extra_fields)
    def create_superuser(self, name, password,**extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(name,password,**extra_fields)
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=30, blank=True,unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    mobile_phone=models.CharField(max_length=10,blank=True,null=True)
    phone=models.CharField(max_length=10,blank=True,null=True)
    surname=models.CharField(max_length=30,blank=True,null=True)
    city=models.ForeignKey(City,related_name="user_have_city",on_delete=models.CASCADE,blank=True,null=True)
    email=models.CharField(max_length=100,blank=True,default="")
    objects = UserManager()
    
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []
 
    def __str__(self):              # __unicode__ on Python 2
        return self.name