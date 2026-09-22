
from django.conf import settings
from django.db import models


class CV(models.Model):
   

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cvs",
        null=True,
        blank=True,
    )

    full_name = models.CharField(max_length=255)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=50, blank=True)

    summary = models.TextField(blank=True)

    # Photo de profil du CV
    photo = models.ImageField(
        upload_to="cv_photos/",
        null=True,
        blank=True,
    )

    template = models.CharField(
        max_length=50,
        default="modern",
    )

    data = models.JSONField(
        default=dict,
        blank=True,
    )

    # PDF généré du CV
    pdf = models.BinaryField(
        null=True,
        blank=True,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.full_name} ({self.pk})"
