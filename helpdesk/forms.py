# -*- encoding: utf-8 -*-
from ckeditor.fields import RichTextFormField
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelChoiceField

from helpdesk.models import State, Comment, Ticket, Project, HelpdeskProfile


class ProfileChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        label = obj.helpdeskprofile.label if hasattr(obj, 'helpdeskprofile') else None
        return u'%s (%s)' % (obj.first_name, label) if label else obj.first_name

    def __init__(self, *args, **kwargs):
        queryset = User.objects.filter(groups__name='Helpdesk support').order_by('first_name')
        super(ProfileChoiceField, self).__init__(queryset, *args, **kwargs)


class CommentForm(forms.ModelForm):
    state = forms.ModelChoiceField(State.objects.all(), widget=forms.RadioSelect, initial='resolved')
    body = RichTextFormField()

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs['placeholder'] = u'Enter your answer here'
        self.fields['body'].label = u'Answer body'

    class Meta:
        model = Comment
        fields = ('body', 'state', 'internal')


class TicketForm(forms.ModelForm):
    assignee = ProfileChoiceField()

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['project'].empty_label = u'- None -'
        for fieldname in self.Meta.fields:
            self.fields[fieldname].show_hidden_initial = True

    class Meta:
        model = Ticket
        fields = ['assignee', 'priority', 'project', 'state']


class FilterForm(forms.Form):
    ASSIGNEES = (
        ('me', u'Me'),
        ('all', u'All')
    )
    MODES = (
        ('normal', u'Normal'),
        ('compact', u'Compact')
    )
    mode = forms.ChoiceField(choices=MODES)
    assignee = forms.ChoiceField(choices=ASSIGNEES)
    state = forms.ModelChoiceField(State.objects.all(), required=False, empty_label=u'All')
    project = forms.ModelChoiceField(Project.objects.all(), required=False, empty_label=u'All')

    def __init__(self, *args, **kwargs):
        email_filter = kwargs.pop('email_filter', False)
        super(FilterForm, self).__init__(*args, **kwargs)
        if email_filter:
            self.fields['email'] = forms.EmailField(required=False)


class TicketCreateForm(forms.ModelForm):
    comment = RichTextFormField()
    assignee = ProfileChoiceField()

    class Meta:
        model = Ticket
        fields = ['title', 'assignee', 'priority', 'project', 'state', 'customer', 'comment']


class SearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': u'Search by email, title or body',
    }))