from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, real_name, gender, phone, is_student, belong, department, age, nickname=None, email=None, password=None):
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
            real_name=real_name,
            gender=gender,
            phone=phone,
            is_student=is_student,
            belong=belong,
            department=department,
            age=age,
            nickname=nickname,
            email=email
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id, password):
        user = self.create_user(
            real_name="MANAGER"+str(id),
            gender=1,
            phone='010-0000-0000',
            belong='yamigu',
            department='development',
            is_student = True,
            age=99,
            nickname='manager'+str(id),
            email='manager'+str(id)+'@yamigu.com',
            password=password,
        )
        user.is_admin = True
        user.is_staff = True    
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_kakao_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        
        user.name = extra_data['properties']['nickname'] + str(extra_data['id'])
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=20, null=True, unique=True)
    real_name = models.CharField(max_length=20, null=True)
    gender = models.IntegerField(blank=False, null=True)
    nickname = models.CharField(max_length=20, blank=True, null=True, unique=True)
    phone_regex = RegexValidator(regex=r'\d{3}[-]?\d{4}[-]?\d{4}', message="Phone number is invalid.")
    phone = models.CharField(_('phone number'), validators=[phone_regex], max_length=14, null=True)
    is_student = models.BooleanField(default=True)
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
    def __str__(self):
        return str(self.id)
