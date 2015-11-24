from django.conf.urls import url, include
from django.contrib.auth.decorators import permission_required, login_required
from tastypie.api import Api

from helpdesk.api import TicketResource, StateResource, AssigneeResource, ProjectResource, CommentResource
from helpdesk.views import HomeView, TicketView, EmailView, CommentEmailView, TicketCreateView, AttachmentView, \
    ComponentView

v1_api = Api(api_name='v1')
v1_api.register(StateResource())
v1_api.register(AssigneeResource())
v1_api.register(TicketResource())
v1_api.register(ProjectResource())
v1_api.register(CommentResource())

urlpatterns = [
    url(r'^$', permission_required('helpdesk.view_tickets')(HomeView.as_view()), name='helpdesk_home'),
    url(r'^tickets/(?P<pk>\d+)/$', permission_required('helpdesk.view_tickets')(TicketView.as_view()),
        name='helpdesk_ticket'),
    url(r'^tickets/create/$', permission_required('helpdesk.add_ticket')(TicketCreateView.as_view()),
        name='helpdesk_ticket_create'),
    url(r'^tickets/(?P<pk>\d+)/email/$', permission_required('helpdesk.view_tickets')(EmailView.as_view()),
        name='helpdesk_email'),
    url(r'^comments/(?P<pk>\d+)/email/$', permission_required('helpdesk.view_tickets')(CommentEmailView.as_view()),
        name='helpdesk_comment_email'),
    url(r'^attachments/(?P<name>.+)', login_required(AttachmentView.as_view()), name='helpdesk_attachment'),

    url(r'^components/(?P<component>[a-z-]+).html', ComponentView.as_view(), name='helpdesk_component'),

    url(r'^api/', include(v1_api.urls)),
]
