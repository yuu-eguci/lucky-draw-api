import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase, TestCase
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


class AttendeeValidationBoundaryTests(TestCase):
    def post(self, **overrides):
        return self.client.post(
            LIST_URL, {**VALID, **overrides}, content_type="application/json"
        )

    def test_boundary_lengths_are_accepted(self):
        self.assertEqual(self.post(name="a" * 64, phone="12345678").status_code, 201)
        res = self.post(name="b", email="b@example.com", phone="1234567890")
        self.assertEqual(res.status_code, 201)

    def test_empty_name_is_rejected(self):
        res = self.post(name="")
        self.assertEqual(res.status_code, 400)
        self.assertIn("name", res.json())

    def test_unicode_name_is_accepted(self):
        res = self.post(name="山田 太郎")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Attendee.objects.get().name, "山田 太郎")

    def test_non_ascii_phone_is_rejected(self):
        res = self.post(phone="０９０１２３４５")
        self.assertEqual(res.status_code, 400)
        self.assertIn("phone", res.json())

    def test_missing_fields_are_rejected(self):
        res = self.client.post(LIST_URL, {}, content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.json()), {"name", "email", "phone"})


class AttendeeUpdateTests(TestCase):
    def setUp(self):
        self.attendee = Attendee.objects.create(**VALID)
        self.other = Attendee.objects.create(
            name="jiro", email="jiro@example.com", phone="08012345"
        )

    def test_put_replaces_all_fields(self):
        body = {"name": "saburo", "email": "saburo@example.com", "phone": "0701234567"}
        res = self.client.put(
            detail_url(self.attendee.pk), body, content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"id": self.attendee.pk, **body})

    def test_put_without_all_fields_is_rejected(self):
        res = self.client.put(
            detail_url(self.attendee.pk), {"name": "x"}, content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_update_to_other_attendees_email_is_rejected(self):
        res = self.client.patch(
            detail_url(self.attendee.pk),
            {"email": self.other.email},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.json())

    def test_patch_keeping_own_values_is_accepted(self):
        res = self.client.patch(
            detail_url(self.attendee.pk),
            {"phone": VALID["phone"]},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)


class NotFoundTests(TestCase):
    def test_missing_attendee_returns_json_404(self):
        for method in ("get", "put", "patch", "delete"):
            res = getattr(self.client, method)(
                detail_url(999), {}, content_type="application/json"
            )
            self.assertEqual(res.status_code, 404, method)
            self.assertIn("detail", res.json())


class ApiRootTests(TestCase):
    def test_api_root_lists_attendee_endpoint(self):
        res = self.client.get("/api/v1/", headers={"Accept": "application/json"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"attendee": "http://testserver/api/v1/attendee/"})


class SettingsGuardTests(SimpleTestCase):
    def run_check(self, **env):
        base = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
        return subprocess.run(
            [sys.executable, "manage.py", "check"],
            cwd=settings.BASE_DIR,
            env={**base, **env},
            capture_output=True,
            text=True,
        )

    def test_non_debug_without_secret_key_fails(self):
        res = self.run_check(DJANGO_DEBUG="0")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY is required", res.stderr)

    def test_non_debug_with_secret_key_passes(self):
        res = self.run_check(DJANGO_DEBUG="0", DJANGO_SECRET_KEY="test-only-key")
        self.assertEqual(res.returncode, 0)


class AttendeeEdgeCaseTests(TestCase):
    def test_deleted_attendee_is_gone_and_second_delete_is_404(self):
        attendee = Attendee.objects.create(**VALID)
        self.assertEqual(self.client.delete(detail_url(attendee.pk)).status_code, 204)
        self.assertEqual(self.client.get(detail_url(attendee.pk)).status_code, 404)
        self.assertEqual(self.client.delete(detail_url(attendee.pk)).status_code, 404)

    def test_non_numeric_id_is_404(self):
        self.assertEqual(self.client.get(detail_url("abc")).status_code, 404)

    def test_name_over_64_chars_is_rejected(self):
        res = self.client.post(
            LIST_URL, {**VALID, "name": "山" * 65}, content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(set(res.json()), {"name"})
