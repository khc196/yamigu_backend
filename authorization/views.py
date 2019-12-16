from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from django.http import Http404, JsonResponse
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import UserSerializer
from .models import User, generateInviteCode
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from rest_framework.authtoken.models import Token
import base64

from core.utils.file_helper import save_uploaded_file, rotate_image, get_file_path
from .tasks import async_image_upload
from requests.exceptions import HTTPError

from firebase_admin._auth_utils import UserNotFoundError
from django.contrib.auth.models import AbstractBaseUser

from core.utils import firebase_message

#from oauth2client.service_account import ServiceAccountCredentials

#scopes = ['https://www.googleapis.com/auth/androidpublisher']
#credentials = ServiceAccountCredentials.from_json_keyfile_name('api-7596831323571844011-92784-c86e59b033df.json', scopes)

#from httplib2 import Http

#http_auth = credentials.authorize(Http())
#from googleapiclient.discovery import build

#androidpublisher = build('androidpublisher', 'v2', http=http_auth)



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
class VerifyView(APIView):
    """
        회원 여부 판단 API
        
        ---
        # Body Schema
            - phone: 핸드폰 번호
    """
    def post(self, request, *args, **kwargs):
        try:
            user = User.objects.get(phone=request.data['phone'])
            token = Token.objects.get(user=user)
            return JsonResponse(data={"key":str(token)}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return JsonResponse(data={"key":None}, status=status.HTTP_200_OK)
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
            - friend_code: 친구 코드 (선택 사항)
        
    """
    def post(self, request, *args, **kwargs):
        user = User.objects.select_related().get(id=request.user.id)
        user.nickname = request.data['nickname']
        user.real_name = request.data['real_name']
        user.gender = request.data['gender']
        user.phone = request.data['phone']
        user.is_student = True if request.data['is_student'] == 'true' else False
        user.belong = request.data['belong']
        user.department = request.data['department']
        user.age = request.data['age']
        invite_code = generateInviteCode()
        while(True):
            try: 
                if(User.objects.filter(invite_code=invite_code).exists()):
                    invite_code = generateInviteCode()
                else:
                    break
            except User.DoesNotExist:
                break
        user.invite_code = invite_code
        user.save()
        
        friend_code = request.data['friend_code']
        if(friend_code):
            try:
                friend = User.objects.get(invite_code=friend_code)
                friend.ticket = friend.ticket + 1
                friend.save()
            except:
                pass
        #user.cert_image = request.data['cert_img']
        return Response(data=None, status=status.HTTP_200_OK)
class WithdrawalView(APIView):
    """
        회원탈퇴 API
        
        ---
    """
    def post(self, request, *args, **kwargs):
        user = User.objects.select_related().get(id=request.user.id)
        user.delete()
        return Response(data=None, status=status.HTTP_200_OK)
class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
class CertificateView(APIView):
    """
        소속 인증 API
        
        ---
        # Body Schema
            - uploaded_file: 소속 인증 사진
        
    """
    def post(self, request, *args, **kwargs):
        TAG = "cert"
        file_name = save_uploaded_file(request.data['uploaded_file'], TAG)
        user = User.objects.get(id=request.user.id)
        user.cert_image = "http://106.10.39.154:9999/media/"+TAG+"/"+file_name
        user.user_certified = 1
        user.save()
        
        #async_image_upload.delay(file_path, request.user.id, 'cert')

        return Response(data=None, status=status.HTTP_200_OK)

class CertificateAdminView(APIView):
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.data['user'])
        notification_content = "인증이 완료되었어요! 즐거운 야미구 하세요!"
        #print(notification_content)
        notification_data = ""
        push_data = {
            'title': "야미구",
            'content': notification_content,
            'clickAction': ".NotificationActivity",
            'intentArgs': ""
        }
        firebase_message.send_push(user.id, push_data)
        firebase_message.send_notification(user.uid, 4, notification_content, notification_data)
        return Response(data=None, status=status.HTTP_200_OK)
    
class ChangeAvataView(APIView):
    """

        프로필 사진 변경 API
        
        ---
        # Body Schema
            - uploaded_file: 변경할 사진
        
    """
    def post(self, request, *args, **kwargs):
        TAG="avata"
        file_name = save_uploaded_file(request.data['uploaded_file'], TAG)
        user = User.objects.get(id=request.user.id)
        user.image = "http://106.10.39.154:9999/media/" + TAG + "/" + file_name
        user.save()
        rotate_image(get_file_path(file_name, TAG))
        return JsonResponse(data={
            'new_avata': user.image}, 
            status=status.HTTP_200_OK)
class ImageURLView(APIView):
    """

        프로필 사진 가져오는 API
        
        ---
        
    """
    permission_classes = [IsAuthenticated]
    def post(self, request, uid):
        user = User.objects.get(uid=uid)
        return JsonResponse(data={
       	    'profile_url': user.image},
       	    status=status.HTTP_200_OK)

class BuyTicketView(APIView):
    """
        티켓 구매 API

        ---
        # Body Schema
            - purchase_number: 구매 티켓 개수

    """
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # device_type = request.data["device"]
        # purchase_token = request.data["purchase_token"]
        # purchase_number = int(request.data["purchase_number"])
        # print("device_type: ", device_type)
        # print("purchase_token: ", purchase_token)
        # print("purchase_number: ", purchase_number)
        
        # package_name = ''
        # product_id = ''
        # if(device_type == 'android'):
        #     package_name = 'com.yamigu.yamigu_app' 
        #     if(purchase_number == 1):
        #         product_id = 'ticket_1'
        #     elif(purchase_number == 3):
        #         product_id = 'ticket_2_plus_1'
        #     product = androidpublisher.purchases().products().get(productId=product_id, packageName=package_name, token=purchase_token)
        #     purchase = product.execute()
        purchase_number = int(request.data["purchase_number"])
        user = User.objects.get(id=request.user.id)
        user.ticket = user.ticket + purchase_number
        user.save()

        return Response(data=None, status=status.HTTP_200_OK)
