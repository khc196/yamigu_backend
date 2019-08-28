from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, name, gender, phone, belong, department, age, nickname=None, email=None, password=None):
        if not name:
            raise ValueError('Users must have a name')
        if not gender:
            raise ValueError('Users must have a gender')
        if not phone:
            raise ValueError('Users must have a phone')
        if not belong:
            raise ValueError('Users must have a belong ')
        if not department:
            raise ValueError('Users must have a department')
        if not age:
            raise ValueError('Users must have an age')

        user = self.model(
            name=name,
            gender=gender,
            phone=phone,
            belong=belong,
            department=department,
            age=age,
            nickname=nickname,
            email=email
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password):
        user = self.create_user(
            name=name,
            gender=1,
            phone='010-0000-0000',
            belong='yamigu',
            department='development',
            age=99,
            nickname=name,
            email=name+'@yamigu.com',
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_kakao_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        # user.name = extra_data['properties']['nickname']
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20, blank=False, unique=True)
    gender = models.IntegerField(blank=False, null=True)
    nickname = models.CharField(max_length=20, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'd{3}[- ]?\d{4}[- ]?\d{4}', message="Phone number is invalid.")
    phone = models.CharField(_('phone number'), validators=[phone_regex], max_length=14, null=True)
    belong = models.CharField(blank=False, max_length=20, null=True)
    department = models.CharField(blank=False, max_length=20, null=True)
    age = models.IntegerField(blank=False, null=True)
    email = models.EmailField(max_length=70, blank=True)
    is_certified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    token = Token
    objects = UserManager()

    USERNAME_FIELD = 'name'
