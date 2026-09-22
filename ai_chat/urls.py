from django.urls import path
from .views import ConversationListCreateView, ConversationDetailView, SendMessageView

urlpatterns = [
    path('conversations/', ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/messages/', SendMessageView.as_view(), name='send-message'),
    path('send/', SendMessageView.as_view(), name='send-message-compat'),
]
