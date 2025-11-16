from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.authentication import TokenAuthentication, SessionAuth

from django.shortcuts import (
    get_object_or_404, get_list_or_404
)

from django.db.models import Q, Count, Max, Prefetch

from django.db import transaction

from models import User, Conversation, Message
    
from serializers import UserSerializer, ConversationSerializer, MessageSerializer

from rest_framework.pagination import PageNumberPagination

from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

# Exceptions
from rest_framework.exceptions import (
    PermissionDenied,
    ValidationError,
    NotFound,
)

from django.utils import timezone

from django.http import Http404

import logging

import time

logger = logging.getLogger(__name__)



class StandardResultsSetPagination(PageNumberPagination):
    """
    Setting up custom pagination for consistent API responses
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserRegistrationView(APIView):
    """
    Handle user registration
    POST /api/users/register/
    """
    permission_classes = [IsAuthenticated]
    
    def post(request):
        """
        Register a new user
        
        Request body:
        {
            "email": "user@example.com",
            "password": "SecurePass123",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "role": "guest"
        }
        """
        
        serializer = UserSerializer(data=request.data)#validating incoming data
        
        if serializer.is_valid():
            # STEP 2: Save user (calls serializer.create())
            user = serializer.save()
            
            # STEP 3: Return success response with user data
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            # STEP 4: Return validation errors
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )



class UserListView(generics.ListAPIView):
    """
    List all users with pagination and search
    GET /api/users/
    
    Query params:
    - page: page number
    - page_size: results per page
    - search: search by email or name
    - role: filter by role
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['first_name', 'last_name']
    ordering = ['first_name']  # Default ordering
    
    def get_queryset():
        """
        Get filtered list of users
        """
        queryset = User.objects.all()
        
        # FILTER: By role if provided
        role = request.query_params.get('role', None)
        if role is not None:
            queryset = queryset.filter(role=role)
        
        # EXCLUDE: Current user from results (optional)
        if request.user.is_authenticated:
            queryset = queryset.exclude(user_id=request.user.user_id)
        
        return queryset



class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a user
    GET /api/users/{user_id}/
    PUT /api/users/{user_id}/
    PATCH /api/users/{user_id}/
    DELETE /api/users/{user_id}/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'user_id'
    
    def get_queryset():
        """
        Users can only access their own profile or admins can access all
        """
        if request.user.role == 'admin':
            return  User.objects.all()
        else:
            return User.objects.filter(user_id=request.user.user_id)
    
    def perform_update(serializer):
        """
        Override to add custom logic before saving
        """
        if serializer.instance.user_id != request.user.user_id:
            # prevents anyone other than the admin from changing a different 
            # profile that is no theirs
            if request.user.role != 'admin':
                raise PermissionDenied("You can only update your own profile")
        
        serializer.save()
    
    def perform_destroy(instance):
        """
        Override to add custom logic before deletion
        """
        # Prevent users from deleting themselves unless admin
        if instance.user_id == request.user.user_id:
            if request.user.role != 'admin':
                raise PermissionDenied("You cannot delete your own account")
        
        instance.delete()


class CurrentUserView(APIView):
    """
    Get current authenticated user's profile
    GET /api/users/me/
    """
    permission_classes = [IsAuthenticated]
    
    def get(request):
        """
        Return current user's data
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)



class ConversationListCreateView(APIView):
    """
    List user's conversations and create new conversations
    GET /api/conversations/
    POST /api/conversations/
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(request):
        """
        Get all conversations for current user
        
        Returns conversations ordered by most recent message
        """
        # Obtaining all conversations with the user_id of current user
        conversations = Conversation.objects.filter(
            participants=request.user
        ).order_by('-created_at')
        
        # STEP 2: Annotate with latest message info (optional)
        for conversation in conversations:
            latest_message = conversation.messages.last()
            if latest_message:
                conversation.append(latest_message)
                conversation.append(latest_message.time)
        
        # Manual pagination since the APIView we are inheriting 
        # requires manual pagination
        paginator = StandardResultsSetPagination()
        paginated_conversations = paginator.paginate_queryset(
            conversations, 
            request
        )
        
        serializer = ConversationSerializer(
            paginated_conversations, 
            many=True, 
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(request):
        """
        Create new conversation
        
        Request body:
        {
            "participant_ids": ["uuid1", "uuid2", "uuid3"]
        }
        """
        participant_ids = request.data.get('participant_ids', [])
        
        if len(participant_ids) < 1:
            return Response(
                {"error": "At least one other participant required"},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        # STEP 3: Add current user to participants
        participant_ids.append(request.user.user_id)
        participant_ids = list(set(participant_ids))
        
        # STEP 4: Validate all participants exist
        participants = User.objects.filter(user_id__in=participant_ids)
        
        if participants.count() != len(participant_ids):
            return Response(
                {"error": "One or more participants not found"},
                status = status.HTTP_404_NOT_FOUND
            )
        
        # STEP 5: Check if conversation already exists with same participants
        # (Optional: prevent duplicate conversations)
        existing_conversation = Conversation.objects.filter(
            participants_id = participant_ids
        )
        
        if existing_conversation:
            serializer = ConversationSerializer(existing_conversation)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        
        # STEP 6: Create new conversation in atomic transaction
        with transaction.atomic():
            conversation = Conversation.objects.create()
            conversation.participants.add(*participants)
            conversation.save()
        
        # STEP 7: Serialize and return created conversation
        serializer = ConversationSerializer(conversation)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class ConversationDetailView(APIView):
    """
    Retrieve, update, or delete a specific conversation
    GET /api/conversations/{conversation_id}/
    PATCH /api/conversations/{conversation_id}/
    DELETE /api/conversations/{conversation_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get_conversation(conversation_id):
        """
        Helper method to get conversation and verify permissions
        """
        # Get conversation or return 404
        conversation = get_object_or_404(
            Conversation,
            conversation_id=conversation_id
        )
        
        # Verify user is a participant
        if request.user not in conversation.participants.all():
            raise PermissionDenied(
                "You are not a participant in this conversation"
            )
        
        return conversation
    
    def get(self, request, conversation_id):
        """
        Get conversation details with messages
        """
        # STEP 1: Get and verify conversation
        conversation = self.get_conversation(conversation_id)
        
        # STEP 2: Serialize conversation
        serializer = ConversationSerializer(
            conversation,
            context={'request': request}
        )
        
        return Response(serializer.data)
    
    def patch(self, request, conversation_id):
        """
        Update conversation (add/remove participants)
        
        Request body:
        {
            "add_participants": ["uuid1", "uuid2"],
            "remove_participants": ["uuid3"]
        }
        """
        # STEP 1: Get and verify conversation
        conversation = self.get_conversation(conversation_id)
        
        # STEP 2: Add new participants
        add_participant_ids = request.data.get('add_participants', [])
        if add_participant_ids:
            users_to_add = User.objects.filter(
                user_id__in=add_participant_ids
            )
            conversation.participants.add(*users_to_add)
        
        # STEP 3: Remove participants
        remove_participant_ids = request.data.get('remove_participants', [])
        if remove_participant_ids:
            # Don't allow removing yourself
            if request.user.user_id in remove_participant_ids:
                return Response(
                    {"error": "Cannot remove yourself from conversation"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            users_to_remove = User.objects.filter(
                user_id__in=remove_participant_ids
            )
            conversation.participants.remove(*users_to_remove)
        
        # STEP 4: Ensure at least 2 participants remain
        if conversation.get_participant_count() < 2:
            return Response(
                {"error": "Conversation must have at least 2 participants"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # STEP 5: Return updated conversation
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)
    
    def delete(self, request, conversation_id):
        """
        Delete conversation (or leave conversation)
        """
        # STEP 1: Get and verify conversation
        conversation = self.get_conversation(conversation_id)
        
        # STEP 2: Option A: Remove user from conversation (leave)
        conversation.participants.remove(request.user)
        
        # STEP 3: If no participants left, delete conversation
        if conversation.get_participant_count() == 0:
            conversation.delete()
            return Response(
                {"message": "Conversation deleted"},
                status=status.HTTP_204_NO_CONTENT
            )
        
        # STEP 4: Return success
        return Response(
            {"message": "Left conversation"},
            status=status.HTTP_200_OK
        )


class MessageListCreateView(APIView):
    """
    List messages in a conversation and send new messages
    GET /api/conversations/{conversation_id}/messages/
    POST /api/conversations/{conversation_id}/messages/
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(request, conversation_id):
        """
        Get all messages in a conversation with pagination
        
        Query params:
        - page: page number
        - page_size: messages per page
        - before: get messages before specific timestamp
        - after: get messages after specific timestamp
        """
        # STEP 1: Get and verify conversation
        conversation = get_object_or_404(
            Conversation,
            conversation_id=conversation_id
        )
        
        # STEP 2: Verify user is participant
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "Not authorized to view this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # STEP 3: Get messages for this conversation
        messages = Message.objects.filter(
            conversation=conversation
        ).order_by('sent_at')
        
        # STEP 4: Apply time filters if provided
        before = request.query_params.get('before', None)
        if before:
            messages = messages.filter(sent_at__lt=before)
        
        after = request.query_params.get('after', None)
        if after:
            messages = messages.filter(sent_at__gt=after)
        
        # STEP 5: Paginate
        paginator = StandardResultsSetPagination()
        paginated_messages = paginator.paginate_queryset(
            messages,
            request
        )
        
        # STEP 6: Serialize and return
        serializer = MessageSerializer(
            paginated_messages,
            many=True,
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(request, conversation_id):
        """
        Send a new message in conversation
        
        Request body:
        {
            "message_body": "Hello, how are you?"
        }
        """
        # STEP 1: Get and verify conversation
        conversation = get_object_or_404(
            Conversation,
            conversation_id=conversation_id
        )
        
        # STEP 2: Verify user is participant
        if request.user not in conversation.participants.all():
            return Response(
                {"error": "Not authorized to send messages in this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # STEP 3: Extract message body
        message_body = request.data.get('message_body', '').strip()
        
        # STEP 4: Validate message body
        if not message_body:
            return Response(
                {"error": "Message body cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(message_body) > 5000:
            return Response(
                {"error": "Message too long (max 5000 characters)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # STEP 5: Create message
        with transaction.atomic():
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                message_body=message_body
            )
        
        
        
        # STEP 7: Serialize and return
        serializer = MessageSerializer(message)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class MessageDetailView(APIView):
    """
    Retrieve, update, or delete a specific message
    GET /api/messages/{message_id}/
    PATCH /api/messages/{message_id}/
    DELETE /api/messages/{message_id}/
    """
    permission_classes = [IsAuthenticated]
    
    def get_message(message_id):
        """
        Helper to get message and verify permissions
        """
        message = get_object_or_404(Message, message_id=message_id)
        
        # Verify user is participant in conversation
        if request.user not in message.conversation.participants.all():
            raise PermissionDenied("Not authorized to access this message")
        
        return message
    
    def get(self, request, message_id):
        """
        Get message details
        """
        message = self.get_message(message_id)
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    def patch(self, request, message_id):
        """
        Edit message (only by sender, within time limit)
        
        Request body:
        {
            "message_body": "Updated message text"
        }
        """
        # STEP 1: Get message
        message = self.get_message(message_id)
        
        # STEP 2: Verify sender
        if message.sender != request.user:
            return Response(
                {"error": "You can only edit your own messages"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        
        # STEP 4: Update message
        new_body = request.data.get('message_body', '').strip()
        if not new_body:
            return Response(
                {"error": "Message body cannot be empty"},
                status=HTTP_400_BAD_REQUEST
            )
        
        message.message_body = new_body
        message.save()
        
        # STEP 5: Return updated message
        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
    def delete(self, request, message_id):
        """
        Delete message (only by sender)
        """
        # STEP 1: Get message
        message = self.get_message(message_id)
        
        # STEP 2: Verify sender
        if message.sender != request.user:
            return Response(
                {"error": "You can only delete your own messages"},
                status=HTTP_403_FORBIDDEN
            )
        
        # STEP 3: Delete message
        message.delete()
        
        return Response(
            {"message": "Message deleted"},
            status=HTTP_204_NO_CONTENT
        )


class SearchMessagesView(APIView):
    """
    Search messages across all user's conversations
    GET /api/messages/search/?q=search_term
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get(request):
        """
        Search messages by content
        """
        # STEP 1: Get search query
        search_query = request.query_params.get('q', '').strip()
        
        if not search_query:
            return Response(
                {"error": "Search query required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # STEP 2: Get user's conversations
        user_conversations = request.user.conversations.all()
        
        # STEP 3: Search messages in those conversations
        messages = Message.objects.filter(
            conversation__in=user_conversations,
            message_body__icontains=search_query
        ).order_by('-sent_at')
        
        # STEP 4: Paginate results
        paginator = StandardResultsSetPagination()
        paginated_messages = paginator.paginate_queryset(
            messages,
            request
        )
        
        # STEP 5: Serialize and return
        serializer = MessageSerializer(
            paginated_messages,
            many=True
        )
        
        return paginator.get_paginated_response(serializer.data)



# ============================================================================
# URL PATTERNS (for reference)
# ============================================================================
"""
urls.py should include:

# User endpoints
/api/users/register/                    → UserRegistrationView
/api/users/                             → UserListView
/api/users/me/                          → CurrentUserView
/api/users/{user_id}/                   → UserDetailView

# Conversation endpoints
/api/conversations/                     → ConversationListCreateView
/api/conversations/{conversation_id}/   → ConversationDetailView
/api/conversations/{conversation_id}/stats/ → ConversationStatsView

# Message endpoints
/api/conversations/{conversation_id}/messages/ → MessageListCreateView
/api/messages/{message_id}/             → MessageDetailView
/api/messages/search/                   → SearchMessagesView
"""


# ============================================================================
# ADDITIONAL CONSIDERATIONS FOR IMPLEMENTATION
# ============================================================================
"""
1. AUTHENTICATION:
   - Use TokenAuthentication or JWT
   - Implement login/logout endpoints
   - Add refresh token mechanism

2. PERMISSIONS:
   - Create custom permission classes
   - IsParticipant permission for conversations
   - IsMessageSender permission for editing/deleting

3. REAL-TIME FEATURES:
   - WebSocket integration for live messaging
   - Django Channels for WebSocket support
   - Notification system for new messages

4. OPTIMIZATIONS:
   - Use select_related() and prefetch_related() for queries
   - Add database indexes
   - Implement caching (Redis)

5. SECURITY:
   - Rate limiting on endpoints
   - Input sanitization
   - CORS configuration
   - File upload validation (for media messages)

6. TESTING:
   - Unit tests for each view
   - Integration tests for workflows
   - Load testing for scalability

7. DOCUMENTATION:
   - Swagger/OpenAPI docs
   - Postman collection
   - README with API examples
"""