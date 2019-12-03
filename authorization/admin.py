from django.contrib import admin
from django.utils.html import format_html

from .models import User

class UserAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        return format_html('<img src="{}" />'.format(obj.image.url))
    image_tag.short_description = 'Image'
    list_display = ['image_tag',]

# Register your models here.
admin.site.register(User, UserAdmin)
