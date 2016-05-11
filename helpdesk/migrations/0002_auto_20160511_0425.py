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
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('file_id', models.UUIDField(default=uuid.uuid1, editable=False)),
                ('attachment_file', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/avalas/projects/django-simple-helpdesk/attachments', base_url='/helpdesk/attachments/'), upload_to='tickets')),
            ],
        ),
        migrations.AlterField(
            model_name='comment',
            name='message_id',
            field=models.CharField(default=uuid.uuid1, editable=False, unique=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='mailattachment',
            name='attachment',
            field=models.OneToOneField(to='helpdesk.AttachmentFile'),
        ),
    ]
