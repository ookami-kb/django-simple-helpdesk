from rest_framework.generics import ListAPIView

from helpdesk.models import Ticket
from helpdesk.serializers import TicketListSerializer


class TicketListView(ListAPIView):
    serializer_class = TicketListSerializer

    def get_queryset(self):
        return Ticket.objects.all()
