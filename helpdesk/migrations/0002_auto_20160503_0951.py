# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('helpdesk', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='message_id',
            field=models.UUIDField(default=uuid.uuid1, editable=False),
        ),
    ]
