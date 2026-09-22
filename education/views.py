from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import google.generativeai as genai
import json

from .models import EducationRecord
from .serializers import EducationRecordSerializer

genai.configure(api_key=settings.GEMINI_API_KEY)


def _ask_gemini(prompt_text):
    model = genai.GenerativeModel("gemini-3.5-flash-lite")
    response = model.generate_content(prompt_text)
    return response.text.strip()


def _clean_json(raw_text):
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


class EducationSearchFilter(filters.SearchFilter):
    search_param = "q"


class EducationRecordViewSet(viewsets.ModelViewSet):
    serializer_class = EducationRecordSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        EducationSearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "institution": ["exact", "icontains"],
        "degree": ["exact", "icontains"],
        "field_of_study": ["exact", "icontains"],
        "is_current": ["exact"],
        "start_date": ["exact", "gte", "lte"],
        "end_date": ["exact", "gte", "lte"],
    }

    search_fields = [
        "institution",
        "degree",
        "field_of_study",
        "description",
    ]

    ordering_fields = [
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
        "institution",
    ]

    ordering = ["-end_date", "-start_date"]

    def get_queryset(self):
        return EducationRecord.objects.filter(
            owner=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




class SummarizeCourseView(APIView):
    """
    Résumer un cours avec l'IA
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get("content")

        if not content:
            return Response(
                {"error": "Le contenu du cours est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            "Résume ce cours de manière claire, structurée et pédagogique, "
            "en français, en gardant les points essentiels.\n\n"
            f"Contenu du cours:\n{content}"
        )

        try:
            summary = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "summary": summary,
                "status": "success",
            }
        )


class GenerateQuizView(APIView):
    """
    Générer un quiz à partir d'un cours
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get("content")
        num_questions = request.data.get("num_questions", 5)

        if not content:
            return Response(
                {"error": "Le contenu du cours est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            f"Génère un quiz de {num_questions} questions à choix multiples "
            "en français à partir de ce cours. Réponds uniquement avec un "
            "tableau JSON valide, où chaque élément a exactement ces clés : "
            '"question" (string), "options" (liste de 3 à 4 chaînes), '
            '"answer" (la bonne réponse, identique à une des options). '
            f"Ne mets rien d'autre que le JSON.\n\nContenu du cours:\n{content}"
        )

        try:
            raw_response = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            quiz = json.loads(_clean_json(raw_response))
        except Exception:
            quiz = []

        return Response(
            {
                "quiz": quiz,
            }
        )


class GenerateFlashcardsView(APIView):
    """
    Générer des cartes mémoire
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get("content")
        num_cards = request.data.get("num_cards", 8)

        if not content:
            return Response(
                {"error": "Le contenu du cours est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            f"Génère {num_cards} flashcards en français à partir de ce cours. "
            "Réponds uniquement avec un tableau JSON valide, où chaque élément "
            'a exactement ces clés : "front" (question ou terme court), '
            '"back" (réponse ou définition concise). '
            f"Ne mets rien d'autre que le JSON.\n\nContenu du cours:\n{content}"
        )

        try:
            raw_response = _ask_gemini(ai_prompt)
        except Exception as e:
            return Response(
                {"error": f"Erreur IA: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            flashcards = json.loads(_clean_json(raw_response))
        except Exception:
            flashcards = []

        return Response(
            {
                "flashcards": flashcards,
            }
        )


class FlashcardListView(APIView):
    """
    Liste des flashcards utilisateur.
    (Pas encore de persistance en base : les flashcards générées
    sont à gérer côté client pour le moment.)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "flashcards": []
            }
        )


class MasterFlashcardView(APIView):
    """
    Marquer une flashcard comme maîtrisée.
    (Pas encore de persistance en base.)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        return Response(
            {
                "message": "Flashcard maîtrisée.",
                "flashcard_id": pk,
            }
        )


class ExplainConceptView(APIView):
    """
    Expliquer un concept avec l'IA
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        concept = request.data.get("concept")

        if not concept:
            return Response(
                {"error": "Le concept est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ai_prompt = (
            "Explique ce concept de manière claire, simple et pédagogique, "
            f"en français, avec un exemple concret si possible.\n\nConcept: {concept}"
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
                "concept": concept,
                "explanation": explanation,
            }
        )