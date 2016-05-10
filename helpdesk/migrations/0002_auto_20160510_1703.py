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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('file_id', models.CharField(unique=True, max_length=255, default=uuid.uuid1, editable=False)),
                ('attachment_file', models.FileField()),
            ],
        ),

        migrations.AlterField(
            model_name='comment',
            name='message_id',
            field=models.CharField(unique=True, max_length=255, default=uuid.uuid1, editable=False),
        ),
        migrations.AlterField(
            model_name='comment',
            name='ticket',
            field=models.ForeignKey(to='helpdesk.Ticket', related_name='comments'),
        ),
        migrations.AlterField(
            model_name='mailattachment',
            name='attachment',
            field=models.OneToOneField(to='helpdesk.AttachmentFile'),
        ),
    ]
