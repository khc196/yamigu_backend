from functools import reduce

from django.db.models import Q, Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
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
from fcm_django.models import FCMDevice
from core.utils import firebase_message
import json

class MeetingCreateView(APIView):
    """
        새로운 미팅 생성 API
        
        ---
        # Body Schema
            - meeting_type: 미팅 타입 (1: 2vs2, 2: 3vs3, 3: 4vs4)
            - date: 날짜(M월 d일)
            - place: 장소
            - appeal: 어필 문구
    """
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
        now=datetime.today()
        my_meetings = Meeting.objects.all().filter(openby__id=request.user.id).filter(date__gte=now)
        if my_meetings.count() == 3:
            return Response(data=None, status=status.HTTP_200_OK)
        serializer = MeetingCreateSerializer(data=data)
        if serializer.is_valid():
            meeting = serializer.save()
            return Response(data=meeting.id, status=status.HTTP_200_OK)
        print(serializer.errors)
       
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class MeetingEditView(APIView):
    """
        미팅 수정 API
        
        ---
        # Body Schema
            - meeting_id: 해당 미팅 id
            - meeting_type: 미팅 타입
            - date: 날짜
            - place_type: 장소
            - appeal: 어필 문구
        
    """
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
        #print(data)
        meeting = get_object_or_404(Meeting, id=request.data['meeting_id'])
        serializer = MeetingCreateSerializer(meeting, data=data)
        if serializer.is_valid():
            meeting = serializer.save()
            return Response(data=meeting.id, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
class MeetingDeleteView(APIView):
    """
        미팅 삭제 API
        
        ---
        # Body Schema
            - meeting_id: 해당 미팅 id
        
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        meeting = get_object_or_404(Meeting, id=request.data['meeting_id'])
        meeting.delete()
        return Response(data=meeting.id, status=status.HTTP_200_OK)

class MyMeetingListView(APIView):
    """
        마이 미팅 리스트 (미진행) API 
        
        ---
        # 아직 진행되지 않은 마이 미팅 리스트
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            now=datetime.today()
            queryset = Meeting.objects.select_related('openby').filter(openby=request.user.id, date__gte=now).order_by('date').prefetch_related(
                Prefetch(
                    'match_receiver',
                    queryset=MatchRequest.objects.all()
                )
                )
  
            serializer = MeetingSerializer(queryset, many=True)
            #print(serializer.data)
            return Response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404
class MyPastMeetingListView(APIView):
    """
        마이 미팅 리스트 (후기 작성 필요) API 

        ---
        # 진행된 과거의 마이 미팅 리스트 중 후기 작성이 안된 리스트
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            now=datetime.today()
            queryset = Meeting.objects.filter(is_matched=True, openby=request.user.id, date__lt=now, rating=None).order_by('date')
            serializer = MeetingSerializer(queryset, many=True)
           # print(serializer.data)
            return Response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404
class TodayMeetingListView(APIView):
	permission_classes = [IsAuthenticated]
	def get(self, request, *args, **kwargs):
		try:
			now=datetime.today()
			queryset = Meeting.objects.filter(is_matched=True, date=now).filter(~Q(openby=request.user.id))
			serializer = MeetingSerializer(queryset, many=True)
			return Response(serializer.data)
		except Meeting.DoesNotExist as e:
			raise Http404
			
class WaitingMeetingListView(APIView, MyPaginationMixin):
    """
        대기 리스트 API
        
        ---
        # Get Parameters
            - date: 날짜 (yyyy-mm-dd format)
            - type: 미팅 타입 (1=2:2, 2=3:3, 3=4:4)
            - place: 장소(1=신촌/홍대, 2=건대/왕십리, 3=강남)
            - minimum_age: 최소 나이(0~11, 0부터 20살, 11은 31세 이상)
            - maximum_age: 최대 나이(0~11)
        # Example
            - https://106.10.39.154:9999/api/meetings/waiting/?date=2019-10-11&date=2019-10-12&type=1&place=1&place=2&place=3
        
    """
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    serializer_class = MeetingSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            selected_dates = request.GET.getlist('date')
            selected_types = request.GET.getlist('type')
            selected_places = request.GET.getlist('place')
            minimum_age = int(request.GET.get('minimum_age')) if request.GET.get('minimum_age') != None else 0
            maximum_age = int(request.GET.get('maximum_age')) if request.GET.get('maximum_age') != None else 11
            #print(request.user.id)

            filtered_data = Meeting.objects.filter(reduce(lambda x, y: x | y, [Q(date=selected_date) for selected_date in selected_dates])).filter(reduce(lambda x, y: x | y, [Q(place_type=selected_place) for selected_place in selected_places])).filter(reduce(lambda x, y: x | y, [Q(meeting_type=selected_type) for selected_type in selected_types])).filter(~Q(openby=request.user.id))
            
            filtered_data = filtered_data.filter(Q(openby__age__gte=minimum_age+20))
            if(maximum_age < 11):
                filtered_data = filtered_data.filter(Q(openby__age__lte=maximum_age+20))
            my_meetings = Meeting.objects.filter(openby__id=request.user.id)
            if(my_meetings.count() > 0):
                for data in filtered_data:
                    if not data.is_matched:
                        for match in data.match_receiver.all():
                            if match.sender in my_meetings or match.receiver in my_meetings:
                                filtered_data = filtered_data.exclude(id=data.id)
                        for match in data.match_sender.all():
                            if match.sender in my_meetings or match.receiver in my_meetings:
                                filtered_data = filtered_data.exclude(id=data.id)
                        for mine in my_meetings:
                            if data.date == mine.date and data.meeting_type != mine.meeting_type:
                                filtered_data = filtered_data.exclude(id=data.id)
            #filtered_data = filtered_data.exclude(
            #    match_receiver__receiver__id__in=my_meetings
            #)
            #filtered_data = filtered_data.exclude(
            #    match_sender__sender__id__in=my_meetings
            #)
            #print(filtered_data.all())
            if(len(selected_dates) == 0):
                raise Http404
            page = self.paginate_queryset(filtered_data.order_by("is_matched", "date"))
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                #print(serializer.data)
                return self.get_paginated_response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404

class WaitingMeetingListNumberView(APIView):
    """
        대기 리스트 Count API
        
        ---
        # Get Parameters
            - date: 날짜 (yyyy-mm-dd format)
            - type: 미팅 타입 (1=2:2, 2=3:3, 3=4:4)
            - place: 장소(1=신촌/홍대, 2=건대/왕십리, 3=강남)
            - minimum_age: 최소 나이(0~11, 0부터 20살, 11은 31세 이상)
            - maximum_age: 최대 나이(0~11)
        # Example
            - https://106.10.39.154:9999/api/meetings/count/?date=2019-10-11&date=2019-10-12&type=1&place=1&place=2&place=3
        
    """
    serializer_class = MeetingSerializer
    def get(self, request, *args, **kwargs):
        try:
            selected_dates = request.GET.getlist('date')
            selected_types = request.GET.getlist('type')
            selected_places = request.GET.getlist('place')
            minimum_age = int(request.GET.get('minimum_age')) if request.GET.get('minimum_age') != None else 0
            maximum_age = int(request.GET.get('maximum_age')) if request.GET.get('maximum_age') != None else 11
            if(len(selected_dates) == 0):
                raise Http404
            filtered_data = Meeting.objects.filter(reduce(lambda x, y: x | y, [Q(date=selected_date) for selected_date in selected_dates])).filter(reduce(lambda x, y: x | y, [Q(place_type=selected_place) for selected_place in selected_places])).filter(reduce(lambda x, y: x | y, [Q(meeting_type=selected_type) for selected_type in selected_types])).filter(~Q(openby=request.user.id))
            filtered_data = filtered_data.exclude(is_matched=True)
            filtered_data = filtered_data.filter(Q(openby__age__gte=minimum_age+20))
            if(maximum_age < 11):
	            filtered_data = filtered_data.filter(Q(openby__age__lte=maximum_age+20))
            my_meetings = Meeting.objects.filter(openby__id=request.user.id)
            for data in filtered_data:
                for match in data.match_receiver.all():
                    if match.sender in my_meetings or match.receiver in my_meetings:
                        filtered_data = filtered_data.exclude(id=data.id)
                for match in data.match_sender.all():
                    if match.sender in my_meetings or match.receiver in my_meetings:
                        filtered_data = filtered_data.exclude(id=data.id)
                for mine in my_meetings:
                    if data.date == mine.date and data.meeting_type == mine.meeting_type:
                        filtered_data = filtered_data.exclude(id=data.id)
            filtered_data = filtered_data.exclude(is_matched=True)
            count = filtered_data.count()

            return JsonResponse(data={
                'count' : count,
            }, json_dumps_params = {'ensure_ascii': True}, status=status.HTTP_200_OK)
        except Meeting.DoesNotExist as e:
            raise Http404
class MeetingSendRequestMatchView(APIView):
    """
        매칭 신청 API
        
        ---
        # Body Schema
            - meeting_type: 미팅 타입
            - date: 날짜(%m월 %d일)
            - place: 장소
            - meeting_id: 신청 대상 미팅
        
    """
    permission = [IsAuthenticated]
    def get_date_object(self, date_string):
        try:
            date_string = str(datetime.now().year) + date_string.strip()
            date_string = date_string.replace(" ", "")
            date = datetime.strptime(date_string, "%Y%m월%d일").date()
            return date
        except:
            raise JsonResponse(data={
            'message': 'Invalid date format', 
        }, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, *args, **kwargs):
        target_meeting = Meeting.objects.get(pk=request.data['meeting_id'])
        if(target_meeting.is_matched):
        	return JsonResponse(data={
        		'message': 'target already matched',
			},status=status.HTTP_200_OK)
        if(int(request.data['meeting_type']) != target_meeting.meeting_type.id):
            print("different type")
            return JsonResponse(data={
                'message': 'different type', 
        }, status=status.HTTP_200_OK)
        now=datetime.today()
        my_meetings = Meeting.objects.filter(openby__id=request.user.id).filter(date__gte=now)
        prev_meeting = Meeting.objects.filter(openby__id=request.user.id, date=self.get_date_object(request.data['date']))
        if(prev_meeting.count() == 0) :
            if(my_meetings.count() == 3):
                return JsonResponse(data={
                    'message': 'full card', 
                    }, status=status.HTTP_200_OK)
            return JsonResponse(data={
                'message': 'You should create new meeting for matching', 
                }, status=status.HTTP_200_OK)
        if(prev_meeting[0].is_matched):
        	return JsonResponse(data={
        		'message': 'my card already matched',
			},status=status.HTTP_200_OK)
        data = {
            'sender': prev_meeting[0].id,
            'receiver': request.data['meeting_id'],
            'manager': settings.MANAGER_ID,
            'is_selected': False
            }
        matches = MatchRequest.objects.all().filter(sender=data['sender'], receiver=data['receiver'])
        
        if(matches.count() > 0):
        	return JsonResponse(data={
        		'message': 'already exists',
			},status=status.HTTP_200_OK)
         
        serializer = MatchRequestSerializer(data=data)
        if serializer.is_valid():
            match = serializer.save()
            #TODO: Push notification & Firebase DB notification (to Receiver)
            receiver = Meeting.objects.get(pk=data['receiver'])
            receiver_user_id = receiver.openby.id
            receiver_user_uid = receiver.openby.uid
            month = prev_meeting[0].date.month
            day = prev_meeting[0].date.day
            notification_content = "{}/{} 미팅 신청이 들어왔어요!".format(month, day)
            print(notification_content)
            notification_data = ""
            push_data = {
                'title': "야미구",
                'content': notification_content,
                'clickAction': ".NotificationActivity",
                'intentArgs': ""
            }
            firebase_message.send_push(receiver_user_id, push_data)
            firebase_message.send_notification(receiver_user_uid, 1, notification_content, notification_data)
            return Response(status=status.HTTP_200_OK, data={
                "message": "created"
            })
        print(serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class MeetingSendRequestMatchNewView(APIView):
    """
        매칭 신청(새로운 카드 생성) API
        
        ---
        # Body Schema
            - meeting_type: 미팅 타입
            - date: 날짜(%m월 %d일)
            - place: 장소
            - appeal: 어필 문구
            - receiver: 신청 대상 미팅
        
    """
    permission = [IsAuthenticated]
    def get_date_object(self, date_string):
        try:
            date_string = str(datetime.now().year) + " " + date_string 
            date_string = date_string.replace(" ", "")
            date = datetime.strptime(date_string, "%Y%m월%d일").date()
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
        receiver = Meeting.objects.get(pk=request.data['meeting_id'])
        if(receiver.is_matched):
        	return JsonResponse(data={
        		'message': 'target already matched',
			},status=status.HTTP_200_OK)
        serializer = MeetingCreateSerializer(data=data)
        if serializer.is_valid():
            meeting = serializer.save()
            data2 = {
    			'sender': meeting.id,
    			'receiver': request.data['meeting_id'],
    			'manager': settings.MANAGER_ID,
    			'is_selected': False
    		}
            serializer2 = MatchRequestSerializer(data=data2)
            if serializer2.is_valid():
                match = serializer2.save()
                #TODO: Push notification & Firebase DB notification (to Receiver)
                receiver_user_id = receiver.openby.id
                receiver_user_uid = receiver.openby.uid
                month = meeting.date.month
                day = meeting.date.day
                notification_content = "{}/{} 미팅 신청이 들어왔어요!".format(month, day)
                print(notification_content)
                notification_data = ""
                push_data = {
                    'title': "야미구",
                    'content': notification_content,
                    'clickAction': ".NotificationActivity",
                    'intentArgs': ""
                    }
                firebase_message.send_push(receiver_user_id, push_data)
                firebase_message.send_notification(receiver_user_uid, 1, notification_content, notification_data)
                return Response(data=match.id, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeetingReceivedRequestMatchView(APIView):
    """
        받은 매칭 신청 리스트 API
        
        ---
        # Body Schema
            - meeting_id: 해당 미팅 id
        
    """
    permission = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            queryset = MatchRequest.objects.filter(receiver__id=request.GET.getlist('meeting_id')[0], is_declined=False)
            serializer = MatchRequestSenderSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404

class MeetingSentRequestMatchView(APIView):
    """
        보낸 매칭 신청 리스트 API
        
        ---
        # Body Schema
            - meeting_id: 해당 미팅 id
        
    """
    permission = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            queryset = MatchRequest.objects.filter(sender__id=request.GET.getlist('meeting_id')[0])
            serializer = MatchRequestReceiverSerializer(queryset, many=True, context={'request': request})
           # print(serializer.data)
            return Response(serializer.data)
        except Meeting.DoesNotExist as e:
            raise Http404

class MeetingAcceptRequestMatchView(APIView):
    """
        매칭 신청 수락 API
        
        ---
        # Body Schema
            - request_id: 매칭 신청 id
        
    """
    permission = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        match_request = get_object_or_404(MatchRequest, id=request.data['request_id'])
        receiver_user_id = match_request.receiver.openby.id
        if match_request.sender.is_matched or match_request.receiver.is_matched:
            match_id = match_request.id
            match_request.delete()
            return JsonResponse(data={
                    'match_id': match_id,
                    'message': "Duplicated"
            }, status=status.HTTP_200_OK)
        if request.user.id == receiver_user_id:
            match_request.is_selected = True
            match_request.accepted_at = datetime.now()
            sender = Meeting.objects.get(pk=match_request.sender.id)
            receiver = Meeting.objects.get(pk=match_request.receiver.id)
            sender.is_matched = True
            receiver.is_matched = True
            sender.matched_meeting = receiver
            receiver.matched_meeting = sender
            sender.save()
            receiver.save()
            match_request.save()
            count_meeting = Meeting.objects.all().filter(openby=request.user.id).filter(is_matched=True).count()
            #TODO: Push notification & Firebase DB notification
            month = receiver.date.month
            day = receiver.date.day
            notification_content = "{}/{} 미팅 매칭이 완료되었어요!".format(month, day)
            notification_data = ""
            push_data = {
                'title': "야미구",
                'content': notification_content,
                'clickAction': ".NotificationActivity",
                'intentArgs': ""
            }
            sender_user_id = sender.openby.id
            sender_user_uid = sender.openby.uid
            firebase_message.send_push(sender_user_id, push_data)
            firebase_message.send_notification(sender_user_uid, 2, notification_content, notification_data)
            return JsonResponse(data={
                    'match_id': match_request.id,
                    'count_meeting': count_meeting,
                    'message': "Accepted"
            }, status=status.HTTP_200_OK)
            
        return Response(data=match_request.id, status=status.HTTP_400_BAD_REQUEST)

class MeetingCancelRequestMatchView(APIView):
    """
        매칭 신청 취소 API
        
        ---
        # Body Schema
            - meeting_type: 미팅 타입
            - request_id: 매칭 신청 id
        
    """
    permission = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        match_request = get_object_or_404(MatchRequest, id=request.data['request_id'])
        sender_user_id = match_request.sender.openby.id
        if request.user.id == sender_user_id:
            match_request.delete()
            return Response(data=match_request.id, status=status.HTTP_200_OK)
        return Response(data=match_request.id, status=status.HTTP_400_BAD_REQUEST)

class MeetingDeclineRequestMatchView(APIView):
    """
        매칭 신청 거절 API
        
        ---
        # Body Schema
            - request_id: 매칭 신청 id
        
    """
    permission = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        match_request = get_object_or_404(MatchRequest, id=request.data['request_id'])
        receiver_user_id = match_request.receiver.openby.id
        sender_user_id = match_request.sender.openby.id
        sender_user_uid = match_request.sender.openby.uid
        if request.user.id == receiver_user_id:
            #match_request.is_declined = True
            #match_request.save()
            

            #TODO: Push notification & Firebase DB notification (to Sender)
            month = match_request.receiver.date.month
            day = match_request.receiver.date.day
            match_request.delete()
            notification_content = "{}/{} 미팅 신청이 거절되었어요!".format(month, day)
            notification_data = ""
            push_data = {
                'title': "야미구",
                'content': notification_content,
                'clickAction': ".NotificationActivity",
                'intentArgs': ""
            }
            firebase_message.send_push(sender_user_id, push_data)
            firebase_message.send_notification(sender_user_uid, 3, notification_content, notification_data)
            return Response(data=match_request.id, status=status.HTTP_200_OK)
        return Response(data=match_request.id, status=status.HTTP_400_BAD_REQUEST)

class MeetingCancelMatchView(APIView):
    """
        매칭 취소 API
        
        ---
        # Body Schema
            - match_id: 매칭 신청 id
        
    """
    permission = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        match_request = get_object_or_404(MatchRequest, id=request.data['match_id'])
        match_id = match_request.id
        partner = match_request.receiver.openby if match_request.sender.openby.id == request.user.id else match_request.sender.openby
        try:
            match_request.sender.delete()
            match_request.receiver.delete()
            match_request.delete()
            #TODO: Push notification & Firebase DB notification 
            notification_content = "매칭 취소로 인해 티켓이 반환되었어요."
            notification_data = ""
            push_data = {
                'title': "야미구",
                'content': notification_content,
                'clickAction': ".NotificationActivity",
                'intentArgs': ""
            }
        
            firebase_message.send_push(partner.id, push_data)
            firebase_message.send_notification(partner.uid, 6, notification_content, notification_data)
            return Response(data=match_id, status=status.HTTP_200_OK)
        except:
            return Response(data=match_id, status=status.HTTP_400_BAD_REQUEST)

# class RatingView(APIView):
#     """
#         별점 평가 API

#         ---
#         # Request Body Schema
#             - meeting_id: 해당 미팅 id
#             - visual: visual 점수
#             - fun: fun 점수
#             - manner: manner 점수
#     """
#     permission_classes = [IsAuthenticated]
#     def post(self, request, *args, **kwargs):
#         data = {
#             'visual': request.data['visual'],
#             'fun': request.data['fun'],
#             'manner': request.data['manner']
#         }
#         meeting = Meeting.objects.filter(id=request.data['meeting_id']) 
#         rating = meeting.values("rating")[0]['rating']
#         serializer = RatingSerializer(data=data)
#         if serializer.is_valid():
#             rating = serializer.save()
#             meeting.update(rating=rating)
#             return Response(status=status.HTTP_200_OK)
#         #print(serializer.errors)
#         return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FeedbackView(APIView):
    """
        후기 API
        
        ---
        # Request Body Schema
            - meeting_id: 해당 미팅 id
            - feedback: 후기 내용
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        
        meeting = Meeting.objects.filter(id=request.data['meeting_id']).prefetch_related('rating')
        data = {
            'description': request.data['feedback'],
        }
        serializer = RatingSerializer(data=data)
        if serializer.is_valid():
            rating = serializer.save()
            meeting.update(rating=rating)
            return Response(status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PushNotificationView(APIView):
    """
    Push Notification API
        
        ---
        # Request Body Schema
        	- receiverId: push notification 받을 대상 유저의 uid
        	- data: 
        		title: notification 제목
        		content: notification 내용
        		clickAction: click 시 열릴 activity의 이름(이름 앞에 .을 붙여야함)
        		intentArgs:  각 Activity를 열기 전에 처리해줘야 할 데이터 목록
        			ex) ChattingActivity의 경우 
        			partner_age: push를 보내는 유저의 나이(integer)
        			partner_belong: push를 보내는 유저의 소속(string)
        			partner_department: push를 보내는 유저의 학과/부서(string)
        			partner_nickname: push를 보내는 유저의 닉네임(string)
        			partner_uid: push를 보내는 유저의 uid(string)
        			date: 미팅 날짜(%m월 %d일, string)
        			place: 미팅 장소(string)
        			type: 미팅 타입(string)
        			meeting_id: 미팅 id(string)
        			matching_id: 매칭 id(string)
        			manager_name: 매니저 이름(string)
        			manager_uid: 매니저 uid(string)
        			accepted_at: 매칭 성사 시간(string)
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(uid=request.data['receiverId']).values("id")[0]["id"]
            devices = FCMDevice.objects.filter(user=user)
            try:
                data=json.loads(request.data['data'])
            except TypeError:
                data=request.data['data']
            
            firebase_message.send_push(user, data)
            return Response(status=status.HTTP_200_OK)
        except MultiValueDictKeyError: 
            error_msg = json.dumps({
                'message': 'Bad Request',
                'required_values': 'receiverId(FCM Token), data(title, content, clickAction(activity name), intentArgs)' 
            })
            return Response(data=error_msg, status=status.HTTP_400_BAD_REQUEST) 
class RecommendationMeetingListView(APIView):
    """
        추천 미팅 리스트 API
        
        ---
        
    """
    permission_class = [IsAuthenticated]
    def get(Self, request, *args, **kwargs):
        now=datetime.today()
        meetings = Meeting.objects.all().filter(~Q(openby=request.user.id)).filter(is_matched=False).filter(date__gte=now).order_by('date')
        my_meetings = Meeting.objects.filter(openby__id=request.user.id)
        if(my_meetings.count() > 0):
            for data in meetings:
                for match in data.match_receiver.all():
                    if match.sender in my_meetings or match.receiver in my_meetings:
                        meetings = meetings.exclude(id=data.id)
                for match in data.match_sender.all():
                    if match.sender in my_meetings or match.receiver in my_meetings:
                        meetings = meetings.exclude(id=data.id)
                for mine in my_meetings:
                    if data.date == mine.date and (data.meeting_type != mine.meeting_type or mine.is_matched):
                        meetings = meetings.exclude(id=data.id)
        meetings = meetings[:5] 
        serializer = MeetingSerializer(meetings, many=True, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class CallManagerView(APIView):
    permission_class = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
# class MeetingTypeView(APIView):
#     def get(self, request, *args, **kwargs):
#         queryset = MeetingType.objects.all()
#         serializer = MeetingTypeSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)


# class PlaceTypeView(APIView):
#     def get(self, request, *args, **kwargs):
#         queryset = PlaceType.objects.all()
#         serializer = PlaceTypeSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)


# class PlaceView(APIView):
#     def get(self, request, *args, **kwargs):
#         queryset = Place.objects.all()
#         serializer = PlaceSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)


# class MeetingListView(APIView): 
#     pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
#     serializer_class = MeetingSerializer

#     def get(self, request, *args, **kwargs):
#         try:
#             selected_dates = request.GET.getlist('date')
#             queryset = Meeting.objects.select_related('openby').prefetch_related('rating').prefetch_related('place').filter(reduce(lambda x, y: x | y, [Q(date=selected_date) for selected_date in selected_dates])).filter(~Q(openby=request.user.id)).order_by('date', 'created_at')
#             page = self.paginate_queryset(queryset)

#             if page is not None:
#                 serializer = self.serializer_class(page, many=True)
#                 return self.get_paginated_response(serializer.data)
#         except Meeting.DoesNotExist as e:
#             raise Http404






# class MeetingDetailView(APIView):
    
#     serializer_class = MeetingSerializer
#     def get(self, request, *args, **kwargs):
#         queryset = Meeting.objects.all()
#         serializer = MeetingSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)



      





