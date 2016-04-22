from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from helpdesk.api_views import TicketListView, StateListView, AssigneeListView, TicketView

urlpatterns = [
    url(r'^tickets\.json$', permission_required('helpdesk.view_tickets')(TicketListView.as_view()),
        name='helpdesk__api__ticket_list'),

    url(r'^tickets/(?P<pk>\d+)\.json$', permission_required('helpdesk.view_tickets')(TicketView.as_view()),
        name='helpdesk__api__ticket'),

    url(r'^states\.json$', permission_required('helpdesk.view_tickets')(StateListView.as_view()),
        name='helpdesk__api__state_list'),

    url(r'^assignees\.json$', permission_required('helpdesk.view_tickets')(AssigneeListView.as_view()),
        name='helpdesk__api__assignee_list'),
]
