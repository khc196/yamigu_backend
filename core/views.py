from functools import reduce

from django.db.models import Q
from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from authorization.models import User
from datetime import datetime
from .utils.pagination import MyPaginationMixin
class MeetingTypeView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = MeetingType.objects.all()
        serializer = MeetingTypeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class PlaceTypeView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = PlaceType.objects.all()
        serializer = PlaceTypeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class PlaceView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Place.objects.all()
        serializer = PlaceSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class RatingView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Rating.objects.all()
        serializer = RatingSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

class MeetingListView(APIView):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = MeetingSerializer

    def get(self, request, *args, **kwargs):
        try:
            selected_dates = request.GET.getlist('date')
            queryset = Meeting.objects.prefetch_related('openby').prefetch_related('rating').prefetch_related('place').filter(reduce(lambda x, y: x | y, [Q(date=selected_date) for selected_date in selected_dates])).filter(~Q(openby=request.user.id)).order_by('date', 'created_at')
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404
class WaitingMeetingListView(APIView, MyPaginationMixin):
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = MeetingSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            selected_dates = request.GET.getlist('date')
            selected_types = request.GET.getlist('type')
            selected_places = request.GET.getlist('place')
            minimum_age = int(request.GET.get('minimum_age')) if request.GET.get('minimum_age') != None else 0
            maximum_age = int(request.GET.get('maximum_age')) if request.GET.get('maximum_age') != None else 11
            filtered_data = Meeting.objects.filter(reduce(lambda x, y: x | y, [Q(date=selected_date) for selected_date in selected_dates])).filter(reduce(lambda x, y: x | y, [Q(place_type=selected_place) for selected_place in selected_places])).filter(reduce(lambda x, y: x | y, [Q(meeting_type=selected_type) for selected_type in selected_types])).filter(~Q(openby=request.user.id))
            filtered_data = filtered_data.filter(Q(openby__age__gt=minimum_age+20))
            if(maximum_age < 11):
	            filtered_data = filtered_data.filter(Q(openby__age__lt=maximum_age+20))

            if(len(selected_dates) == 0):
                raise Http404
            page = self.paginate_queryset(filtered_data)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404
class WaitingMeetingListNumberView(APIView):
    serializer_class = MeetingSerializer
    def get(self, request, *args, **kwargs):
        try:
            selected_dates = request.GET.getlist('date')
            selected_types = request.GET.getlist('type')
            selected_places = request.GET.getlist('place')
            minimum_age = int(request.GET.get('minimum_age'))
            maximum_age = int(request.GET.get('maximum_age'))
            if(len(selected_dates) == 0):
                raise Http404
            filtered_data = Meeting.objects.filter(reduce(lambda x, y: x | y, [Q(date=selected_date) for selected_date in selected_dates])).filter(reduce(lambda x, y: x | y, [Q(place_type=selected_place) for selected_place in selected_places])).filter(reduce(lambda x, y: x | y, [Q(meeting_type=selected_type) for selected_type in selected_types])).filter(~Q(openby=request.user.id))
            filtered_data = filtered_data.filter(Q(openby__age__gt=minimum_age+20))
            if(maximum_age < 11):
	            filtered_data = filtered_data.filter(Q(openby__age__lt=maximum_age+20))
            count = filtered_data.count()

            return JsonResponse({
                'count' : count,
            }, json_dumps_params = {'ensure_ascii': True})
        except Meeting.DoesNotExist as e:
            raise Http404
class MyMeetingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            now=datetime.today()
            queryset = Meeting.objects.filter(openby=request.user.id).filter(Q(date__gte=now))
            serializer = MeetingSerializer(queryset, many=True)
            #print(serializer.data)
            return Response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404


class MeetingDetailView(APIView):
    serializer_class = MeetingSerializer
    def get(self, request, *args, **kwargs):
        queryset = Meeting.objects.all()
        serializer = MeetingSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class MeetingCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get_date_object(self, date_string):
        try:
            date_string = str(datetime.now().year) + " " + date_string 
            date = datetime.strptime(date_string, "%Y %m월 %d일").date()
            return date
        except:
            raise Http404
    def post(self, request, *args, **kwargs):
        data = {
                'openby': request.user.id,
                'meeting_type': request.data['meeting_type'],
                'date': self.get_date_object(request.data['date']),
                'place_type': request.data['place'],
                'appeal': request.data['appeal'],
                'place': None,
                'rating': None,
                'is_matched': False,
            }
        serializer = MeetingCreateSerializer(data=data)
        if serializer.is_valid():
            meeting = serializer.save()
            return Response(data=meeting.id, status=status.HTTP_201_CREATED)
        #print(serializer.errors)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class MeetingRequestMatchView(APIView):
    permission = [IsAuthenticated]
    def get_date_object(self, date_string):
        try:
            date_string = str(datetime.now().year) + " " + date_string 
            date = datetime.strptime(date_string, "%Y %m월 %d일").date()
            return date
        except:
            raise Http404
    def get(self, request, *args, **kwargs):
        try:
            queryset = MatchRequest.objects.filter(Q(receiver__id=request.GET.getlist('meeting_id')[0]))
            serializer = MatchRequestSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404
    def post(self, request, *args, **kwargs):
        data = {
                'openby': request.user.id,
                'meeting_type': request.data['meeting_type'],
                'date': self.get_date_object(request.data['date']),
                'place_type': request.data['place'],
                'appeal': request.data['appeal'],
                'place': None,
                'rating': None,
                'is_matched': False,
            }
        serializer = MeetingCreateSerializer(data=data)
        if serializer.is_valid():
            meeting = serializer.save()
            data2 = {
                'sender': meeting.id,
                'receiver': request.data['meeting_id'],
                'is_selected': False
                }
            serializer2 = MatchRequestSerializer(data=data2)
            if serializer2.is_valid():
                match = serializer2.save()
                # TODO: push notification to receiver
                return Response(data=match.id, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

