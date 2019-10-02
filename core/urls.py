from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

api_urlpattern = [
    path('meetings/', MeetingListView.as_view()),
    path('meetings/<int:id>/', MeetingDetailView.as_view()),
    path('meetings/create/', MeetingCreateView.as_view()),
    path('meetings/edit/', MeetingEditView.as_view()),
    path('meetings/delete/', MeetingDeleteView.as_view()),
    path('meetings/my/', MyMeetingListView.as_view()),
    path('meetings/my_past/', MyPastMeetingListView.as_view()),
    path('meetings/waiting/', WaitingMeetingListView.as_view()),
    path('meetings/waiting/count/', WaitingMeetingListNumberView.as_view()),
    path('meetings/received_request/', MeetingReceivedRequestMatchView.as_view()),
    path('meetings/sent_request/', MeetingSentRequestMatchView.as_view()),
    path('meetings/send_request/', MeetingSendRequestMatchView.as_view()),
    path('meetings/send_request_new/', MeetingSendRequestMatchNewView.as_view()),
	path('meetings/cancel_request/', MeetingCancelRequestMatchView.as_view()),
	path('meetings/accept_request/', MeetingAcceptRequestMatchView.as_view()),
	path('meetings/decline_request/', MeetingDeclineRequestMatchView.as_view()),
    path('meetings/rate/', RatingView.as_view()),
    path('meetings/feedback/', FeedbackView.as_view()),
]
