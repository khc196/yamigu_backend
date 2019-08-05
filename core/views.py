from functools import reduce

from django.db.models import Q
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import *
from authorization.models import User
import datetime

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


class MeetingDetailView(APIView):
    serializer_class = MeetingSerializer
    def get(self, request, *args, **kwargs):
        queryset = Meeting.objects.all()
        serializer = MeetingSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class MeetingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_meetingtype_object(self, id):
        try:
            return MeetingType.objects.get(id=id)
        except:
            raise Http404
    def post(self, request, *args, **kwargs):
        type_id = kwargs['category']
        mettingtype = self.get_meetingtype_object(type_id)
        data = {
                'meeting_type': mettingtype.id,
                'openby': request.user.id,
                'date': request.data['date'],
                'place': request.data['place'],
                'appeal': request.data['appeal'],
            }
        if(request.user.gender == 0):
            data['man'] = request.user.id
        elif(request.user.gender == 1):
            data['woman'] = request.user.id

        serializer = MeetingSerializer(data=data)

        if serializer.valid():
            meeting = serializer.save()
            return Response(data=meeting.id, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)