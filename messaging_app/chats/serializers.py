from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Handles user creation, validation, and representation.
    """
    # Write-only field for password (won't be included in responses)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    
    # Read-only fields
    user_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    # Optional: Add a computed field
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'password',
            'created_at',
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def get_full_name(self, obj):
        """Method for computed field."""
        return f"{obj.first_name} {obj.last_name}"
    
    def create(self, validated_data):
        """Override create to handle password hashing"""
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    
    def update(self, user_instance, validated_data):
        """Override update to handle password hashing."""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(user_instance, attr, value)
        
        if password:
            user_instance.set_password(password)
        
        user_instance.save()
        return user_instance


class UserSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for User - used in nested relationships.
    Only includes essential fields.
    """
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name']
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model.
    """
    message_id = serializers.UUIDField(read_only=True)
    sent_at = serializers.DateTimeField(read_only=True)
    
    # Nested serializer - shows sender details
    sender = UserSummarySerializer(read_only=True)
    
    # Write-only field to accept sender_id during creation
    sender_id = serializers.UUIDField(write_only=True)
    
    # Optional: Add message preview
    preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation_id',
            'sender',
            'sender_id',
            'message_body',
            'preview',
            'sent_at',
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def get_preview(self, obj):
        """Return message preview (first 50 characters)."""
        return obj.get_preview(50)
    
    def validate_sender_id(self, value):
        """Validate that sender exists."""
        try:
            User.objects.get(user_id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Sender does not exist.")
        return value
    
    def validate_message_body(self, value):
        """Validate that message is not empty or just whitespace."""
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """Override create to handle sender_id."""
        sender_id = validated_data.pop('sender_id')
        sender = User.objects.get(user_id=sender_id)
        return Message.objects.create(sender=sender, **validated_data)
    
    def update(self, instance, validated_data):
    # Only update message_body if provided
        validated_data.pop('sender_id', None)
        message_body = validated_data.get('message_body', None)

        if message_body is not None:
            if message_body.strip() == "":
                raise serializers.ValidationError("Message cannot be empty.")
            instance.message_body = message_body

        instance.save()
        return instance

         



class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model.
    """
    conversation_id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    # Nested serializer for participants
    participants = UserSummarySerializer(many=True, read_only=True)
    
    # Write-only field to accept participant IDs during creation
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    
    # Include recent messages (optional)
    messages = MessageSerializer(many=True, read_only=True)
    
    # Computed fields
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'participant_count',
            'messages',
            'last_message',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_participant_count(self, obj):
        """Return number of participants."""
        return obj.participants.count()
    
    def get_last_message(self, obj):
        """Return the last message in conversation."""
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None
    
    def validate_participant_ids(self, value):
        """Validate that all participants exist and there are at least 2."""
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants."
            )
        
        # Check if all users exist
        existing_users = User.objects.filter(user_id__in=value)
        if existing_users.count() != len(value):
            raise serializers.ValidationError(
                "One or more participant IDs are invalid."
            )
        
        return value
    
    def create(self, validated_data):
        """Override create to handle many-to-many relationship."""
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.add(*participants)
        
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing conversations.
    Doesn't include all messages, just summary info.
    """
    conversation_id = serializers.UUIDField(read_only=True)
    participants = UserSummarySerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_count',
            'last_message',
            'unread_count',
            'created_at',
        ]
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-sent_at').first()
        if last_msg:
            return {
                'message_id': str(last_msg.message_id),
                'sender': last_msg.sender.email,
                'preview': last_msg.get_preview(30),
                'sent_at': last_msg.sent_at
            }
        return None
    
    def get_unread_count(self, obj):
        """Placeholder for unread message count."""
        # This would require additional model fields to track read status
        return 0
