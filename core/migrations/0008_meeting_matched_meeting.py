# Generated by Django 2.2.3 on 2019-09-30 02:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_matchrequest_is_declined'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='matched_meeting',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meeting_matched', to='core.Meeting'),
        ),
    ]
