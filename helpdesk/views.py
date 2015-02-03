# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import TemplateView, ListView, DetailView, View, CreateView
import time

from helpdesk import Filter
from helpdesk.forms import CommentForm, TicketForm, FilterForm, TicketCreateForm
from helpdesk.models import Ticket, HistoryAction, Comment
from helpdesk.signals import new_answer, ticket_updated


class TestView(TemplateView):
    template_name = 'test.html'


class HomeView(ListView):
    template_name = 'helpdesk/home.html'
    filter_form = None
    filter = None

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        return context

    def dispatch(self, request, *args, **kwargs):
        self.filter = Filter(request)
        self.filter_form = FilterForm(data=request.POST or None, initial=self.filter.get_form_init())
        return super(HomeView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.filter_form.is_valid():
            self.filter.by_assignee(self.filter_form.cleaned_data['assignee'])
            self.filter.by_state(self.filter_form.cleaned_data['state'])
            self.filter.by_project(self.filter_form.cleaned_data['project'])
            return HttpResponseRedirect(reverse('helpdesk_home'))
        return self.render_to_response(self.get_context_data())

    def get_queryset(self):
        queryset = Ticket.objects.all()
        filters = self.filter.get_filters()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset.order_by('-updated')


class TicketCreateView(CreateView):
    model = Ticket
    template_name = 'helpdesk/ticket_create.html'
    form_class = TicketCreateForm

    def form_valid(self, form):
        data = form.cleaned_data
        comment = data.pop('comment')
        ticket = Ticket.create(body=u'This ticket was created by [user:%d]' % self.request.user.pk,
                               message_id=u'ticket-%d' % time.mktime(now().timetuple()),
                               author=self.request.user,
                               **data)
        reply = Comment.objects.create(ticket=ticket, body=comment, author=self.request.user)
        new_answer.send(sender=Comment, ticket=ticket, answer=reply)
        return HttpResponseRedirect(reverse('helpdesk_home'))


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

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.reply_form = CommentForm(request.POST or None if 'reply' in request.POST else None)
        self.ticket_form = TicketForm(request.POST or None if 'ticket' in request.POST else None,
                                      instance=self.object)
        return super(TicketView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        self.object = ticket
        if 'reply' in request.POST and self.reply_form.is_valid():
            reply = self.reply_form.save(commit=False)
            reply.author = request.user
            reply.ticket = ticket
            reply.save()

            ticket.state = self.reply_form.cleaned_data['state']
            ticket.save()

            new_answer.send(sender=Comment, ticket=ticket, answer=reply)
            HistoryAction.objects.create(
                user=reply.author,
                change=u'added %scomment and set state to <i>%s</i>' % (
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
                changes.append(u'%s: %s → %s' % (fieldname, old_value, new_value))
            self.object.save(update_fields=self.ticket_form.changed_data)
            if changes:
                HistoryAction.objects.create(
                    user=request.user,
                    change=u'\n'.join(changes),
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
        return context

