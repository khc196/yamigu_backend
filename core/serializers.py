from rest_framework.serializers import ModelSerializer, SerializerMethodField, CurrentUserDefault, CharField, IntegerField
from rest_framework.validators import UniqueTogetherValidator
from django.db.models import Q, Count
from .models import *
import time 
from datetime import datetime
class MeetingTypeSerializer(ModelSerializer):
    class Meta:
        model = MeetingType
        fields = ("id", "name", "created_at")
class PlaceTypeSerializer(ModelSerializer):
    class Meta:
        model = PlaceType
        fields = ("id", "name", "created_at")
class PlaceSerializer(ModelSerializer):
    class Meta:
        model = Place
        fields = ("id", "name", "place_type", "is_premium", "description", "link", "created_at")
class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = ("id", "description", "created_at")
class MatchedMeetingSerializer(ModelSerializer):
    openby_nickname = CharField(source='openby.nickname', read_only=True)
    openby_uid = CharField(source='openby.uid', read_only=True)
    openby_age = CharField(source='openby.age', read_only=True)
    openby_belong = CharField(source='openby.belong', read_only=True)
    openby_department = CharField(source='openby.department', read_only=True)
    class Meta:
        model = Meeting
        fields= ("id", "openby_uid",  "openby_nickname", "openby_age", "openby_belong", "openby_department", "rating")
class MeetingSerializer(ModelSerializer):
    place_type_name = CharField(source='place_type.name', read_only=True)
    openby_nickname = CharField(source='openby.nickname', read_only=True)
    openby_age = CharField(source='openby.age', read_only=True)
    openby_belong = CharField(source='openby.belong', read_only=True)
    openby_department = CharField(source='openby.department', read_only=True)
    openby_profile = CharField(source='openby.image', read_only=True)
    received_request = SerializerMethodField('get_received_request_prefetch_related')
    sent_request = SerializerMethodField('get_sent_request_prefetch_related')
    matched_meeting = MatchedMeetingSerializer()
    def get_received_request_prefetch_related(self, meeting):
        match_request_queryset = meeting.match_receiver.all().order_by('created_at').filter(Q(is_declined=False))
        
        data = [{'id': match_request.id,'is_selected': match_request.is_selected, 'sender': match_request.sender.id, 'receiver': match_request.receiver.id, 'manager_uid': match_request.manager.uid, 'manager_name': match_request.manager.nickname, 'manager_profile': match_request.manager.image, 'accepted_at': int(((match_request.accepted_at - datetime(1970, 1, 1)).total_seconds() - 3600 * 9)* 1000) if match_request.accepted_at != None else None
} for match_request in match_request_queryset]
       	return_data = { 'count': match_request_queryset.count(), 'data': data}
       	return return_data
    def get_sent_request_prefetch_related(self, meeting):
        match_request_queryset = meeting.match_sender.all().order_by('created_at').filter(Q(is_declined=False))
        data = [{'id': match_request.id,'is_selected': match_request.is_selected,  'sender': match_request.sender.id, 'receiver': match_request.receiver.id, 'manager_uid': match_request.manager.uid, 'manager_name': match_request.manager.nickname, 'manager_profile': match_request.manager.image, 'accepted_at': int(((match_request.accepted_at - datetime(1970, 1, 1)).total_seconds() - 3600 * 9)* 1000) if match_request.accepted_at != None else None} for match_request in match_request_queryset]
       	return_data = { 'count': match_request_queryset.count(), 'data': data}
       	return return_data     
    class Meta:
        model = Meeting
        fields = ("id", "meeting_type", "openby", "openby_nickname", "openby_age", "openby_belong", "openby_department", "openby_profile", "date", "place_type", "place_type_name", "place", "appeal", "rating", "is_matched", "created_at", "received_request", "sent_request", "matched_meeting")

class MeetingCreateSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = ("id", "meeting_type", "openby", "date", "place_type", "appeal", "rating", "is_matched", "created_at")
        validators = [
            UniqueTogetherValidator(
                queryset=Meeting.objects.all(), 
                fields=['openby', 'date']
            )
        ]
class MatchRequestSerializer(ModelSerializer):
	manager_uid = IntegerField(source='manager.uid', read_only=True)
	class Meta:
		model = MatchRequest
		fields = ("id", "sender", "receiver", "manager", "manager_uid", "accepted_at", "created_at")
class MatchRequestSenderSerializer(ModelSerializer):
    sender = MeetingSerializer()
    #receiver = MeetingSerializer()
    class Meta:
        model = MatchRequest
        fields = ("id", "sender", "created_at")

class MatchRequestReceiverSerializer(ModelSerializer):
    #sender = MeetingSerializer()
    receiver = MeetingSerializer()
    class Meta:
        model = MatchRequest
        fields = ("id", "receiver", "created_at")

class ChattingRoomListSerializer(ModelSerializer):
    manager_info = SerializerMethodField('get_manager_info')
    meeting_info = SerializerMethodField('get_meeting_info')
    receiver_info = SerializerMethodField('get_receiver_info')
    sender_info = SerializerMethodField('get_sender_info')
    def get_manager_info(self, match):
        return {'id': match.manager.id, 'uid': match.manager.uid, 'nickname': match.manager.nickname}
    def get_meeting_info(self, match):
        return {'type': match.sender.meeting_type.name, 'date': match.sender.date, 'accepted_at': match.accepted_at}
    def get_receiver_info(self, match):
        return {'meeting_id': match.receiver.id, 'id': match.receiver.openby.id, 'uid': match.receiver.openby.uid, 'nickname': match.receiver.openby.nickname, 'age': match.receiver.openby.age, 'gender': '남' if match.receiver.openby.gender == 1 else '여', 'belong': match.receiver.openby.belong, 'department':  match.receiver.openby.department }
    def get_sender_info(self, match):
        return {'meeting_id': match.sender.id, 'id': match.sender.openby.id, 'uid': match.sender.openby.uid, 'nickname': match.sender.openby.nickname, 'age': match.sender.openby.age, 'gender': '남' if match.sender.openby.gender == 1 else '여', 'belong': match.sender.openby.belong, 'department':  match.sender.openby.department}
    class Meta:
        model = MatchRequest
        fields = ("id", "manager_call", "manager_info", "meeting_info", "receiver_info", "sender_info")
