from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions
from django.core.exceptions import PermissionDenied



class IsParticipantOfConversation(BasePermission):
    """Class to determine if the logged in user
    should access a conversation or a message"""
    def has_permission(self, request, view):
        """Gives only authenticated users access to the api"""
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Grants access to users for the conversation object""" 
        if hasattr(obj, 'conversation_id'): # if the obj is a message model
            conversation = obj.conversation_id
        else:
            conversation = obj # if the obj is a conversation model
        return request.user in conversation.participants_id.all()

class IsSender(BasePermission):
    """Class to determine if the logged in user 
    should access the message"""
    def has_permission(self, request, view):
        """Gives only authenticated users access to the api"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Grants access to users for the conversation object""" 
        if request.method in SAFE_METHODS:
            return True
        if request.method in ('DELETE', 'PATCH', 'PUT', 'POST'):
            if obj.sender_id == request.user:
                return True
            else:
                raise PermissionDenied('Permission denied')
        
