from rest_framework import serializers

from .models import EducationRecord


class EducationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationRecord
        fields = [
            "id",
            "owner",
            "institution",
            "degree",
            "field_of_study",
            "start_date",
            "end_date",
            "is_current",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def validate(self, attrs):
        """Keep chronological and current-study information consistent."""
        start_date = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end_date = attrs.get("end_date", getattr(self.instance, "end_date", None))
        is_current = attrs.get("is_current", getattr(self.instance, "is_current", False))

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": "La date de fin doit être postérieure à la date de début."}
            )

        if is_current and end_date:
            raise serializers.ValidationError(
                {"end_date": "Une formation en cours ne peut pas avoir de date de fin."}
            )

        return attrs
