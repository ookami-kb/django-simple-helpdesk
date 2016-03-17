# -*- encoding: utf-8 -*-
from mimetypes import guess_type
import time

from django.contrib.contenttypes.forms import generic_inlineformset_factory
from django.core.signing import Signer, BadSignature
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.http import urlencode
from django.utils.timezone import now
from django.views.generic import TemplateView, ListView, DetailView, View, CreateView

from helpdesk import Filter
from helpdesk.forms import CommentForm, TicketForm, FilterForm, TicketCreateForm, SearchForm
from helpdesk.models import Ticket, HistoryAction, Comment, MailAttachment
from helpdesk.signals import new_answer, ticket_updated


class TestView(TemplateView):
    template_name = 'test.html'


class HomeView(ListView):
    template_name = 'helpdesk/home.html'
    filter_form = None
    filter = None
    paginate_by = 20
    search = None
    search_form = None

    def _get_list_template(self):
        mode = self.request.session.get('mode', 'normal')
        if mode not in ['normal', 'compact']:
            mode = 'normal'

        if mode == 'normal':
            return 'helpdesk/ticket_list.html'
        else:
            return 'helpdesk/ticket_list_compact.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        context['list_template'] = self._get_list_template()
        context['search_form'] = self.search_form
        context['search'] = self.search
        context['extra'] = urlencode({'search': self.search}) if self.search else None
        return context

    def dispatch(self, request, *args, **kwargs):
        self.search_form = SearchForm(request.GET)
        if self.search_form.is_valid():
            self.search = self.search_form.cleaned_data.get('search', None)

        self.filter = Filter(request)
        initial = self.filter.get_form_init()
        initial.update(
            {'mode': request.session.get('mode', 'normal')}
        )
        self.filter_form = FilterForm(data=request.POST or None, initial=initial,
                                      email_filter=request.user.has_perm('helpdesk.view_customer'),
                                      view_assignees=request.user.has_perm('helpdesk.view_customer'))
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.filter_form.is_valid():
            self.filter.by_assignee(self.filter_form.cleaned_data['assignee'])
            self.filter.by_state(self.filter_form.cleaned_data['state'])
            self.filter.by_project(self.filter_form.cleaned_data['project'])
            self.filter.by_email(self.filter_form.cleaned_data.get('email', None))

            self.request.session['mode'] = self.filter_form.cleaned_data['mode']

            return HttpResponseRedirect(reverse('helpdesk_home'))
        return self.render_to_response(self.get_context_data())

    def get_queryset(self):
        queryset = Ticket.objects.all()
        filters = self.filter.get_filters()
        if filters:
            queryset = queryset.filter(**filters)
        if self.search:
            keywords = [w for w in self.search.split(' ') if w]
            print(keywords)
            qs = Q()
            for word in keywords:
                qs |= Q(customer__icontains=word) | Q(title__icontains=word) | Q(body__icontains=word)
            queryset = queryset.filter(qs)
        return queryset.order_by('-updated')


AttachmentFormset = generic_inlineformset_factory(MailAttachment, can_delete=False, extra=3)


class TicketCreateView(CreateView):
    model = Ticket
    template_name = 'helpdesk/ticket_create.html'
    form_class = TicketCreateForm
    attachment_formset = None

    def dispatch(self, request, *args, **kwargs):
        self.attachment_formset = AttachmentFormset(data=request.POST or None, files=request.FILES or None)
        return super(TicketCreateView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.attachment_formset.is_valid():
            return self.render_to_response(self.get_context_data())
        data = form.cleaned_data
        comment = data.pop('comment')
        ticket = Ticket.create(body='This ticket was created by [user:%d]' % self.request.user.pk,
                               message_id='ticket-%d' % time.mktime(now().timetuple()),
                               author=self.request.user,
                               **data)
        reply = Comment.objects.create(ticket=ticket, body=comment, author=self.request.user)

        self.attachment_formset.instance = reply
        self.attachment_formset.save()

        new_answer.send(sender=Comment, ticket=ticket, answer=reply)
        return HttpResponseRedirect(reverse('helpdesk_home'))

    def get_context_data(self, **kwargs):
        context = super(TicketCreateView, self).get_context_data(**kwargs)
        context['attachment_formset'] = self.attachment_formset
        return context


class EmailView(View):
    def get(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=kwargs['pk'])
        return HttpResponse(ticket.body)


class CommentEmailView(View):
    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['pk'])
        return HttpResponse(comment.body)


class TicketView(DetailView):
    template_name = 'helpdesk/ticket.html'
    model = Ticket
    reply_form = None
    ticket_form = None
    attachment_formset = None

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.reply_form = CommentForm(request.POST or None if 'reply' in request.POST else None)
        self.ticket_form = TicketForm(request.POST or None if 'ticket' in request.POST else None,
                                      instance=self.object)
        self.attachment_formset = AttachmentFormset(data=request.POST or None if 'reply' in request.POST else None,
                                                    files=request.FILES or None)
        return super(TicketView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        self.object = ticket
        if 'reply' in request.POST and self.reply_form.is_valid() and self.attachment_formset.is_valid():
            reply = self.reply_form.save(commit=False)
            reply.author = request.user
            reply.ticket = ticket
            reply.save()

            self.attachment_formset.instance = reply
            self.attachment_formset.save()

            ticket.state = self.reply_form.cleaned_data['state']
            ticket.save()

            new_answer.send(sender=Comment, ticket=ticket, answer=reply)
            HistoryAction.objects.create(
                user=reply.author,
                change='added %scomment and set state to <i>%s</i>' % (
                    'internal ' if reply.internal else '',
                    reply.ticket.state),
                ticket=reply.ticket
            )

            return HttpResponseRedirect(reverse('helpdesk_home'))
        elif 'ticket' in request.POST and self.ticket_form.is_valid():
            changes = []
            for fieldname in self.ticket_form.changed_data:
                old_value = self._get_display_value(fieldname)
                setattr(self.object, fieldname, self.ticket_form.cleaned_data[fieldname])
                new_value = self._get_display_value(fieldname)
                changes.append('%s: %s → %s' % (fieldname, old_value, new_value))
            self.object.save(update_fields=self.ticket_form.changed_data)
            if changes:
                HistoryAction.objects.create(
                    user=request.user,
                    change='\n'.join(changes),
                    ticket=self.object
                )
                ticket_updated.send(sender=Ticket,
                                    changed_data=self.ticket_form.changed_data,
                                    changes=changes,
                                    ticket=self.object,
                                    updater=request.user)
            return HttpResponseRedirect(reverse('helpdesk_home'))
        return self.render_to_response(self.get_context_data())

    def _get_display_value(self, fieldname):
        try:
            return getattr(self.object, 'get_%s_display' % fieldname)()
        except:
            return getattr(self.object, fieldname)

    def get_comments(self):
        return self.object.comment_set.all().order_by('created')

    def get_context_data(self, **kwargs):
        context = super(TicketView, self).get_context_data(**kwargs)
        context['comments'] = self.get_comments()
        context['reply_form'] = self.reply_form
        context['ticket_form'] = self.ticket_form
        context['history'] = self.object.historyaction_set.all().order_by('-created')
        context['attachments'] = self.object.attachments.all()
        context['attachment_formset'] = self.attachment_formset
        return context


class AttachmentView(View):
    def dispatch(self, request, *args, **kwargs):
        try:
            mid = Signer().unsign(kwargs['signature'])

            a = get_object_or_404(MailAttachment, pk=mid)
            attachment = a.attachment
            response = HttpResponse()
            response['X-Sendfile'] = attachment.path.encode('utf-8')
            response['Content-Length'] = attachment.size
            response['Content-Type'] = guess_type(attachment.name.split('/')[-1])[0]
            response['Content-Disposition'] = 'attachment; filename=%s' % attachment.name.split('/')[-1]
            return response
        except BadSignature:
            raise Http404
