# Generated by Django 2.2.3 on 2019-09-05 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0012_auto_20190830_0212'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
