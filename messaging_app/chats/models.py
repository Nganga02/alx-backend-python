# Create your models here.
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses UUID as primary key and adds role and phone_number fields.
    """
    
    # Role choices as ENUM
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Override default id with UUID
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # Additional fields (first_name, last_name, email, password already in AbstractUser)

    # Making sure this is not null
    first_name = models.CharField(
        blank=False
    )

    # Making sure this field is not null
    last_name = models.CharField(
        blank=False
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False,
        db_index=True  # Index on email as per specification
    )
    
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        null=True,
        blank=True
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='guest',
        null=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Override username requirement (use email instead)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class Conversation(models.Model):
    """
    Conversation model to track participants in a conversation.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    participants_id = models.ManyToManyField(
        User,
        related_name='conversations',
        blank=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        participant_emails = ', '.join(
            [user.email for user in self.participants.all()[:3]]
        )
        return f"Conversation {self.conversation_id} - {participant_emails}"
    
    def get_participant_count(self):
        """Return the number of participants in this conversation."""
        return self.participants.count()


class Message(models.Model):
    """
    Message model containing sender, conversation, and message content.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=False
    )
    
    sender_id = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=False,
        db_column='sender_id'  # Match database specification
    )
    
    message_body = models.TextField(
        null=False,
        blank=False
    )
    
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['sent_at']
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender_id']),
        ]
        constraints = [
            # Ensure message_body is not empty
            models.CheckConstraint(
                check=~models.Q(message_body=''),
                name='message_body_not_empty'
            )
        ]
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"
    
    def get_preview(self, length=50):
        """Return a preview of the message body."""
        if len(self.message_body) > length:
            return f"{self.message_body[:length]}..."
        return self.message_body
    