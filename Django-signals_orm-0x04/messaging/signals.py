from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender = Message)
def notify(sender, instance, created, **kwargs):
    """Notify when a message has been created"""
    if created:
        Notification.objects.create(
            recepient = instance.receiver,
            actor = instance.sender,
            message = instance
        )