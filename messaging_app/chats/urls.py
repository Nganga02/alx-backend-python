from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet)
router.register(r'conversations/(?P<conversation_id>\d+)/messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
]