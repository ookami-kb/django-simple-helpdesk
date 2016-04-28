from rest_framework import serializers
from helpdesk.models import Ticket, State, Assignee, Comment


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('machine_name', 'title', 'resolved')

        extra_kwargs = {
            'machine_name': {
                'validators': [],
                'read_only': False,
            }
        }


class AssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignee
        fields = ('id', 'first_name', 'last_name', 'tickets_count', 'full_name')
        extra_kwargs = {
            'id': {
                'read_only': False,
            }
        }


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
        fields = ('id', 'title', 'state', 'priority', 'customer', 'created', 'updated', 'project', 'project_title',
                  'customer_name', 'assignee', 'body', 'comments')
    
    
    def validate(self, data):
        """Validate data"""
        if self.context['request'].method == 'PATCH':    
            allowed = ('state', 'project', 'assignee', 'priority')
            for item in data:
                if not item in allowed:
                    raise serializers.ValidationError('You can update only "state", ' \
                                                       '"project", "assignee" and "priority" fields')
        return data
    

    def update(self, instance, validated_data):
        """Override method to add writable nested serializers support"""
        state_data = validated_data.pop('state', None)
        assignee_data = validated_data.pop('assignee', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if state_data:
            try:
                instance.state = State.objects.get(machine_name=state_data['machine_name'])
            except State.DoesNotExist:
                pass

        if assignee_data:
            try:
                instance.assignee = Assignee.objects.get(id=assignee_data['id'])
            except Assignee.DoesNotExist:
                pass

        instance.save()
        return instance
