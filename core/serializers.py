from rest_framework.serializers import ModelSerializer, SerializerMethodField, CurrentUserDefault, CharField
from rest_framework.validators import UniqueTogetherValidator
from django.db.models import Q
from .models import *

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
        fields = ("id", "visual", "fun", "manner", "description", "created_at")
class MatchedMeetingSerializer(ModelSerializer):
    openby_nickname = CharField(source='openby.nickname', read_only=True)
    openby_age = CharField(source='openby.age', read_only=True)
    openby_belong = CharField(source='openby.belong', read_only=True)
    openby_department = CharField(source='openby.department', read_only=True)
    class Meta:
        model = Meeting
        fields = ("id", "openby_nickname", "openby_age", "openby_belong", "openby_department", "rating")
class MeetingSerializer(ModelSerializer):
    place_type_name = CharField(source='place_type.name', read_only=True)
    openby_nickname = CharField(source='openby.nickname', read_only=True)
    openby_age = CharField(source='openby.age', read_only=True)
    openby_belong = CharField(source='openby.belong', read_only=True)
    openby_department = CharField(source='openby.department', read_only=True)
    openby_profile = CharField(source='openby.image', read_only=True)
    received_request = SerializerMethodField('get_match_request_prefetch_related')
    matched_meeting = MatchedMeetingSerializer()
    def get_match_request_prefetch_related(self, meeting):
        match_request_queryset = meeting.match_receiver.all().order_by('created_at').filter(Q(is_declined=False))
        return match_request_queryset.count()
    class Meta:
        model = Meeting
        fields = ("id", "meeting_type", "openby", "openby_nickname", "openby_age", "openby_belong", "openby_department", "openby_profile", "date", "place_type", "place_type_name", "place", "appeal", "rating", "is_matched", "created_at", "received_request", "matched_meeting")

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
    class Meta:
        model = MatchRequest
        fields = ("id", "sender", "receiver", "created_at")
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



