from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, name, password=None):
        if not name:
            raise ValueError('Users must have an name')

        user = self.model(
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, name, password):
        user = self.create_user(
            name=name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    def create_kakao_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        user.name = extra_data['properties']['nickname']
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20,blank=False,unique=True)
    image = models.CharField(max_length=200,blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    token = Token

    objects = UserManager()

    USERNAME_FIELD = 'name'

