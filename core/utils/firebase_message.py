from fcm_django.models import FCMDevice
from firebase_admin import db
from datetime import datetime
def send_push(user_id, data):
    devices = FCMDevice.objects.filter(user=user_id)
    for device in devices:
        if(device.type == 'android'):
            device.send_message(data=data)
        else:
            device.send_message(data=data, title=data['title'], body=data['content'])
            
def send_notification(uid, notification_type, content, data):
    ref = db.reference('user/' + uid + '/notification')
    key = ref.push().key
    ref.child(key).set({
        'id': key,
        'type': notification_type,
        'content': content,
        'data': data,
        'isUnread': True,   
        'time': int((datetime.now() - datetime(1970, 1, 1)).total_seconds()* 1000)
    })
    