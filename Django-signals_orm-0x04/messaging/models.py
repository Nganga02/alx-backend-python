from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    pass


class Message(models.Model):

    content = models.TextField(blank = False)
    edited = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add=True)    
    read = models.BooleanField(default = False)
    delivered = models.BooleanField(default = False)

    #relationships
    sender = models.ForeignKey(
        CustomUser,
        on_delete= models.CASCADE,
        related_name='messages'
    )

    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f'{self.sender}: {self.content}'
    

class Notification(models.Model):
    recepient = models.ForeignKey(
        CustomUser,
        on_delete = models.CASCADE,
        related_name = 'notifications'
    )

    actor = models.ForeignKey(
        CustomUser,
        on_delete= models.DO_NOTHING
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.DO_NOTHING,
        related_name='messages'
    )

    def __str__(self):
        return f'From: {self.actor} To: {self.recepient}'