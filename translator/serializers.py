from rest_framework import serializers
from .models import Translation


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ('id', 'source_language', 'target_language', 'source_text', 'translated_text', 'created_at')
        read_only_fields = ('id', 'translated_text', 'created_at')


class TranslateRequestSerializer(serializers.Serializer):
    source_language = serializers.ChoiceField(choices=Translation.LANGUAGE_CHOICES)
    target_language = serializers.ChoiceField(choices=Translation.LANGUAGE_CHOICES)
    source_text = serializers.CharField()