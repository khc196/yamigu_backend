from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import User
from core.utils import firebase_message
import requests
class UserAdmin(admin.ModelAdmin):
    change_form_template = 'admin/change_form.html'
    list_filter = ('user_certified',)
    list_display = ('id', 'uid', 'nickname', 'age', 'gender_string', 'real_name', 'user_certified_string', 'ticket')
    list_editable = ('ticket',)
    search_fields = ('nickname', 'uid', 'real_name')
    readonly_fields = ('uid', 'firebase_token', 'real_name', 'avata', 'image', 'cert_img', 'cert_image', 'last_login', 'created_at')
    exclude = ('is_admin', 'is_staff', 'is_active', 'password', 'groups', 'user_permissions', 'Superuser_status')
    ordering = ('-id',)
    
    def gender_string(self, obj):
        gen_str = '' 
        if obj.gender == 1:
            gen_str = '남'
        elif obj.gender == 0:
            gen_str = '여'
        return gen_str
    def user_certified_string(self, obj):
        cer_str = '미인증' 
        if(obj.user_certified == 1):
            cer_str = '진행중'
        elif(obj.user_certified == 2):
            cer_str = '완료'
        return cer_str
    def avata(self, obj):
        if(obj.image != None):
            return mark_safe('<img src="{url}" width="320px" />'.format(url = obj.image))
        return ""
    def cert_img(self, obj):
        if(obj.cert_image != None):
            return mark_safe('<img src="{url}" width="320px" />'.format(url = obj.cert_image))
        return ""
    def has_add_permission(self, request):
        return False
    def response_change(self, request, obj):
        if "certificate" in request.POST:
            obj.user_certified = 2
            obj.ticket = obj.ticket + 1
            obj.save()
            data = {'user': obj.id} 
            res = requests.post("http://106.10.39.154:9999/api/manager/certificate/user/", data=data)
        return super().response_change(request, obj)
    gender_string.short_description = "성별"
    avata.short_description = "프로필 사진"
    cert_img.short_description = "인증 사진"
# Register your models here.
admin.site.register(User, UserAdmin)
