# -*- encoding: utf-8 -*-
import logging
import re

from django.core.files.base import ContentFile
from django.core.management import BaseCommand

from imbox import Imbox

from helpdesk import SETTINGS
from helpdesk.models import Ticket, Comment, Project, MailAttachment, ProjectAlias

logger = logging.getLogger('helpdesk.mail')


class BlackList(object):
    def __contains__(self, value):
        return value not in ['script']


class Command(BaseCommand):
    server = None

    def _get_initial_issue(self, message):
        subject = getattr(message, 'subject', 'Email ticket')
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

    def handle_messages(self, imbox, project, email=None, assignee=None):
        logger.info("--- Started processing emails ---")
        unread_messages = imbox.messages(unread=True, folder='INBOX', sent_to=email or project.email)
        for uid, message in unread_messages:
            try:
                subject = getattr(message, 'subject', 'Email ticket')
                logger.info("Got message %s: %s" % (uid, subject))

                if Ticket.objects.filter(message_id=uid).exists() or Comment.objects.filter(message_id=uid).exists():
                    logger.info('  Message already exists, skipping')
                    if SETTINGS['mark_seen']:
                        imbox.mark_seen(uid)
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
                        assignee=assignee or project.default_assignee,
                        project=project
                    )
                    logger.info('  Created new ticket')
                    self._create_attachments(message.attachments, ticket)
                else:
                    comment = Comment.objects.create(
                        body=body,
                        author=None,
                        message_id=uid,
                        ticket=initial
                    )
                    self._create_attachments(message.attachments, comment)
                    logger.info('  Added comment to ticket')

                if SETTINGS['mark_seen']:
                    imbox.mark_seen(uid)
            except Exception:
                logger.exception('  Error while retrieving email %s' % uid)
        logger.info("--- Finished processing emails ---")

    def handle(self, *args, **options):
        logger.info("===== Started check_mail =====")
        imbox = Imbox('imap.gmail.com',
                      username=SETTINGS['username'],
                      password=SETTINGS['password'],
                      ssl=True)

        for project in Project.objects.all():
            logger.info("=== Processing project %s ===" % project.title)
            self.handle_messages(imbox, project)

        for alias in ProjectAlias.objects.all():
            logger.info("=== Processing alias '{alias}' for project '{project}' ===".format(
                alias=alias.email,
                project=alias.project.title)
            )
            self.handle_messages(imbox, alias.project, email=alias.email, assignee=alias.assignee)

        imbox.logout()
        logger.info("===== Finished check_mail =====")

    def _create_attachments(self, attachments, obj):
        for attachment in attachments:
            f = ContentFile(attachment['content'].read(), name=attachment.get('filename', 'Attachment'))
            mail_attachment = MailAttachment(
                attachment=f, content_object=obj
            )
            mail_attachment.save()
