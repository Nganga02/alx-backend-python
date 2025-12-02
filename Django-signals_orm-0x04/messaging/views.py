from django.shortcuts import render, get_object_or_404
from django.contrib.auth import logout, decorators

from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.contrib import messages

# Create your views here.
@decorators.login_required
@api_view(['GET', 'POST '])
def delete_user(request, pk):
    #fetching the user to delete from the data
    user = get_object_or_404(CustomUser, pk = pk)

    if request.user.pk == user.pk:
        logout(request)
        messages.success(request, "Your account has been successfully deleted")
        user.delete()
