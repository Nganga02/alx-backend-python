from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Setting up custom pagination for consistent API responses
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    """
    List all conversations for the current user.
    Create a new conversation with participants.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get all conversations for current user
        
        Returns conversations ordered by most recent message
        """
        conversations = Conversation.objects.filter(participants=self.request.user.user_id)
        paginator = StandardResultsSetPagination()
        paginated_conversations = paginator.paginate_queryset(
            conversations, 
            self.request
        )

        serializer = ConversationSerializer(
            paginated_conversations, 
            many=True, 
            context={'request': self.request}
        )

        return paginator.get_paginated_response(serializer.data) 

    def perform_create(self, serializer):
        """
        Create new conversation
        
        Request body:
        {
            "participant_ids": ["uuid1", "uuid2", "uuid3"]
        }
        """
        conversation = serializer.save()
        # Ensure current user is in participants
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in this conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    List messages in a conversation.
    Send a new message to a conversation.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        messages = Message.objects.filter(
            conversation_id = conversation_id
        ).order_by('sent_at')
        
        
        paginator = StandardResultsSetPagination()
        paginated_messages = paginator.paginate_queryset(
            messages,
            self.request
        )
        
        # STEP 6: Serialize and return
        serializer = MessageSerializer(
            paginated_messages,
            many=True,
            context={'request': self.request}
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    def perform_create(self, serializer):
        conversation = get_object_or_404(
            Conversation,
            id=self.kwargs['conversation_id'],
            participants=self.request.user
        )
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )
        # Update conversation timestamp
        conversation.save(update_fields=['updated_at'])
