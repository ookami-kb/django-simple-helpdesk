from rest_framework.test import APIClient, force_authenticate, APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from helpdesk.models import Ticket, State, AttachmentFile
from rest_framework import status
import tempfile


class APITests(APITestCase):

    def setUp(self):
        u = User.objects.create_superuser('test', password='test', email='test@test.test')
        state = State.objects.create(machine_name = 'test', title = 'Test')
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
        # Create test files
        temp_file_1 = tempfile.NamedTemporaryFile()
        temp_file_2 = tempfile.NamedTemporaryFile()
        temp_file_3 = tempfile.NamedTemporaryFile()

        # Upload test files
        response = client.post(url, {'attachment_file': temp_file_1,}, format='multipart')
        # Check if created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Remember uploaded files names
        uploaded_file_1 = response.data['filename']
        file_id_1 = response.data['file_id']

        
        # And same for other files
        response = client.post(url, {'attachment_file': temp_file_2,}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        uploaded_file_2 = response.data['filename']
        file_id_2 = response.data['file_id']

        response = client.post(url, {'attachment_file': temp_file_3,}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        uploaded_file_3 = response.data['filename']
        file_id_3 = response.data['file_id']

        # Post first comment with attachment
        url = '/helpdesk/api/tickets/1/comments.json' 
        data = {
            'internal': 'true',
            'body': 'test comment',
            'attachments_ids': [file_id_1] # Attach one file
        }
        # Post comment
        response = client.post(url, data, format='multipart')
        # Check if created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Get comment's attachment filename
        #if response.data['attachments']:
        comment_attachment_filename = response.data['attachments'][0]['attachment']['filename']
        # Check if it's the same file
        self.assertEqual(uploaded_file_1, comment_attachment_filename)

        # Send request with the same file to be sure that
        # app don't crash
        response = client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Send empty list        
        data['attachments_ids'] = []
        response = client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Send data without 'attacments_ids' key  
        data.pop('attachments_ids', None)
        response = client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Next, let's create another comment with 2 files attached
        # We'll use same data, only different attachments
        data['attachments_ids'] = [file_id_2, file_id_3]
        response = client.post(url, data, format='multipart')
        # Check if created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if 2 attachments in response
        self.assertEqual(len(response.data['attachments']), 2)

        # Get comment's attachments filenames
        comment_attachment_filename = response.data['attachments'][0]['attachment']['filename']
        self.assertEqual(uploaded_file_2, comment_attachment_filename)

        comment_attachment_filename = response.data['attachments'][1]['attachment']['filename']
        self.assertEqual(uploaded_file_3, comment_attachment_filename)