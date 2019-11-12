from django.conf import settings
import uuid
import os

def save_uploaded_file(f):
    ext = f.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path =  os.path.join(settings.MEDIA_ROOT, filename)

    with open(file_path, 'wb+') as destination:
       for chunk in f.chunks():
            destination.write(chunk)

    return filename