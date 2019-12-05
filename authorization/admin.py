from django.contrib import admin

from .models import User

class UserAdmin(admin.ModelAdmin):
	list_display = ('id', 'uid', 'nickname', 'real_name', 'user_certified')
	search_fields = ('nickname', 'uid', 'real_name')
	ordering = ('-id',)

# Register your models here.
admin.site.register(User, UserAdmin)
