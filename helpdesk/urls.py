from django.conf.urls import url
from django.contrib.auth.decorators import permission_required, login_required

from helpdesk.views import HomeView, TicketView, EmailView, CommentEmailView, TicketCreateView, AttachmentView

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
    url(r'^attachments/(?P<signature>[A-z0-9:-]+)/', AttachmentView.as_view(), name='helpdesk_attachment')
]
