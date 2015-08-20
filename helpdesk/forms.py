from ckeditor.fields import RichTextFormField
from django import forms
from django.contrib.auth.models import User
from django.db.models import Count
from django.forms import ModelChoiceField

from helpdesk.models import State, Comment, Ticket, Project, HelpdeskProfile


class ProfileChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        label = obj.helpdeskprofile.label if hasattr(obj, 'helpdeskprofile') else None
        return '%s (%s)' % (obj.get_full_name(), label) if label else obj.first_name

    def __init__(self, *args, **kwargs):
        queryset = User.objects.filter(groups__name='Helpdesk support').order_by('first_name')
        super(ProfileChoiceField, self).__init__(queryset, *args, **kwargs)


class CommentForm(forms.ModelForm):
    state = forms.ModelChoiceField(State.objects.all(), widget=forms.RadioSelect, initial='resolved')
    body = RichTextFormField()

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget.attrs['placeholder'] = 'Enter your answer here'
        self.fields['body'].label = 'Answer body'

    class Meta:
        model = Comment
        fields = ('body', 'state', 'internal')


class TicketForm(forms.ModelForm):
    assignee = ProfileChoiceField()

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['project'].empty_label = '- None -'
        for fieldname in self.Meta.fields:
            self.fields[fieldname].show_hidden_initial = True

    class Meta:
        model = Ticket
        fields = ['assignee', 'priority', 'project', 'state']


class FilterForm(forms.Form):
    ASSIGNEES = (
        ('me', 'Me'),
        ('all', 'All')
    )
    MODES = (
        ('normal', 'Normal'),
        ('compact', 'Compact')
    )
    mode = forms.ChoiceField(choices=MODES)
    assignee = forms.ChoiceField(choices=ASSIGNEES)
    state = forms.ModelChoiceField(State.objects.all(), required=False, empty_label='All')
    project = forms.ModelChoiceField(Project.objects.all(), required=False, empty_label='All')

    def _get_user_label(self, user):
        label = user.helpdeskprofile.label if hasattr(user, 'helpdeskprofile') else None
        return '{} ({})'.format(user.first_name, label) if label else user.first_name

    def __init__(self, *args, **kwargs):
        email_filter = kwargs.pop('email_filter', False)
        view_assignees = kwargs.pop('view_assignees', False)
        super(FilterForm, self).__init__(*args, **kwargs)
        if email_filter:
            self.fields['email'] = forms.EmailField(required=False)

        if view_assignees:
            choices = User.objects.filter(ticket__isnull=False, ticket__state='open').annotate(
                tickets=Count('ticket')).order_by('-tickets')
            assignees = self.ASSIGNEES + tuple(
                (u.pk, '{} - {}'.format(self._get_user_label(u), u.tickets)) for u in choices
            )
            self.fields['assignee'].choices = assignees


class TicketCreateForm(forms.ModelForm):
    comment = RichTextFormField()
    assignee = ProfileChoiceField()

    class Meta:
        model = Ticket
        fields = ['title', 'assignee', 'priority', 'project', 'state', 'customer', 'comment']


class SearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search by email, title or body',
    }))
