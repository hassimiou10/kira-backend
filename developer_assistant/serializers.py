from rest_framework import serializers

from .models import DeveloperAssistantPrompt


class DeveloperAssistantPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeveloperAssistantPrompt
        fields = [
            "id",
            "owner",
            "title",
            "prompt",
            "response",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "response", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data["owner"] = request.user
        return super().create(validated_data)
