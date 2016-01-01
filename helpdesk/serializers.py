from rest_framework import serializers

from helpdesk.models import Ticket, State


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('machine_name', 'title', 'resolved')


class TicketListSerializer(serializers.ModelSerializer):
    state = StateSerializer()

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'state', 'priority', 'customer', 'created', 'updated', 'project_title',
                  'customer_name')
