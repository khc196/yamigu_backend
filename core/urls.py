from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

api_urlpattern = [
    path('meetings/', MeetingListView.as_view()),
    path('meetings/<int:id>/', MeetingDetailView.as_view()),
    path('meetings/create/', MeetingCreateView.as_view()),
    path('meetings/my/', MyMeetingListView.as_view()),
    path('meetings/waiting/', WaitingMeetingListView.as_view()),
    path('meetings/waiting/count/', WaitingMeetingListNumberView.as_view()),
    path('meetings/request_match/', MeetingRequestMatchView.as_view()),
]
