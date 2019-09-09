from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Meeting)
admin.site.register(MatchRequest)
admin.site.register(MeetingType)
admin.site.register(PlaceType)
admin.site.register(Place)