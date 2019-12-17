from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Meeting)
admin.site.register(Rating)
admin.site.register(MatchRequest)
admin.site.register(AndroidVersion)
admin.site.register(IOSVersion)
admin.site.register(MeetingType)
admin.site.register(PlaceType)