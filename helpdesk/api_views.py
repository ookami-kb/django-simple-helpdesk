from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination

from helpdesk.models import Ticket, State, Assignee, Comment, MailAttachment, AttachmentFile
from helpdesk.serializers import TicketListSerializer, StateSerializer,\
    AssigneeSerializer, TicketDetailSerializer, CommentSerializer, AttachmentFileSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from ast import literal_eval
from django.contrib.contenttypes.models import ContentType
from rest_framework.parsers import FormParser, MultiPartParser


class Pagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'limit'


class TicketListView(ListAPIView):
    serializer_class = TicketListSerializer
    pagination_class = Pagination

    def get_queryset(self):
        filters = {}
        state = self.request.query_params.get('state', '')
        if state:
            filters['state'] = state

        if not self.request.user.has_perm('helpdesk.view_all_tickets'):
            filters['assignee'] = self.request.user
        else:
            assignee = self.request.query_params.get('assignee', '')
            if assignee == 'me':
                filters['assignee'] = self.request.user
            elif assignee:
                filters['assignee__pk'] = int(assignee)

        search = self.request.query_params.get('search', '')
        qs = Q()
        if search:
            qs |= Q(title__icontains=search) | Q(body__icontains=search)
            if self.request.user.has_perm('helpdesk.view_all_tickets'):
                qs |= Q(customer__icontains=search)
        return Ticket.objects.filter(qs, **filters)


class TicketView(RetrieveUpdateAPIView):
    serializer_class = TicketDetailSerializer

    def get_queryset(self):
        filters = {}
        if not self.request.user.has_perm('helpdesk.view_all_tickets'):
            filters['assignee'] = self.request.user

        return Ticket.objects.filter(**filters)

        # def post(self, request, *args, **kwargs):
        #     ticket = self.get_object()
        #     data = request.data
        #     serializer = CommentSerializer(data=data)
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save(author=request.user, ticket=ticket)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)


class StateListView(ListAPIView):
    serializer_class = StateSerializer
    queryset = State.objects.all()


class AssigneeListView(ListAPIView):
    serializer_class = AssigneeSerializer
    queryset = Assignee.objects.all()


class CommentListView(ListCreateAPIView):
    serializer_class = CommentSerializer

    def _get_ticket_object(self):
        return get_object_or_404(Ticket, pk=self.kwargs['pk'])        

    def _create_attachment(self, comment_id, attachment_file_id):
        """Return instance of MailAttachment class"""
        comment_ct = ContentType.objects.get(
            app_label='helpdesk', 
            model='comment'
        )
        try:
            attachment_file = AttachmentFile.objects.get(pk=attachment_file_id)
            attachment_obj = MailAttachment(
                content_type = comment_ct,
                object_id = comment_id,
                attachment = attachment_file
            )
        except AttachmentFile.DoesNotExist:
            attachment_obj = None

        return attachment_obj


    def get_queryset(self):
        return Comment.objects.filter(ticket=self._get_ticket_object())


    def post(self, request, *args, **kwargs):

        # Get ticket object
        ticket_obj = self._get_ticket_object()

        # Create comment
        comment = Comment.objects.create(
            ticket = ticket_obj,
            body = request.data.get('body'),
            author = request.user,
            internal = request.data.get('internal'),
        )
        # Handle attachments
        attachments_ids = request.data.get('attachments_ids', None)        
        if attachments_ids:
            # Parse attachments_ids string using ast.literal_eval()

            # https://docs.python.org/3/library/ast.html#ast.literal_eval

            # Safely evaluate an expression node or a string containing a 
            # Python literal or container display. The string or node provided 
            # may only consist of the following Python literal structures: 
            # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None.

            try:
                ids = literal_eval(attachments_ids)
            except:
                ids = None

            if ids:
                comment_ct = ContentType.objects.get(
                    app_label='helpdesk', 
                    model='comment'
                )
                # Check if ids is int or sequence type
                if isinstance(ids, int):
                    attachment_obj = self._create_attachment(comment.id, ids)
                    if attachment_obj:
                        attachment_obj.save()

                elif type(ids) in (list, tuple, set):
                    attachments_list = []
                    for attachment_id in ids:
                        attachment_obj = self._create_attachment(comment.id, attachment_id)
                        if attachment_obj:
                            attachments_list.append(attachment_obj)
                    MailAttachment.objects.bulk_create(attachments_list)
                else:
                    pass

        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AttachmentFileUploadView(CreateAPIView):
    """Attachment file upload"""
    serializer_class = AttachmentFileSerializer
    parser_classes = (FormParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save(attachment_file=self.request.data.get('attachment_file'))