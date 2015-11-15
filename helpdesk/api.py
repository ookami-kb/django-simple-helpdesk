from django.contrib.auth.models import User
from tastypie import fields
from tastypie.constants import ALL_WITH_RELATIONS
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
        excludes = ['body']
        filtering = {
            'state': ALL_WITH_RELATIONS,
        }

    def dehydrate_customer(self, bundle):
        if not bundle.request.user.has_perm('helpdesk.view_customer'):
            return None
        return bundle.obj.customer

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super().build_filters(filters)

        if 'state' in filters:
            orm_filters['state__machine_name'] = filters['state']

        return orm_filters
