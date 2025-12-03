from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout, decorators
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser, Message
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib import messages

# Create your views here.
@decorators.login_required
def delete_user(request, pk):
    #fetching the user to delete from the data
    user = get_object_or_404(CustomUser, pk = pk)

    if request.user.pk == user.pk:
        logout(request)
        messages.success(request, "Your account has been successfully deleted")
        user.delete()


@api_view
@permission_classes([IsAuthenticatedOrReadOnly])
def thread_view(request, pk):
    #parent message
    message_qs = Message.objects.filter(
        Q(sender = request.user) |
        Q(receiver = request.user), parent_message = None
    ).select_related(
        'sender',
        'receiver',
        'parent_message'
    ).prefetch_related(
        'replies'
    )

    conversation = [msg.get_thread for msg in message_qs]
    return Response({
        'conversation':conversation
    })