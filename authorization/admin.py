from django.contrib import admin
from .models import User

# Register your models here.
admin.site.register(User)

fields = ( 'image_tag', )
readonly_fields = ('image_tag',)