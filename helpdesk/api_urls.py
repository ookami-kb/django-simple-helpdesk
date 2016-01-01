from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from helpdesk.api_views import TicketListView

urlpatterns = [
    url(r'^tickets/$', permission_required('helpdesk.view_tickets')(TicketListView.as_view()),
        name='helpdesk__api__ticket_list')
]
