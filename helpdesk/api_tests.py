from rest_framework.test import APIClient, force_authenticate, APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from helpdesk.models import Ticket, State, AttachmentFile
from rest_framework import status
import tempfile


class APITests(APITestCase):

    def setUp(self):
        u = User.objects.create_superuser('test', password='test',
                                     email='test@test.test')
        u.save()

        state = State.objects.create(
            machine_name = 'test',
            title = 'Test'
        )

        ticket = Ticket.objects.create(
            pk = 1,
            title = 'test',
            body = 'test',
            state = state,
            customer = 'test@test.test',
            message_id = '1',
        )

    def test_comment_post(self):
        """Comment posting test"""
        
        # Login
        client = APIClient()
        client.login(username='test', password='test')


        # Upload new attachment file
        url = reverse('helpdesk__api__attachment_file_upload')
        temp_file = tempfile.NamedTemporaryFile()
        data = {'attachment_file': temp_file,}
        response = client.post(url, data, format='multipart')
        # Check if created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Remember uploaded file's name
        uploaded_file_name = response.data['filename']

        # Post comment
        # Values of 'attachments_ids' parameter are uploaded files id's
        url = 'http://127.0.0.1:8000/helpdesk/api/tickets/1/comments.json?attachments_ids=[1,2]' 
        data = {
            'internal': 'true',
            'body': 'test comment'
        }
        # Post comment
        response = client.post(url, data, format='multipart')
        # Check if created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Get comment's attachment filename
        comment_attachment_filename = response.data['attachments'][0]['attachment']['filename']
        # Check if it's the same file
        self.assertEqual(uploaded_file_name, comment_attachment_filename)
