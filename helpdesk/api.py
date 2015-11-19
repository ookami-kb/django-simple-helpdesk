from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource

from helpdesk.models import Ticket, State, Project


class StateResource(ModelResource):
    class Meta:
        queryset = State.objects.all()


class AssigneeResource(ModelResource):
    full_name = fields.CharField('get_full_name', default='Unknown')

    class Meta:
        queryset = User.objects.filter(groups__name='Helpdesk support')
        fields = ['id']


class ProjectResource(ModelResource):
    class Meta:
        queryset = Project.objects.all()
        fields = ['machine_name', 'title']


class TicketResource(ModelResource):
    state = fields.ForeignKey(StateResource, 'state', full=True)
    project = fields.ForeignKey(ProjectResource, 'project', full=True)
    assignee = fields.ForeignKey(AssigneeResource, 'assignee', full=True)

    class Meta:
        queryset = Ticket.objects.all()
        resource_name = 'ticket'
        ordering = ['priority', 'updated', 'title']

    def dehydrate_customer(self, bundle):
        if not bundle.request.user.has_perm('helpdesk.view_customer'):
            return None
        return bundle.obj.customer

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super().build_filters(filters)

        if 'filter_state' in filters:
            orm_filters['state__machine_name'] = filters['filter_state']
        if 'filter_project' in filters:
            orm_filters['project__machine_name'] = filters['filter_project']
        if 'filter_assignee' in filters:
            orm_filters['assignee__id'] = filters['filter__assignee']

        return orm_filters
