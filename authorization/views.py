from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from django.http import Http404, JsonResponse

from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from .serializers import UserSerializer
from .models import User


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if user is None:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = User.objects.select_related().get(id=user.id)
        serializer = UserSerializer(queryset, many=False)
        return Response(serializer.data)

class NicknameValidator(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, nickname):
    
        if(not nickname or User.objects.filter(nickname=nickname).exists()):
            return JsonResponse({
                "is_available": False
            })
        else:
            return JsonResponse({
                "is_available": True
            })
            
class ChangeNicknameView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        user.nickname = request.data['nickname']
        user.save()
        return Response(data=None, status=status.HTTP_200_OK)

class SignUpView(APIView):
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
        user.save()
        return Response(data=None, status=status.HTTP_200_OK)
class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
