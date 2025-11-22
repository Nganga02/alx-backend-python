# views.py
from rest_framework import viewsets, status,filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationViewSet(viewsets.ModelViewSet):
    """
    List all conversations for the current user.
    Create a new conversation with participants.
    """

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__id']
    ordering_fields = ['updated_at', 'created_at']
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # Let DRF handle pagination

    def get_queryset(self):
        """
        Return conversations for current user, ordered by most recent message
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).order_by('-updated_at')

    def perform_create(self, serializer):
        conversation = serializer.save()
        # Ensure current user is in participants
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages in this conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('timestamp')
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    List messages in a conversation.
    Send a new message to a conversation.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('timestamp')  # or 'sent_at' if that's your field

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