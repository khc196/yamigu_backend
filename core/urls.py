from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

api_urlpattern = [
    path('meetings/', MeetingListView.as_view()),
    path('meetings/<int:id>/', MeetingDetailView.as_view()),
]