# -*- encoding: utf-8 -*-
from ckeditor.fields import RichTextFormField
from django import forms

from helpdesk.models import State, Comment, Ticket, Project


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


class TicketCreateForm(forms.ModelForm):
    comment = RichTextFormField()

    class Meta:
        model = Ticket
        fields = ['title', 'assignee', 'priority', 'project', 'state', 'customer', 'comment']