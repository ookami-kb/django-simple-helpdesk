from rest_framework.test import APIClient, force_authenticate, APITestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from helpdesk.models import Ticket, State, AttachmentFile
import tempfile


class FileUploadTests(APITestCase):

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
            customer = 'email@test.test',
            message_id = '1',
        )

    def _create_test_file(self, path):
        f = open(path, 'w')
        f.write('test123\n')
        f.close()
        f = open(path, 'rb')
        return f
    '''
    def test_upload_file(self):
        #url = reverse('helpdesk__api__ticket_comments')
        url = 'http://127.0.0.1:8000/helpdesk/api/tickets/1/comments.json' 
        temp_file = tempfile.NamedTemporaryFile()
        temp_file_2 = tempfile.NamedTemporaryFile()
        data = {
            'attachments': [{self._create_test_file('/tmp/test_upload')},],
            'attachments': [temp_file, temp_file_2],
            'internal': 'true',
            'body': 'test comment'
        }

        client = APIClient()
        client.login(username='test', password='test')
        response = client.post(url, data, format='multipart')
        #print(response.data)
    '''



    def test_comment_creation(self):

        url = 'http://127.0.0.1:8000/helpdesk/api/tickets/1/comments.json?attachments_ids=(1,2)' 
        data = {
            'internal': 'true',
            'body': 'test comment'
        }

        #temp_file = tempfile.NamedTemporaryFile()
        #f = AttachmentFile.objects.create(attachment_file=temp_file, id=1)


        client = APIClient()
        client.login(username='test', password='test')
        response = client.post(url, data, format='multipart')

        print(response.data)