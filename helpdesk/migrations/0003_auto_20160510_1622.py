# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('helpdesk', '0002_auto_20160510_0712'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AddField(
            model_name='attachmentfile',
            name='file_id',
            field=models.CharField(editable=False, unique=True, default=uuid.uuid1, max_length=255),
        ),
        migrations.AlterField(
            model_name='attachmentfile',
            name='attachment_file',
            field=models.FileField(upload_to='tickets', storage=django.core.files.storage.FileSystemStorage(base_url='/helpdesk/attachments/', location='/home/avalas/projects/django-simple-helpdesk/attachments')),
        ),
        migrations.AlterField(
            model_name='comment',
            name='ticket',
            field=models.ForeignKey(to='helpdesk.Ticket', related_name='comments'),
        ),
    ]
