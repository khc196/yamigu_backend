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
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "(%s)" % (self.description)
        
class Meeting(models.Model):
    meeting_type = models.ForeignKey(MeetingType, on_delete=models.CASCADE, null=True)
    openby = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="meeting_openby")
    date = models.DateField(null=False, blank=False)
    place_type = models.ForeignKey(PlaceType, on_delete=models.CASCADE, null=True, related_name="meeting_place_type")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, blank=True, null=True, related_name="meeting_place")
    appeal = models.TextField()
    is_matched = models.BooleanField(default=False)
    matched_meeting = models.ForeignKey("Meeting", on_delete=models.CASCADE, blank=True, null=True, related_name="meeting_matched")
    rating = models.OneToOneField(
        Rating,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="meeting_rating",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (
            ("openby", "date")
        )
    def __str__(self):
    	name = ""
    	if(self.openby != None):
    		name = self.openby.nickname
    	return "%d년 %d월 %d일 %s %s(%s)" % (self.date.year, self.date.month, self.date.day, self.meeting_type.name, self.place_type.name, name)

        

class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    image = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)

class MatchRequest(models.Model):
    receiver = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=False, related_name="match_receiver")
    sender = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=False, related_name="match_sender")
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="meeting_manager")
    is_selected = models.BooleanField(default=False)
    is_declined = models.BooleanField(default=False)
    manager_call = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        string =  "%d년 %d월 %d일 %s (%s - %s)" % (self.sender.date.year, self.sender.date.month, self.sender.date.day, self.sender.meeting_type.name, self.sender.openby.nickname, self.receiver.openby.nickname)
        
        return string


class AndroidVersion(models.Model):
    code = models.IntegerField(null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class IOSVersion(models.Model):
    code = models.IntegerField(null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)