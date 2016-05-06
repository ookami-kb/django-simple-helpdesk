# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('helpdesk', '0002_auto_20160503_0951'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachmentFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('attachment_file', models.FileField(storage=django.core.files.storage.FileSystemStorage(base_url='/helpdesk/attachments/', location='/home/avalas/projects/django-simple-helpdesk/attachments'), upload_to='tickets')),
            ],
        ),
        migrations.CreateModel(
            name='Assignee',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.AlterField(
            model_name='comment',
            name='ticket',
            field=models.ForeignKey(to='helpdesk.Ticket', related_name='comments'),
        ),
        migrations.AlterField(
            model_name='mailattachment',
            name='attachment',
            field=models.OneToOneField(to='helpdesk.AttachmentFile', null=True, blank=True),
        ),
    ]
