# Generated by Django 2.2.3 on 2019-08-22 12:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_certified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=14, validators=[django.core.validators.RegexValidator(message='Phone number is invalid.', regex='d{3}[- ]?\\d{4}[- ]?\\d{4}')], verbose_name='phone number'),
        ),
    ]
