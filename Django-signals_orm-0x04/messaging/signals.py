from django.db.models.signals import (
    post_save, 
    pre_save, 
    post_delete
    )
from django.dispatch import receiver
from .models import (
    Message,
    Notification,
    MessageHistory,
    CustomUser)

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


@receiver(post_delete, sender = CustomUser)
def delete_user_related_data(sender, instance, **kwargs):
    """Deleting all data related to the user"""
    Message.objects.filter(sender=instance).delete()
    Notification.objects.filter(User=instance).delete()
    MessageHistory.objects.filter(message_sender = instance).delete()