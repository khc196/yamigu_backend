# Generated by Django 2.2.3 on 2019-10-15 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0013_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='firebase_token',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
