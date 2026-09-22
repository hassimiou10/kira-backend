from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import google.generativeai as genai

from .models import Document
from .serializers import DocumentSerializer

genai.configure(api_key=settings.GEMINI_API_KEY)


class DocumentUploadView(generics.CreateAPIView):
    """
    Upload d'un nouveau document.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentListView(generics.ListAPIView):
    """
    Liste des documents de l'utilisateur connecté.
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(
            owner=self.request.user
        ).order_by("-created_at")


class DocumentQuestionView(APIView):
    """
    Pose une question sur un document, avec une vraie réponse IA basée
    sur le contenu du document.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        document = get_object_or_404(
            Document,
            pk=pk,
            owner=request.user
        )

        question = request.data.get("question")

        if not question:
            return Response(
                {"error": "Le champ 'question' est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not document.content:
            return Response(
                {"error": "Ce document n'a pas de contenu exploitable."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            "Voici le contenu d'un document. Réponds à la question de "
            "l'utilisateur en te basant uniquement sur ce contenu. Si la "
            "réponse ne s'y trouve pas, dis-le clairement.\n\n"
            f"Contenu du document:\n{document.content}\n\n"
            f"Question: {question}"
        )

        try:
            model = genai.GenerativeModel("gemini-3.5-flash-lite")
            response = model.generate_content(ai_prompt)
            answer = response.text.strip()
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "document": {
                    "id": document.id,
                    "title": document.title,
                },
                "question": question,
                "answer": answer,
            },
            status=status.HTTP_200_OK,
        )