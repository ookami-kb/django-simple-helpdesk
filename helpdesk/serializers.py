from rest_framework import serializers

from helpdesk.models import Ticket, State, Assignee, Comment, MailAttachment, AttachmentFile
from django.contrib.contenttypes.models import ContentType


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


class AttachmentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentFile
        fields = ('file_id', 'filename', 'signed_url')


class AttachmentSerializer(serializers.ModelSerializer):
    """Mail attachments serializer class"""
    attachment = AttachmentFileSerializer()
    class Meta:
        model = MailAttachment
        fields = ('id', 'attachment')


class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer"""
    author = AssigneeSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachments_ids = serializers.ListField(
        write_only=True,
        required=False,
        child=serializers.UUIDField(required=False),
    )
    
    class Meta:
        model = Comment
        read_only_fields = ('created', 'author', 'notified', 'ticket', 'attachments')
    
    def create(self, validated_data, **kwargs):
        """Create Comment"""
        ids = validated_data.pop('attachments_ids')
        # Create comment
        comment = Comment(**validated_data)
        comment.author = self.context['request'].user
        comment.ticket = self.context['ticket']
        comment.save()

        # Handle file attachments
        if ids:
            comment_ct = ContentType.objects.get(app_label='helpdesk', model='comment')
            attachment_qs = AttachmentFile.objects.filter(file_id__in=ids).select_related()
            attachments_list = []
            for obj in attachment_qs:
                # Check if mail attachment with this file exists
                try:
                    ma = obj.mailattachment
                except MailAttachment.DoesNotExist:
                    attachment_obj = MailAttachment(
                        content_type = comment_ct,
                        object_id = comment.id,
                        attachment = obj
                    )
                    attachments_list.append(attachment_obj)

            MailAttachment.objects.bulk_create(attachments_list)

        return comment


class TicketDetailSerializer(TicketListSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = ('id', 'title', 'state', 'state_id',
                  'priority', 'customer', 'created', 'updated', 'project', 'project_title',
                  'customer_name', 'assignee', 'assignee_id', 'body', 'comments')
        read_only_fields = ('customer_name', 'customer', 'title', 'body')
