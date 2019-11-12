from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.conf import settings
from authorization.models import User
from core.utils.image import Compressor
import time,imghdr,os

@shared_task
def async_image_upload(file_path, user_id, tag):
    image_file = open(file_path,'rb')

    vaild_image_ext = ['jpg', 'jpeg', 'bmp', 'gif', 'png']
    image_ext = imghdr.what(image_file)
    if image_ext not in vaild_image_ext:
        return 'invalid extension'

    processed_image,width,height, is_portrait = Compressor.compress(image_file)
    processed_image_path = tag + '/image/' + str(user_id) + '_' + str(
        int(round(time.time() * 1000))) + '.' + image_ext

    # # try upload image to s3 bucket
    # try:
    #     s3_instance = S3()
    #     upload_image_res = s3_instance.upload_file_public(processed_image_path, processed_image)
    # except:
    #     return 'failed to upload'
    user = User.objects.get(id=user_id)
    if(tag == 'cert'):
        pass
    elif(tag == 'profile'):
        pass
    return 'success'
