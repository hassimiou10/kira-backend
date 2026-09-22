from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import google.generativeai as genai

from .models import DeveloperAssistantPrompt
from .serializers import DeveloperAssistantPromptSerializer

genai.configure(api_key=settings.GEMINI_API_KEY)


def _ask_gemini(prompt_text):
    model = genai.GenerativeModel("gemini-3.5-flash-lite")
    response = model.generate_content(prompt_text)
    return response.text.strip()


class DeveloperAssistantPromptViewSet(viewsets.ModelViewSet):
    serializer_class = DeveloperAssistantPromptSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "status": ["exact"],
        "title": ["exact", "icontains"],
        "created_at": ["exact", "gte", "lte"],
    }

    search_fields = [
        "title",
        "prompt",
        "response",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "title",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        return DeveloperAssistantPrompt.objects.filter(
            owner=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)




class GenerateCodeView(APIView):
    """
    Générer du code avec l'IA
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = (
            request.data.get("prompt")
            or request.data.get("description")
            or ""
        )
        language = request.data.get("language", "python")

        if not prompt:
            return Response(
                {"error": "Le prompt est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            f"Écris du code {language} pour répondre à cette demande. "
            f"Réponds uniquement avec le code, sans explication ni texte autour, "
            f"sans balises markdown.\n\nDemande: {prompt}"
        )

        try:
            code = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "data": {
                    "language": language,
                    "prompt": prompt,
                    "code": code,
                }
            }
        )


class FixBugView(APIView):
    """
    Corriger un bug dans un code
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")
        error = (
            request.data.get("error")
            or request.data.get("error_message")
            or ""
        )
        language = request.data.get("language", "")

        if not code:
            return Response(
                {"error": "Le code est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            "Corrige ce code qui contient un bug. Réponds uniquement avec le "
            "code corrigé, sans explication ni balises markdown.\n\n"
            f"Langage: {language}\n"
            f"Code:\n{code}\n\n"
            f"Erreur rencontrée: {error}"
        )

        try:
            fixed_code = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "data": {
                    "original_code": code,
                    "error": error,
                    "fixed_code": fixed_code,
                }
            }
        )


class ExplainCodeView(APIView):
    """
    Expliquer un code
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")

        if not code:
            return Response(
                {"error": "Le code est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            "Explique ce code de manière claire et pédagogique, en français, "
            f"étape par étape.\n\nCode:\n{code}"
        )

        try:
            explanation = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "explanation": explanation,
            }
        )


class ReviewCodeView(APIView):
    """
    Faire une revue de code
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code")

        if not code:
            return Response(
                {"error": "Le code est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            "Fais une revue de code professionnelle de ce code. Réponds "
            "uniquement avec un objet JSON valide ayant exactement ces clés : "
            '"quality" (évaluation générale), "security" (problèmes de '
            'sécurité éventuels), "performance" (pistes d\'optimisation). '
            f"Ne mets rien d'autre que le JSON.\n\nCode:\n{code}"
        )

        try:
            raw_response = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        import json
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            review = json.loads(cleaned)
        except Exception:
            review = {
                "quality": raw_response,
                "security": "",
                "performance": "",
            }

        return Response(
            {
                "data": {
                    "review": review,
                }
            }
        )