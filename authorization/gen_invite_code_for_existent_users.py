from .models import User, generateInviteCode

users = User.objects

for user in users:
    if(not user.invite_code):
        invite_code = generateInviteCode()
        while(True):
            try: 
                if(User.objects.filter(invite_code=invite_code).exists()):
                    invite_code = generateInviteCode()
                else:
                    break
            except User.DoesNotExist:
                break
        user.invite_code = invite_code
        user.save()