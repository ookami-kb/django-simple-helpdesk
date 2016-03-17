import base64
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from django.utils.safestring import mark_safe

from helpdesk import SETTINGS
from helpdesk.signals import new_comment_from_client, ticket_updated, new_answer, ticket_pre_created, \
    ticket_post_created


class Project(models.Model):
    machine_name = models.CharField(max_length=64, primary_key=True)
    title = models.CharField(max_length=255)
    email = models.EmailField()
    default_assignee = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return self.title


class ProjectAlias(models.Model):
    project = models.ForeignKey(Project)
    email = models.EmailField(unique=True)
    assignee = models.ForeignKey(User, blank=True, null=True)


class HelpdeskProfile(models.Model):
    user = models.OneToOneField(User)
    signature = models.TextField(blank=True, null=True)
    send_notifications = models.BooleanField(default=True)
    label = models.CharField(max_length=255, blank=True, null=True)


class State(models.Model):
    COLORS = (
        ('default', 'Default'),
        ('primary', 'Primary'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info')
    )
    machine_name = models.CharField(max_length=32, primary_key=True)
    title = models.CharField(max_length=64)
    resolved = models.BooleanField(default=False)
    color = models.CharField(max_length=32, default='default', choices=COLORS)

    def __str__(self):
        return self.title

    @property
    def label(self):
        return mark_safe('<span class="label label-%s">%s</span>' % (self.color, self.title))


attachment_fs = FileSystemStorage(location=settings.BASE_DIR + '/attachments',
                                  base_url='/helpdesk/attachments/')


class MailAttachment(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    attachment = models.FileField(upload_to='tickets', storage=attachment_fs)

    @property
    def filename(self):
        return os.path.basename(self.attachment.name)

    @property
    def signed_url(self):
        signer = Signer()
        return reverse('helpdesk_attachment', args=[signer.sign(self.pk)])


class Ticket(models.Model):
    PRIORITIES = (
        (0, 'Low'),
        (1, 'Normal'),
        (2, 'High')
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    project = models.ForeignKey(Project, blank=True, null=True)
    state = models.ForeignKey(State, default='open')
    priority = models.IntegerField(choices=PRIORITIES, default=1)
    assignee = models.ForeignKey(User, blank=True, null=True, limit_choices_to={'groups__name': 'Helpdesk support'})
    customer = models.EmailField()
    message_id = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    attachments = GenericRelation(MailAttachment)

    @property
    def customer_user(self):
        try:
            return User.objects.get(email=self.customer)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def reply(self, text, author=None, state='resolved'):
        answer = Comment.objects.create(
            ticket=self,
            body=text,
            author=author or self.project.default_assignee
        )
        self.state = State.objects.get(machine_name=state)
        self.save()
        new_answer.send(sender=self.__class__, ticket=self, answer=answer)

    @staticmethod
    def create(**kwargs):
        author = kwargs.pop('author', None)
        ticket = Ticket(**kwargs)
        ticket_pre_created.send(sender=Ticket, sent_from=ticket.customer, ticket=ticket, author=author)
        ticket.save()
        ticket_post_created.send(sender=Ticket, instance=ticket, author=author)
        return ticket

    def notify_assignee(self, subject, template, **kwargs):
        if self.assignee is None:
            return

        if hasattr(self.assignee, 'helpdeskprofile') and not self.assignee.helpdeskprofile.send_notifications:
            return

        data = {
            'ticket': self,
        }
        data.update(kwargs)
        msg = EmailMessage(subject, render_to_string(template, data),
                           self.project.email if self.project else SETTINGS['from_email'],
                           [self.assignee.email])
        msg.content_subtype = 'html'
        msg.send(fail_silently=True)

    def notify_customer(self, subject, template, **kwargs):
        data = {
            'ticket': self,
            'signature': self.assignee.helpdeskprofile.signature if hasattr(self.assignee, 'helpdeskprofile') else None,
            'attachments': kwargs.get('attachments', []),
            'host': SETTINGS['host']
        }
        data.update(kwargs)
        msg = EmailMessage(subject, render_to_string(template, data),
                           self.project.email if self.project else SETTINGS['from_email'],
                           [self.customer])
        msg.content_subtype = 'html'
        msg.send(fail_silently=False)

    def get_absolute_url(self):
        return reverse('helpdesk_ticket', SETTINGS['urlconf'], args=[self.pk])

    def get_full_url(self):
        return ''.join([SETTINGS['host'] or 'http://' + get_current_site(None).domain, self.get_absolute_url()])

    def __str__(self):
        return 'HD-%d %s' % (self.pk, self.title)

    @property
    def priority_label(self):
        if self.priority == 0:
            color = 'default'
        elif self.priority == 1:
            color = 'info'
        else:
            color = 'danger'
        return mark_safe('<span class="label label-%s" title="%s">%s</span>' % (color,
                                                                                self.get_priority_display(),
                                                                                self.get_priority_display()[0]))

    class Meta:
        permissions = (
            ("view_customer", "Can view ticket customer"),
            ("view_tickets", "Can view tickets"),
            ("view_all_tickets", "Can view tickets assigned to other users"),
        )


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket)
    created = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    author = models.ForeignKey(User, blank=True, null=True, related_name='helpdesk_answers')
    internal = models.BooleanField(default=False, help_text='If checked this comment will not be emailed to client')
    notified = models.BooleanField(default=True, editable=False)
    message_id = models.CharField(max_length=256, blank=True, null=True)
    attachments = GenericRelation(MailAttachment)

    def is_from_client(self):
        return self.author is None


@receiver(post_save, sender=Comment, dispatch_uid='on_comment_inserted')
def on_comment_inserted(sender, **kwargs):
    if not kwargs['created']:
        return
    comment = kwargs['instance']
    if comment.is_from_client():
        comment.ticket.state = State.objects.get(pk='open')
        comment.ticket.save()
        new_comment_from_client.send(sender=sender, comment=comment, ticket=comment.ticket)


@receiver(ticket_post_created, sender=Ticket, dispatch_uid='on_ticket_save')
def on_ticket_save(sender, **kwargs):
    ticket = kwargs['instance']
    if kwargs.get('author', None) != ticket.assignee:
        ticket.notify_assignee('Ticket created', 'helpdesk/ticket_created.html')


@receiver(ticket_updated, dispatch_uid='on_ticket_update')
def on_ticket_update(sender, **kwargs):
    if kwargs['updater'] != kwargs['ticket'].assignee:
        kwargs['ticket'].notify_assignee('Ticket updated', 'helpdesk/ticket_updated.html',
                                         changes=kwargs['changes'], updater=kwargs['updater'])


@receiver(new_comment_from_client, dispatch_uid='on_new_client_comment')
def on_new_client_comment(sender, comment, ticket, **kwargs):
    ticket.notify_assignee('Comment added', 'helpdesk/comment_added.html')


@receiver(new_answer, dispatch_uid='on_new_answer')
def on_new_answer(sender, ticket, answer, **kwargs):
    if answer.author != ticket.assignee:
        ticket.notify_assignee('Answer added', 'helpdesk/answer_added.html', answer=answer)

    if not answer.internal:
        subject = 'Re: [HD-%d] %s' % (ticket.pk, ticket.title)
        try:
            ticket.notify_customer(subject, 'helpdesk/customer_answer.html',
                                   answer=answer, attachments=answer.attachments.all())
        except Exception as e:
            print('Error sending email:', e)
            import traceback
            traceback.print_exc()
            answer.notified = False
            ticket.state = State.objects.get(machine_name='open')

            answer.save()


class HistoryAction(models.Model):
    ticket = models.ForeignKey(Ticket)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    change = models.TextField()
