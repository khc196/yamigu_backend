from django.conf import settings
import uuid
import os

def save_uploaded_file(f, TAG):
    ext = f.name.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    print(filename)
    root_path = os.path.join(settings.MEDIA_ROOT, TAG)
    file_path =  os.path.join(root_path, filename)

    with open(file_path, 'wb+') as destination:
       for chunk in f.chunks():
            destination.write(chunk)

    return filename
