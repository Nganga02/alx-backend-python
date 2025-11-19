from rest_framework import permissions, Basepermission
from models import (
    Conversation,
    Message
)


class IsParticipant(Basepermission):
    def has_permission(self, request, view):
        result = Conversation.objects.filter(participants=request.user)
        if result:
            return True
        else:
            return False 