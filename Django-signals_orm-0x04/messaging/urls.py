from django.urls import path
from . import views



urlpatterns = [
    path('users/<int:pk>/delete', views.delete_user, name='delete_user')
]