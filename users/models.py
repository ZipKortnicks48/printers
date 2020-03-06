from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, login, password,**extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            login=login,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self,email,login,password,**extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email,login,password,**extra_fields)
    def create_superuser(self, email, login, password,**extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(email,login,password,**extra_fields)
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=40, unique=True)
    login = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_superuser=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['login']
 
    def __str__(self):              # __unicode__ on Python 2
        return str(self.login)+":"+str(self.email)