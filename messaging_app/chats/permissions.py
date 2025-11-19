from rest_framework import permissions, BasePermission
from models import (
    Conversation,
    Message
)


class IsParticipant(BasePermission):
    """Class to determine if the logged in user
    should access a conversation"""
    def has_object_permission(self, request, view, obj):
        return request.user in obj.participants_id.all()

class IsSender(BasePermission):
    """Class to determine if the logged in user 
    should access the message"""
    def has_object_permission(self, request, view, obj):
        return obj.sender_id == request.user