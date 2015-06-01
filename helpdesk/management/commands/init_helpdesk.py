# -*- encoding: utf-8 -*-
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from helpdesk.models import State


class Command(BaseCommand):
    def handle(self, *args, **options):
        State.objects.get_or_create(machine_name='open', color='danger', resolved=False, title='Open')
        State.objects.get_or_create(machine_name='resolved', color='success', resolved=True, title='Resolved')
        Group.objects.get_or_create(name='Helpdesk support')