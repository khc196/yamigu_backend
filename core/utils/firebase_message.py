from fcm_django.models import FCMDevice
from firebase_admin import db
from datetime import datetime
from authorization.models import User
import threading

def send_push_thread(user_id, data, is_chat=False):
    devices = FCMDevice.objects.filter(user=user_id)
    user = User.objects.get(id=user_id)
    ref = db.reference('user/{}/notifications'.format(user.uid))
    badge = 0
    for noti in ref.get().values():
        if noti['isUnread']:
            badge = badge + 1
    if is_chat:
        badge = badge + 1
    for device in devices:
        if(not device.active):
            continue
        if(device.type == 'android'):
            device.send_message(data=data)
        else:
            device.send_message(data=data, title=data['title'], body=data['content'], badge=badge)
def send_notification_thread(uid, notification_type, content, data):
    ref = db.reference('user/{}/notifications'.format(uid))
    key = ref.push().key
    ref.child(key).set({
        'id': key,
        'type': notification_type,
        'content': content,
        'data': data,
        'isUnread': True,   
        'time': int(((datetime.now() - datetime(1970, 1, 1)).total_seconds() - 3600 * 9)* 1000)
    })
    
def send_push(user_id, data, is_chat=False):
    t = threading.Thread(target=send_push_thread, args=(user_id, data, is_chat))
    t.start()
def send_notification(uid, notification_type, content, data):   
    t = threading.Thread(target=send_notification_thread, args=(uid, notification_type, content, data))
    t.start()
