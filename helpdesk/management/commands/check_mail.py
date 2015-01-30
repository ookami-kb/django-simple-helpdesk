# -*- encoding: utf-8 -*-
import re

from django.core.management import BaseCommand
from imbox import Imbox
from helpdesk import SETTINGS

from helpdesk.models import Ticket, Comment, Project
from helpdesk.signals import ticket_pre_created


class BlackList(object):
    def __contains__(self, value):
        return value not in ['script']


class Command(BaseCommand):
    def _get_initial_issue(self, message):
        subject = getattr(message, 'subject', u'Email ticket')
        customer = message.sent_from[0]['email']
        pattern = re.compile(r'.*\[HD-(\d+)\].*')
        m = pattern.match(subject)
        if m:
            pk = m.group(1)
        else:
            return None

        try:
            return Ticket.objects.get(customer=customer, pk=pk)
        except Ticket.DoesNotExist:
            return None

    def handle_messages(self, imbox, project):
        unread_messages = imbox.messages(unread=True, folder='INBOX', sent_to=project.email)
        for uid, message in unread_messages:
            if Ticket.objects.filter(message_id=uid).exists() or Comment.objects.filter(message_id=uid).exists():
                continue

            try:
                body = message.body['html'][0]
            except IndexError:
                body = message.body['plain'][0]

            initial = self._get_initial_issue(message)
            subject = getattr(message, 'subject', u'Email ticket')

            print u'Processing message: %s' % subject

            if initial is None:
                ticket = Ticket(
                    title=subject,
                    body=body,
                    customer=message.sent_from[0]['email'],
                    message_id=uid,
                    assignee=project.default_assignee,
                    project=project
                )
                ticket_pre_created.send(sender=Ticket, sent_from=message.sent_from[0]['email'], ticket=ticket)
                ticket.save()
            else:
                Comment.objects.create(
                    body=body,
                    author=None,
                    message_id=uid,
                    ticket=initial
                )

            imbox.mark_seen(uid)

    def handle(self, *args, **options):
        imbox = Imbox('imap.gmail.com',
                      username=SETTINGS['username'],
                      password=SETTINGS['password'],
                      ssl=True)

        for project in Project.objects.all():
            self.handle_messages(imbox, project)

        imbox.logout()