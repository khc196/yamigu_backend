from .models import User

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super(SocialAccountAdapter, self).save_user(request, sociallogin, form)
        social_app_name = sociallogin.account.provider.upper()
        User.objects.create_kakao_user(user_pk=user.pk, extra_data=sociallogin.account.extra_data)
    def pre_social_login(self, request, sociallogin):
        print(sociallogin)