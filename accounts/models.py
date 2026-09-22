
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    LANGUAGE_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
    ]

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
    )

    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='fr',
    )

    is_premium = models.BooleanField(default=False)

    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
