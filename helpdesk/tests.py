from django.core.management import call_command
from django.test import TestCase
from helpdesk.models import Ticket, Comment, State


class WorkflowTest(TestCase):
    def test_open_state_on_comment(self):
        call_command('init_helpdesk')
        ticket = Ticket.objects.create(title=u'Test', body=u'Test', customer='test@example.com', message_id='test')
        self.assertEqual(ticket.state.machine_name, 'open', u'Ticket state must be "Open" after creation')

        ticket.state = State.objects.get(pk='resolved')
        ticket.save()

        Comment.objects.create(ticket=ticket, body='Another comment from client')
        ticket = Ticket.objects.get(pk=1)
        self.assertEqual(ticket.state.machine_name, 'open', u'Ticket state must be "Open" after comment from client')
