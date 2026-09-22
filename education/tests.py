from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import TestCase
from rest_framework.test import APIClient

from .models import EducationRecord


class EducationAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="eduuser", email="edu@example.com", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_retrieve_update_delete_education_record(self):
        list_url = reverse("educationrecord-list")
        create_payload = {
            "institution": "Test University",
            "degree": "Master of Science",
            "field_of_study": "Computer Science",
            "start_date": "2021-09-01",
            "end_date": "2023-06-30",
            "is_current": False,
            "description": "Thesis on backend systems.",
        }

        create_resp = self.client.post(list_url, create_payload, format="json")
        self.assertEqual(create_resp.status_code, 201)
        record_id = create_resp.data["id"]

        detail_url = reverse("educationrecord-detail", kwargs={"pk": record_id})
        retrieve_resp = self.client.get(detail_url)
        self.assertEqual(retrieve_resp.status_code, 200)
        self.assertEqual(retrieve_resp.data["institution"], "Test University")
        self.assertEqual(retrieve_resp.data["owner"], self.user.id)

        update_payload = {
            "description": "Updated thesis description.",
            "is_current": True,
            "end_date": None,
        }
        update_resp = self.client.patch(detail_url, update_payload, format="json")
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.data["description"], "Updated thesis description.")
        self.assertTrue(update_resp.data["is_current"])

        delete_resp = self.client.delete(detail_url)
        self.assertIn(delete_resp.status_code, (204, 200))
        self.assertEqual(self.client.get(detail_url).status_code, 404)

    def test_record_cannot_be_accessed_by_another_user(self):
        record = EducationRecord.objects.create(
            owner=self.user,
            institution="Private University",
            degree="Bachelor",
        )
        other_user = get_user_model().objects.create_user(
            username="otheruser", password="pass"
        )
        self.client.force_authenticate(other_user)

        detail_url = reverse("educationrecord-detail", kwargs={"pk": record.id})
        self.assertEqual(self.client.get(detail_url).status_code, 404)
        self.assertEqual(self.client.patch(detail_url, {"degree": "Changed"}, format="json").status_code, 404)

    def test_rejects_inconsistent_dates(self):
        response = self.client.post(
            reverse("educationrecord-list"),
            {
                "institution": "Test University",
                "degree": "Bachelor",
                "start_date": "2024-01-01",
                "end_date": "2023-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("end_date", response.data)

    def test_search_endpoint_returns_matching_records(self):
        EducationRecord.objects.create(
            owner=self.user,
            institution="Backend Academy",
            degree="Bachelor",
            field_of_study="Software Engineering",
        )
        EducationRecord.objects.create(
            owner=self.user,
            institution="Frontend College",
            degree="Bachelor",
            field_of_study="Design",
        )

        response = self.client.get(reverse("educationrecord-search"), {"q": "Backend"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["institution"], "Backend Academy")
