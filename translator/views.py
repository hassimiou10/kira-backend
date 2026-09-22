from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import google.generativeai as genai
from .models import Translation
from .serializers import TranslationSerializer, TranslateRequestSerializer

genai.configure(api_key=settings.GEMINI_API_KEY)

LANGUAGE_NAMES = dict(Translation.LANGUAGE_CHOICES)


class TranslationHistoryView(generics.ListAPIView):
    serializer_class = TranslationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Translation.objects.filter(user=self.request.user)


class TranslateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TranslateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        source_lang_name = LANGUAGE_NAMES[data['source_language']]
        target_lang_name = LANGUAGE_NAMES[data['target_language']]

        prompt = (
            f"Traduis ce texte de {source_lang_name} vers {target_lang_name}. "
            f"Réponds uniquement avec la traduction, sans explication ni guillemets.\n\n"
            f"Texte: {data['source_text']}"
        )

        try:
            model = genai.GenerativeModel("gemini-3.5-flash-lite")
            response = model.generate_content(prompt)
            translated_text = response.text.strip()
        except Exception as e:
            return Response({'error': f'Erreur traduction: {str(e)}'}, status=status.HTTP_502_BAD_GATEWAY)

        translation = Translation.objects.create(
            user=request.user,
            source_language=data['source_language'],
            target_language=data['target_language'],
            source_text=data['source_text'],
            translated_text=translated_text,
        )

        return Response(TranslationSerializer(translation).data, status=status.HTTP_201_CREATED)