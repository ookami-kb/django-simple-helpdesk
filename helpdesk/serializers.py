from rest_framework import serializers

from helpdesk.models import Ticket, State, Assignee, Comment


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('machine_name', 'title', 'resolved')


class AssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignee
        fields = ('id', 'first_name', 'last_name', 'tickets_count', 'full_name')


class TicketListSerializer(serializers.ModelSerializer):
    state = StateSerializer()
    assignee = AssigneeSerializer()

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'state', 'priority', 'customer', 'created', 'updated', 'project_title',
                  'customer_name', 'assignee')


class CommentSerializer(serializers.ModelSerializer):
    author = AssigneeSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'created', 'body', 'author', 'internal', 'notified')
        read_only_fields = ('created', 'author', 'notified')


class TicketDetailSerializer(TicketListSerializer):
    comments = CommentSerializer(many=True)

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'state', 'priority', 'customer', 'created', 'updated', 'project_title',
                  'customer_name', 'assignee', 'body', 'comments')
