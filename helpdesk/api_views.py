from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination

from helpdesk.models import Ticket, State, Assignee, Comment, MailAttachment, AttachmentFile
from helpdesk.serializers import TicketListSerializer, StateSerializer,\
    AssigneeSerializer, TicketDetailSerializer, CommentSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from ast import literal_eval
from django.contrib.contenttypes.models import ContentType



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

    def get_queryset(self):
        ticket_pk = self.kwargs['pk']
        ticket_obj = get_object_or_404(Ticket, pk=ticket_pk)
        return Comment.objects.filter(ticket=ticket_obj)


    def post(self, request, *args, **kwargs):

        # Get ticket object
        ticket_pk = self.kwargs['pk']
        ticket_obj = get_object_or_404(Ticket, pk=ticket_pk)

        # Create comment
        comment = Comment.objects.create(
            ticket = ticket_obj,
            body = request.data.get('body'),
            author = request.user,
            internal = request.data.get('internal'),
        )

        # Handle attachments
        attachments_ids = request.query_params.get('attachments_ids', None)        
        if attachments_ids:
            comment_content_type = ContentType.objects.get(app_label='helpdesk', model='comment')
            ids = literal_eval(attachments_ids)
            print(ids, type(ids))
            for attachment_id in ids:
                try:
                    attachment_file = AttachmentFile.objects.get(pk=attachment_id)
                    attachment_obj = MailAttachment.objects.create(
                        content_type = comment_content_type,
                        object_id = comment.id,
                        attachment = attachment_file
                    )
                    attachment_obj.save()
                
                except AttachmentFile.DoesNotExist:
                    pass

        serializer = self.get_serializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)