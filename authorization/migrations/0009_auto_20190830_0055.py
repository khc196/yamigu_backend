# Generated by Django 2.2.3 on 2019-08-29 15:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0008_merge_20190830_0050'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.AddField(
            model_name='user',
            name='real_name',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=14, null=True, validators=[django.core.validators.RegexValidator(message='Phone number is invalid.', regex='\\d{3}[-]?\\d{4}[-]?\\d{4}')], verbose_name='phone number'),
        ),
    ]
