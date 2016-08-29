# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SNSToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arn', models.CharField(max_length=128)),
                ('registration_id', models.TextField()),
                ('platform', models.CharField(max_length=4, choices=[(b'apns', b'APNS'), (b'gcm', b'GCM')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='snstoken',
            unique_together=set([('arn', 'user')]),
        ),
    ]
