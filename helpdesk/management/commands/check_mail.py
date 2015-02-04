# -*- encoding: utf-8 -*-
import logging
import re

from django.core.files.base import ContentFile
from django.core.management import BaseCommand
from imbox import Imbox

from helpdesk import SETTINGS
from helpdesk.models import Ticket, Comment, Project, MailAttachment


logger = logging.getLogger('helpdesk.mail')


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
            try:
                subject = getattr(message, 'subject', u'Email ticket')
                logger.info(u"Got message %s: %s" % (uid, subject))

                if Ticket.objects.filter(message_id=uid).exists() or Comment.objects.filter(message_id=uid).exists():
                    logger.info(u'  Message already exists, skipping')
                    continue

                try:
                    body = message.body['html'][0]
                except IndexError:
                    body = message.body['plain'][0]

                initial = self._get_initial_issue(message)

                if initial is None:
                    ticket = Ticket.create(
                        title=subject,
                        body=body,
                        customer=message.sent_from[0]['email'],
                        message_id=uid,
                        assignee=project.default_assignee,
                        project=project
                    )
                    logger.info(u'  Created new ticket')
                    self._create_attachments(message.attachments, ticket)
                else:
                    comment = Comment.objects.create(
                        body=body,
                        author=None,
                        message_id=uid,
                        ticket=initial
                    )
                    self._create_attachments(message.attachments, comment)
                    logger.info(u'  Added comment to ticket')

                if SETTINGS['mark_seen']:
                    imbox.mark_seen(uid)
            except Exception:
                logger.exception(u'  Error while retrieving email %s' % uid)

    def handle(self, *args, **options):
        imbox = Imbox('imap.gmail.com',
                      username=SETTINGS['username'],
                      password=SETTINGS['password'],
                      ssl=True)

        for project in Project.objects.all():
            self.handle_messages(imbox, project)

        imbox.logout()

    def _create_attachments(self, attachments, obj):
        for attachment in attachments:
            f = ContentFile(attachment['content'].read(), name=attachment['filename'])
            mail_attachment = MailAttachment(
                attachment=f, content_object=obj
            )
            mail_attachment.save()