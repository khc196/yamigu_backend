# authorization/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserInfoView, KakaoLoginView

api_urlpattern = [
    path('auth/', include('rest_auth.urls')),
    path('user/info/', UserInfoView.as_view()),
    path('oauth/kakao/', KakaoLoginView.as_view(), name='socialaccount_signin'),
]