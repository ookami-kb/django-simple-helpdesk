from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource

from helpdesk.models import Ticket, State


class StateResource(ModelResource):
    class Meta:
        queryset = State.objects.all()


class AssigneeResource(ModelResource):
    full_name = fields.CharField('get_full_name', default='Unknown')

    class Meta:
        queryset = User.objects.filter(groups__name='Helpdesk support')
        fields = ['id']


class TicketResource(ModelResource):
    state = fields.ForeignKey(StateResource, 'state', full=True)
    project = fields.CharField('project_title')
    assignee = fields.ForeignKey(AssigneeResource, 'assignee', full=True)

    class Meta:
        queryset = Ticket.objects.all()
        resource_name = 'ticket'
        ordering = ['priority', 'updated', 'title']
