# authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

api_urlpattern = [
    path('auth/', include('rest_auth.urls')),
    path('user/info/', UserInfoView.as_view()),
    path('user/change/nickname/', ChangeNicknameView.as_view()),
    path('oauth/kakao/', KakaoLoginView.as_view(), name='socialaccount_signin'),
    path('oauth/apple/', AppleLoginView.as_view()),
    path('user/validation/nickname/<nickname>', NicknameValidator.as_view()),
    path('auth/signup/', SignUpView.as_view()),
    path('auth/verify/', VerifyView.as_view()),
    path('user/certificate/', CertificateView.as_view()),
    path('user/change/avata/',  ChangeAvataView.as_view()),
    path('buyticket/', BuyTicketView.as_view()),
    path('user/<uid>/image/', ImageURLView.as_view()),
    path('manager/certificate/user/', CertificateAdminView.as_view()),
    path('auth/withdrawal/', WithdrawalView.as_view()),
    path('turn_on/chat/', TurnOnChat.as_view()),
    path('turn_off/chat/', TurnOffChat.as_view()),
    path('turn_on/push/', TurnOnPush.as_view()),
    path('turn_off/push/', TurnOffPush.as_view()),
]
