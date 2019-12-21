from django.contrib import admin
from .models import *
# Register your models here.

class MeetingAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)

class MatchRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)

admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Rating)
admin.site.register(MatchRequest)
admin.site.register(AndroidVersion)
admin.site.register(IOSVersion)
admin.site.register(MeetingType)
admin.site.register(PlaceType)

