from rest_framework import serializers

from helpdesk.models import Ticket, State, Assignee, Comment, MailAttachment


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('machine_name', 'title', 'resolved')


class AssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignee
        fields = ('id', 'first_name', 'last_name', 'tickets_count', 'full_name')


class TicketListSerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)
    state_id = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    assignee = AssigneeSerializer(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(queryset=Assignee.objects.all())

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'state', 'state_id', 'priority', 'customer', 'created', 'updated', 'project_title',
                  'customer_name', 'assignee', 'assignee_id')


class AttachmentSerializer(serializers.ModelSerializer):
    """Mail attachments serializer class"""
    class Meta:
        model = MailAttachment
        fields = ('attachment', 'filename', 'signed_url')


'''
class AttachmentRelatedField(serializers.RelatedField):
    """Attachment related field"""
    queryset=MailAttachment.objects.all()

    def to_representation(self, value):
        serializer = AttachmentSerializer(value)
        return serializer.data
'''

class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer"""
    author = AssigneeSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True)
    #attachments = AttachmentRelatedField(many=True)

    class Meta:
        model = Comment
        #fields = (
        #    'id', 'message_id', 'created', 'body', 'author', 
        #    'internal', 'notified', 'attachments',
        #)
        read_only_fields = ('created', 'author', 'notified', 'ticket')


class TicketDetailSerializer(TicketListSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'state', 'state_id',
                  'priority', 'customer', 'created', 'updated', 'project', 'project_title',
                  'customer_name', 'assignee', 'assignee_id', 'body', 'comments')
        read_only_fields = ('customer_name', 'customer', 'title', 'body')
