from rest_framework import serializers

from .models import CV


class CVSerializer(serializers.ModelSerializer):
    class Meta:
        model = CV
        fields = [
            "id",
            "owner",
            "full_name",
            "email",
            "phone",
            "summary",
            "template",
            "data",
            "photo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")

        if (
            request
            and hasattr(request, "user")
            and request.user.is_authenticated
        ):
            validated_data["owner"] = request.user

        return super().create(validated_data)