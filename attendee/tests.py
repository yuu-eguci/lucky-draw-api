from django.test import TestCase
from rest_framework.test import APIClient

from .models import Attendee

LIST_URL = "/api/v1/attendee/"


def detail_url(pk):
    return f"{LIST_URL}{pk}/"


VALID = {"name": "taro", "email": "taro@example.com", "phone": "09012345"}


class AttendeeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_and_list(self):
        res = self.client.post(LIST_URL, VALID, format="json")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(set(res.json()), {"id", "name", "email", "phone"})
        res = self.client.get(LIST_URL)
        self.assertEqual(res.status_code, 200)
        self.assertEqual([a["email"] for a in res.json()], [VALID["email"]])

    def test_retrieve_update_delete(self):
        attendee = Attendee.objects.create(**VALID)
        self.assertEqual(
            self.client.get(detail_url(attendee.pk)).json()["name"], "taro"
        )
        res = self.client.patch(
            detail_url(attendee.pk), {"name": "jiro"}, format="json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Attendee.objects.get(pk=attendee.pk).name, "jiro")
        self.assertEqual(self.client.delete(detail_url(attendee.pk)).status_code, 204)
        self.assertFalse(Attendee.objects.exists())

    def test_admin_prefixed_route_is_kept(self):
        self.assertEqual(self.client.get("/admin/attendee/").status_code, 200)

    def test_duplicate_email_and_phone_are_rejected(self):
        Attendee.objects.create(**VALID)
        res = self.client.post(LIST_URL, VALID, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.json())
        self.assertIn("phone", res.json())

    def test_invalid_email_is_rejected(self):
        res = self.client.post(
            LIST_URL, {**VALID, "email": "not-an-email"}, format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.json())

    def test_too_short_phone_is_rejected(self):
        res = self.client.post(LIST_URL, {**VALID, "phone": "1234567"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("phone", res.json())

    def test_too_long_values_are_rejected(self):
        res = self.client.post(
            LIST_URL, {**VALID, "name": "a" * 65, "phone": "1" * 11}, format="json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.json()), {"name", "phone"})

    def test_phone_with_spaces_is_rejected(self):
        res = self.client.post(LIST_URL, {**VALID, "phone": "090 1234"}, format="json")
        self.assertEqual(res.status_code, 400)
        self.assertIn("phone", res.json())


class CorsTests(TestCase):
    def test_whitelisted_origin_is_allowed(self):
        res = self.client.get(LIST_URL, headers={"Origin": "http://localhost:3000"})
        self.assertEqual(
            res.headers["Access-Control-Allow-Origin"], "http://localhost:3000"
        )
        self.assertNotIn("Access-Control-Allow-Credentials", res.headers)

    def test_unknown_origin_is_not_allowed(self):
        res = self.client.get(LIST_URL, headers={"Origin": "http://evil.example"})
        self.assertNotIn("Access-Control-Allow-Origin", res.headers)
