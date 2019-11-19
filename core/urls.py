from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
api_urlpattern = [
    path('meetings/create/', MeetingCreateView.as_view()),
    path('meetings/edit/', MeetingEditView.as_view()),
    path('meetings/delete/', MeetingDeleteView.as_view()),
    path('meetings/my/', MyMeetingListView.as_view()),
    path('meetings/my_past/', MyPastMeetingListView.as_view()),
    path('meetings/waiting/', WaitingMeetingListView.as_view()),
    path('meetings/waiting/count/', WaitingMeetingListNumberView.as_view()),
    path('meetings/today/', TodayMeetingListView.as_view()),
    path('meetings/recommendation/', RecommendationMeetingListView.as_view()),
    path('matching/received_request/', MeetingReceivedRequestMatchView.as_view()),
    path('matching/sent_request/', MeetingSentRequestMatchView.as_view()),
    path('matching/send_request/', MeetingSendRequestMatchView.as_view()),
    path('matching/send_request_new/', MeetingSendRequestMatchNewView.as_view()),
	path('matching/cancel_request/', MeetingCancelRequestMatchView.as_view()),
	path('matching/accept_request/', MeetingAcceptRequestMatchView.as_view()),
	path('matching/decline_request/', MeetingDeclineRequestMatchView.as_view()),
    path('matching/cancel_matching/', MeetingCancelMatchView.as_view()),
    path('meetings/rate/', RatingView.as_view()),
    path('meetings/feedback/', FeedbackView.as_view()),
    path('fcm/register_device/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('fcm/send_push/', PushNotificationView.as_view()),
]
