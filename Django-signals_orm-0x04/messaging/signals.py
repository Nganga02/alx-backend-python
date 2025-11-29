from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender = Message)
def notify(sender, instance, created, **kwargs):
    """Notify when a message has been created"""
    if created:
        Notification.objects.create(
            recipient = instance.receiver,
            actor = instance.sender,
            message = instance
        )


@receiver(pre_save, sender = Message)
def log_message_history(sender, instance, **kwargs):
    """Log previous version of edited message to MessageHistory"""
    if instance.pk:
        old_message = Message.objects.get(pk = instance.pk)
        if old_message.content != instance.content:
            message_history = MessageHistory.objects.create(
                message = instance.content,
                old_content = old_message.content
            )
            message_history.participants.add(instance.recipient, instance.actor)
            instance.edited = True
            instance.edited_by = instance.sender
