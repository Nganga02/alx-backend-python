from django.db import models



class UnreadMessagesManager(models.Manager):
    """Unread messages custom manager"""
    def unread_messages(self, user):
        return self.filter(receiver = user, read = False)