# authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

api_urlpattern = [
    path('auth/', include('rest_auth.urls')),
    path('user/info/', UserInfoView.as_view()),
    path('user/change/nickname/', ChangeNicknameView.as_view()),
    path('oauth/kakao/', KakaoLoginView.as_view(), name='socialaccount_signin'),
    path('user/validation/nickname/<nickname>', NicknameValidator.as_view()),
    path('auth/signup/', SignUpView.as_view()),
    path('user/certificate/', CertificateView.as_view()),
    path('user/change/avata/',  ChangeAvataView.as_view()),
]