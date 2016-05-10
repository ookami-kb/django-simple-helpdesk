from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination

from helpdesk.models import Ticket, State, Assignee, Comment, MailAttachment, AttachmentFile
from helpdesk.serializers import TicketListSerializer, StateSerializer,\
    AssigneeSerializer, TicketDetailSerializer, CommentSerializer, AttachmentFileSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
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

    def get_queryset(self):
        return Comment.objects.filter(ticket=self._get_ticket_object())

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request, # request object is passed here
            'ticket': self._get_ticket_object(),
            'view': self
        }


class AttachmentFileUploadView(CreateAPIView):
    """Attachment file upload"""
    serializer_class = AttachmentFileSerializer
    parser_classes = (FormParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save(attachment_file=self.request.data.get('attachment_file'))