from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _


class MeetingType(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PlaceType(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=30)
    place_type = models.ForeignKey(PlaceType, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)
    description = models.TextField()
    link = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Rating(models.Model):
    visual = models.IntegerField()
    fun = models.IntegerField()
    manner = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Meeting(models.Model):
    meeting_type = models.ForeignKey(MeetingType, on_delete=models.SET_NULL, null=True)
    man = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="meeting_man")
    woman = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="meeting_woman")
    openby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="meeting_openby")
    date = models.DateField(null=False, blank=False)
    place_type = models.ForeignKey(PlaceType, on_delete=models.SET_NULL, null=True, related_name="meeting_place_type")
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True, related_name="meeting_place")
    appeal = models.TextField()
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null=True)
    is_matched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    image = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
