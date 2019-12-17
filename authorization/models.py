from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext as _
from django.conf import settings
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin._auth_utils import UidAlreadyExistsError
import os
import string
import random

 
def generateInviteCode():
    _LENGTH = 6
    string_pool = string.digits + string.ascii_lowercase
    result = ""
    for i in range(_LENGTH):
        result += random.choice(string_pool) 
    return result

class UserManager(BaseUserManager):
    def create_user(self, name, real_name, gender, phone, is_student, belong, department, age, nickname=None, email=None, password=None):
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

    def create_superuser(self, name, password):
        user = self.create_user(
            name=name,
            real_name="MANAGER-"+name,
            gender=1,
            phone='010-0000-0000',
            belong='yamigu',
            department='development',
            is_student = True,
            age=99,
            nickname='manager_'+name,
            email='manager_'+name+'@yamigu.com',
            password=password,
        )
        user.is_admin = True
        user.is_staff = True    
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def create_kakao_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        
        user.name = 'kakao-' + extra_data['properties']['nickname'] + str(extra_data['id'])
        user.uid = str(extra_data['id'])
        user.save(using=self._db)
        print(str(extra_data['id']))
        try:
        	user.image = extra_data['properties']['profile_image']
        except KeyError:
        	pass
       	user.firebase_token = create_token_uid(str(extra_data['id']))
       	try:
       		auth.create_user(uid=user.uid, photo_url=user.image)
       	except UidAlreadyExistsError:
       		pass
       	except ValueError:
            try:
       		    auth.create_user(uid=user.uid)
            except UidAlreadyExistsError:
                pass
        user.save(using=self._db)
        return user

    def create_apple_user(self, user_pk, extra_data):
        user = User.objects.get(pk=user_pk)
        apple_id = extra_data['id'].replace(".", "")
        user.name = 'apple-' +apple_id
        user.uid = apple_id
        user.save(using=self._db)
        print(apple_id)
       	user.firebase_token = create_token_uid(apple_id)
       	try:
       		auth.create_user(uid=user.uid)
       	except UidAlreadyExistsError:
       		pass
        user.save(using=self._db)
        return user

def create_token_uid(uid):

    # [START create_token_uid]
  
    custom_token = auth.create_custom_token(uid)
    custom_token = custom_token.decode('utf-8')
    # [END create_token_uid]
    return custom_token

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, null=True, unique=True)
    uid = models.CharField(max_length=100, null=True, unique=True)
    real_name = models.CharField(max_length=20, null=True)
    gender = models.IntegerField(blank=False, null=True)
    nickname = models.CharField(max_length=20, blank=True, null=True)
    phone_regex = RegexValidator(regex=r'\d{3}[-]?\d{4}[-]?\d{4}', message="Phone number is invalid.")
    phone = models.CharField(_('phone number'), validators=[phone_regex], max_length=14, null=True)
    is_student = models.BooleanField(default=True)
    belong = models.CharField(blank=False, max_length=20, null=True)
    department = models.CharField(blank=False, max_length=20, null=True)
    age = models.IntegerField(blank=False, null=True)
    email = models.EmailField(max_length=70, blank=True)
    image = models.CharField(max_length=200,blank=True)
    user_certified = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    cert_image = models.CharField(max_length=200, blank=True, null=True)
    ticket = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    token = Token
    firebase_token= models.CharField(max_length=1000, null=True, unique=True)
    invite_code = models.CharField(max_length=6, null=True, unique=True)
    push_on = models.BooleanField(default=True)
    chat_on = models.BooleanField(default=True)
    objects = UserManager()
    USERNAME_FIELD = 'name'
    

    def __str__(self):
        real_name = ''
        nickname = ''
        age = 0
        gender = ''
        if(self.real_name):
            real_name = self.real_name
        if(self.nickname):
            nickname = self.nickname
        if(self.age):
            age = self.age
        if(self.gender == 1):
            gender = '남'
        elif(self.gender == 2):
            gender = '여'
        return "%s(%s, %s, %d)" % (nickname, real_name, gender, age)
