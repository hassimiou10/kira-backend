from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Document


class DocumentsAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="docuser", email="doc@example.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_retrieve_update_delete_document(self):
        list_url = reverse("document-list")
        payload = {
            "title": "Test document",
            "content": "Contenu du document.",
            "is_public": False,
        }

        create_resp = self.client.post(list_url, payload, format="json")
        self.assertEqual(create_resp.status_code, 201)
        doc_id = create_resp.data["id"]

        detail_url = reverse("document-detail", kwargs={"pk": doc_id})
        retrieve_resp = self.client.get(detail_url)
        self.assertEqual(retrieve_resp.status_code, 200)
        self.assertEqual(retrieve_resp.data["title"], "Test document")
        self.assertEqual(retrieve_resp.data["owner"], self.user.id)

        update_resp = self.client.patch(detail_url, {"title": "Updated title"}, format="json")
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.data["title"], "Updated title")

        delete_resp = self.client.delete(detail_url)
        self.assertIn(delete_resp.status_code, (204, 200))
        self.assertEqual(self.client.get(detail_url).status_code, 404)

    def test_document_cannot_be_accessed_by_another_user(self):
        document = Document.objects.create(
            owner=self.user,
            title="Private doc",
            content="Ceci est privé.",
        )
        other_user = get_user_model().objects.create_user(username="otheruser", password="pass")
        self.client.force_authenticate(other_user)

        detail_url = reverse("document-detail", kwargs={"pk": document.id})
        self.assertEqual(self.client.get(detail_url).status_code, 404)
        self.assertEqual(self.client.patch(detail_url, {"title": "Changed"}, format="json").status_code, 404)

    def test_search_and_filter_documents(self):
        Document.objects.create(owner=self.user, title="Backend guide", content="Tutoriel Django", is_public=False)
        Document.objects.create(owner=self.user, title="Frontend notes", content="React et CSS", is_public=True)

        response = self.client.get(reverse("document-list"), {"search": "Backend"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Backend guide")

        response = self.client.get(reverse("document-list"), {"is_public": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Frontend notes")
