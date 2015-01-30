from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from helpdesk.views import HomeView, TicketView, EmailView, CommentEmailView


urlpatterns = patterns(
    '',
    url(r'^$', permission_required('helpdesk.view_tickets')(HomeView.as_view()), name='home'),
    url(r'^tickets/(?P<pk>\d+)/$', permission_required('helpdesk.view_tickets')(TicketView.as_view()), name='ticket'),
    url(r'^tickets/(?P<pk>\d+)/email/$', permission_required('helpdesk.view_tickets')(EmailView.as_view()),
        name='email'),
    url(r'^comments/(?P<pk>\d+)/email/$', permission_required('helpdesk.view_tickets')(CommentEmailView.as_view()),
        name='comment_email'),
)