from django.conf import settings
from django.db import models


class Translation(models.Model):
    LANGUAGE_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
        ('es', 'Español'),
        ('ar', 'العربية'),
        ('pt', 'Português'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='translations')
    source_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    target_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES)
    source_text = models.TextField()
    translated_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.source_language} → {self.target_language}: {self.source_text[:30]}"