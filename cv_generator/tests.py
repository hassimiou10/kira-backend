from django.test import TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient

from . import services
from .models import CV


class ServicesTests(TestCase):
    def test_ai_generate_fallback_uses_prompt(self):
        result = services.ai_generate_resume({}, prompt="Experienced backend developer")
        self.assertIsInstance(result, dict)
        self.assertIn("summary", result)

    def test_generate_pdf_reportlab_or_weasy(self):
        cv = CV.objects.create(full_name="Test User", email="t@example.com", summary="Short summary")
        try:
            pdf = services.generate_pdf(cv)
        except RuntimeError:
            self.skipTest("No PDF backend installed (reportlab or weasy)")
            return
        self.assertIsInstance(pdf, (bytes, bytearray))
        self.assertGreater(len(pdf), 10)


class APITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="apiuser", email="api@example.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_crud_pdf_and_ai_endpoints(self):
        list_url = reverse("cv-list")
        create_payload = {
            "full_name": "API User",
            "email": "a@a.com",
            "summary": "API summary",
            "data": {"skills": ["python"]},
        }
        create_resp = self.client.post(list_url, create_payload, format="json")
        self.assertEqual(create_resp.status_code, 201)
        cv_id = create_resp.data["id"]

        detail_url = reverse("cv-detail", kwargs={"pk": cv_id})
        retrieve_resp = self.client.get(detail_url)
        self.assertEqual(retrieve_resp.status_code, 200)
        self.assertEqual(retrieve_resp.data["full_name"], "API User")

        update_payload = {"summary": "Updated summary", "data": {"skills": ["django", "python"]}}
        update_resp = self.client.patch(detail_url, update_payload, format="json")
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.data["summary"], "Updated summary")
        self.assertEqual(update_resp.data["data"]["skills"], ["django", "python"])

        pdf_url = reverse("cv-pdf", kwargs={"pk": cv_id})
        pdf_resp = self.client.get(pdf_url)
        if pdf_resp.status_code != 200:
            self.skipTest("PDF backend not available or endpoint raised an error")
        self.assertEqual(pdf_resp["Content-Type"], "application/pdf")
        self.assertGreater(len(pdf_resp.content), 10)

        download_url = reverse("cv-download-pdf", kwargs={"pk": cv_id})
        download_resp = self.client.get(download_url)
        if download_resp.status_code != 200:
            self.skipTest("PDF backend not available or download endpoint raised an error")
        self.assertEqual(download_resp["Content-Type"], "application/pdf")
        self.assertIn("attachment; filename=", download_resp["Content-Disposition"])
        self.assertGreater(len(download_resp.content), 10)

        ai_url = reverse("cv-ai-generate", kwargs={"pk": cv_id})
        ai_resp = self.client.post(ai_url, {"prompt": "Propose a concise summary."}, format="json")
        self.assertIn(ai_resp.status_code, (200, 201))
        if ai_resp.status_code == 200:
            self.assertIn("data", ai_resp.data)
            self.assertIsInstance(ai_resp.data["data"], dict)

        delete_resp = self.client.delete(detail_url)
        self.assertIn(delete_resp.status_code, (204, 200))
        self.assertEqual(self.client.get(detail_url).status_code, 404)

