from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated

from django.http import Http404

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


class KakaoLoginView(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
