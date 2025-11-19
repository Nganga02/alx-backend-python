from rest_framework.permissions import BasePermission
from models import (
    Conversation,
    Message
)


class IsParticipant(BasePermission):
    """Class to determine if the logged in user
    should access a conversation"""
    def has_permission(self, request, view):
        """Gives only authenticated users access to the api"""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Grants access to users for the conversation object""" 
        return request.user in obj.participants_id.all()

class IsSender(BasePermission):
    """Class to determine if the logged in user 
    should access the message"""
    def has_permission(self, request, view):
        """Gives only authenticated users access to the api"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Grants access to users for the conversation object""" 
        return obj.sender_id == request.user