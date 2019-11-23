from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from django.http import Http404, JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import UserSerializer
from .models import User
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

import base64

from core.utils.file_helper import save_uploaded_file
from .tasks import async_image_upload
from requests.exceptions import HTTPError

from firebase_admin._auth_utils import UserNotFoundError
def pretty_request(request):
    headers = ''
    for header, value in request.META.items():
        if not header.startswith('HTTP'):
            continue
        header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
        headers += '{}: {}\n'.format(header, value)

    return (
        '{method} HTTP/1.1\n'
        'Content-Length: {content_length}\n'
        'Content-Type: {content_type}\n'
        '{headers}\n\n'
        '{body}'
    ).format(
        method=request.method,
        content_length=request.META['CONTENT_LENGTH'],
        content_type=request.META['CONTENT_TYPE'],
        headers=headers,
        body=request.body,
    )

def create_token_uid(uid):

    # [START create_token_uid]

    custom_token = auth.create_custom_token(uid)
    custom_token = custom_token.decode('utf-8')
    # [END create_token_uid]
    return custom_token


class UserInfoView(APIView):
    """
        유저 정보 API
        
        ---
    """
    #permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user is None:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)

        uid = user.uid
        user.firebase_token = create_token_uid(uid)
        user.save()

        try:
        	auth.update_user(
        		uid=uid,
        		display_name=user.nickname,
	        	photo_url=user.image,
     	   	)
        except ValueError:
        	auth.update_user(
     			uid=uid,
     			display_name=user.nickname
     		)
        except UserNotFoundError:
            try:
       		    auth.create_user(uid=user.uid, photo_url=user.image)
       	    except ValueError:
       		    auth.create_user(uid=user.uid)
    
        queryset = User.objects.select_related().get(id=user.id)
        serializer = UserSerializer(queryset, many=False)
        return Response(serializer.data)

class NicknameValidator(APIView):
    """
        닉네임 유효성 검사 API
        
        ---
    """
    #permission_classes = [IsAuthenticated]
    def get(self, request, nickname):
    
        try: 
            if(not nickname or User.objects.filter(nickname=nickname).exists()):
                return JsonResponse({
                    "is_available": False
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "is_available": True
                })
        except User.DoesNotExist:
            return JsonResponse({
                "is_available": False
            }, status=status.HTTP_200_OK)

class ChangeNicknameView(APIView):
    """
        닉네임 변경 API
        
        ---
        # Body Schema
            - nickname: 변경할 닉네임
        
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
    	user = User.objects.get(id=request.user.id)
    	user.nickname = request.data['nickname']
    	user.save()
    	return JsonResponse({
    		'code': 200,
    		'data': user.nickname
    	})

class SignUpView(APIView):
    """
        회원가입 API
        
        ---
        # Body Schema
            - nickname: 닉네임
            - real_name: 실명
            - gender: 성별(1: 남자, 2: 여자)
            - phone: 핸드폰 번호
            - is_student: 학생 여부
            - belong: 소속(학교 or 직장)
            - department: 부서(전공 or 팀)
            - age: 나이 
            - cert_img: 소속 인증 사진
        
    """
    def post(Self, request, *args, **kwargs):
        user = User.objects.select_related().get(id=request.user.id)
        user.nickname = request.data['nickname']
        user.real_name = request.data['real_name']
        user.gender = request.data['gender']
        user.phone = request.data['phone']
        user.is_student = True if request.data['is_student'] == 'true' else False
        user.belong = request.data['belong']
        user.department = request.data['department']
        user.age = request.data['age']
        #user.cert_image = request.data['cert_img']
        user.save()
        return Response(data=None, status=status.HTTP_200_OK)
class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter


class CertificateView(APIView):
    """
        소속 인증 API
        
        ---
        # Body Schema
            - uploaded_file: 소속 인증 사진
        
    """
    permission_classes = [IsAuthenticated]
    def post(Self, request, *args, **kwargs):
        TAG = "cert"
        file_name = save_uploaded_file(request.data['uploaded_file'], TAG)
        user = User.objects.get(id=request.user.id)
        user.cert_image = "http://106.10.39.154/9999/media/"+TAG+"/"+file_name
        user.user_certified = 1
        user.save()
        
        #async_image_upload.delay(file_path, request.user.id, 'cert')

        return Response(data=None, status=status.HTTP_200_OK)

class ChangeAvataView(APIView):
    """

        프로필 사진 변경 API
        
        ---
        # Body Schema
            - uploaded_file: 변경할 사진
        
    """
    def post(Self, request, *args, **kwargs):
        TAG="avata"
        file_name = save_uploaded_file(request.data['uploaded_file'], TAG)
        user = User.objects.get(id=request.user.id)
        user.image = "http://106.10.39.154:9999/media/" + TAG + "/" + file_name
        user.save()

        return Response(data=None, status=status.HTTP_200_OK)

