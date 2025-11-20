"""Contains filters for filtering messages"""

from django_filters import FilterSet

from .models import (
    Message,
    Conversation
)

class ConversationFilter(FilterSet):
    class Meta:
        model = Conversation
        fields = ['participants_id']

class MessageFilter(FilterSet):
    class Meta:
        model = Message
        fields = {
            'sent_at': ['date__range', 'time__range']
        }
