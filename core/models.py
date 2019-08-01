from django.db import models

class Meeting(models.Model):
    meeting_type = models.ForeignKey(MeetingType, on_delete=models.SET_NULL, null=True)
    man = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    woman = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    openby = models.ForeignKey(setting.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateField(null=False, blank=False)
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)
    appeal = models.TextField()
    rating = models.ForeignKey(Rating, on_delete=models.SET_NULL, null=True)
    is_matched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)   

class MeetingType(models.Model):
    name = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class PlaceType(models.Model):
    name = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField()
    place_type = models.ForeignKey(PlaceType, on_delete=model.CASCADE)
    is_premium = models.BooleanField(default=False)
    description = models.TextField()
    link = models.TextField()
    created_At = models.DateTimeField(auto_now_add=True)
class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    image = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    
