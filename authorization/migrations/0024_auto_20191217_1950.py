# Generated by Django 2.2.3 on 2019-12-17 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0023_user_invite_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chat_on',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='push_on',
            field=models.BooleanField(default=True),
        ),
    ]
