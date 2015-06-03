# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField()),
                ('internal', models.BooleanField(help_text='If checked this comment will not be emailed to client', default=False)),
                ('notified', models.BooleanField(editable=False, default=True)),
                ('message_id', models.CharField(max_length=256, blank=True, null=True)),
                ('author', models.ForeignKey(related_name='helpdesk_answers', blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HelpdeskProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('signature', models.TextField(blank=True, null=True)),
                ('send_notifications', models.BooleanField(default=True)),
                ('label', models.CharField(max_length=255, blank=True, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HistoryAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('change', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='MailAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('object_id', models.PositiveIntegerField()),
                ('attachment', models.FileField(storage=django.core.files.storage.FileSystemStorage(base_url='/helpdesk/attachments/', location='/home/ookami/projects/attachments'), upload_to='tickets')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('machine_name', models.CharField(primary_key=True, serialize=False, max_length=64)),
                ('title', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('default_assignee', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('assignee', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('project', models.ForeignKey(to='helpdesk.Project')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('machine_name', models.CharField(primary_key=True, serialize=False, max_length=32)),
                ('title', models.CharField(max_length=64)),
                ('resolved', models.BooleanField(default=False)),
                ('color', models.CharField(choices=[('default', 'Default'), ('primary', 'Primary'), ('success', 'Success'), ('warning', 'Warning'), ('danger', 'Danger'), ('info', 'Info')], max_length=32, default='default')),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('priority', models.IntegerField(choices=[(0, 'Low'), (1, 'Normal'), (2, 'High')], default=1)),
                ('customer', models.EmailField(max_length=254)),
                ('message_id', models.CharField(unique=True, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('assignee', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
                ('project', models.ForeignKey(to='helpdesk.Project', blank=True, null=True)),
                ('state', models.ForeignKey(to='helpdesk.State', default='open')),
            ],
            options={
                'permissions': (('view_customer', 'Can view ticket customer'), ('view_tickets', 'Can view tickets'), ('view_all_tickets', 'Can view tickets assigned to other users')),
            },
        ),
        migrations.AddField(
            model_name='historyaction',
            name='ticket',
            field=models.ForeignKey(to='helpdesk.Ticket'),
        ),
        migrations.AddField(
            model_name='historyaction',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comment',
            name='ticket',
            field=models.ForeignKey(to='helpdesk.Ticket'),
        ),
    ]
