# Generated by Django 2.2.3 on 2019-08-22 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0002_auto_20190822_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, max_length=70),
        ),
    ]
