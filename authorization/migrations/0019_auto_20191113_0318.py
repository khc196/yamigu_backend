# Generated by Django 2.2.3 on 2019-11-12 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0018_auto_20191107_2325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_certified',
        ),
        migrations.AddField(
            model_name='user',
            name='user_certified',
            field=models.IntegerField(default=0),
        ),
    ]
