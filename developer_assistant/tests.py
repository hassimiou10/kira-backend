from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient

from .models import DeveloperAssistantPrompt


class DeveloperAssistantAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="devuser", email="dev@example.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_and_list_prompts(self):
        list_url = reverse("developerassistantprompt-list")
        payload = {
            "title": "Initial prompt",
            "prompt": "Generate a code example for a Django view.",
        }

        response = self.client.post(list_url, payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Initial prompt")
        self.assertEqual(response.data["owner"], self.user.id)
        self.assertEqual(response.data["status"], DeveloperAssistantPrompt.STATUS_PENDING)

        list_resp = self.client.get(list_url)
        self.assertEqual(list_resp.status_code, 200)
        self.assertEqual(len(list_resp.data), 1)

    def test_prompt_cannot_be_accessed_by_other_user(self):
        prompt = DeveloperAssistantPrompt.objects.create(
            owner=self.user,
            title="Private prompt",
            prompt="Secret code",
        )

        other_user = get_user_model().objects.create_user(username="otheruser", password="pass")
        self.client.force_authenticate(other_user)

        detail_url = reverse("developerassistantprompt-detail", kwargs={"pk": prompt.id})
        self.assertEqual(self.client.get(detail_url).status_code, 404)
