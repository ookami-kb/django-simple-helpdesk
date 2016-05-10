# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('helpdesk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentFile',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('attachment_file', models.FileField()),
            ],
        ),
        migrations.AlterField(
            model_name='comment',
            name='message_id',
            field=models.CharField(max_length=255, unique=True, editable=False, default=uuid.uuid1),
        ),
        migrations.AlterField(
            model_name='mailattachment',
            name='attachment',
            field=models.OneToOneField(to='helpdesk.AttachmentFile'),
        ),
    ]
