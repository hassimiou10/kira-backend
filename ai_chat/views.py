from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import google.generativeai as genai

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    SendMessageSerializer,
)

genai.configure(api_key=settings.GEMINI_API_KEY)


class ConversationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        return Conversation.objects.filter(
            user=self.request.user
        ).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Keep the response shape consistent with the Flutter client.
        return Response({"data": response.data})


class ConversationDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({"data": response.data})


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        conversation_id = pk or request.data.get("conversation_id")
        if conversation_id:
            conversation = get_object_or_404(
                Conversation,
                pk=conversation_id,
                user=request.user,
            )
        else:
            # The first message starts a new conversation.
            title = (request.data.get("message") or request.data.get("content") or "")
            conversation = Conversation.objects.create(
                user=request.user,
                title=title[:80] or "Nouvelle conversation",
            )

        payload = request.data.copy()
        # Flutter sends `message`; the original Django endpoint used `content`.
        if "content" not in payload and "message" in payload:
            payload["content"] = payload["message"]
        serializer = SendMessageSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        user_content = serializer.validated_data["content"]

        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_content,
        )

        history = conversation.messages.order_by("created_at")

        gemini_history = []
        for message in history:
            gemini_role = "model" if message.role == "assistant" else "user"
            gemini_history.append({"role": gemini_role, "parts": [message.content]})

        try:
            model = genai.GenerativeModel("gemini-3.5-flash-lite")
            # The SDK expects roles MODEL or USER; use MODEL to convey system-like instruction
            system_prompt = {
                "role": "model",
                "parts": [
                    "Tu es KIRA, un assistant IA intelligent, utile, professionnel et toujours poli."
                ],
            }
            chat = model.start_chat(history=[system_prompt] + gemini_history[:-1])
            response = chat.send_message(user_content)
            ai_content = response.text

        except Exception as e:
            return Response(
                {"error": f"Erreur IA : {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        ai_message = Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=ai_content,
        )

        conversation.save()

        return Response(
            {
                "conversation_id": str(conversation.id),
                "conversation_title": conversation.title,
                "message": MessageSerializer(ai_message).data,
                "user_message": user_content,
                "ai_message": ai_content,
                "ai_message_id": ai_message.id,
            },
            status=status.HTTP_201_CREATED,
        )
