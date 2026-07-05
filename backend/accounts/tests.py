from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class MeViewTests(APITestCase):
    def test_me_requires_authentication(self):
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        user = User.objects.create_user(
            username="a@example.com", email="a@example.com", first_name="Ada"
        )
        self.client.force_authenticate(user=user)
        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "a@example.com")
        self.assertEqual(response.data["first_name"], "Ada")


class GoogleLoginViewTests(APITestCase):
    def test_missing_credential_is_rejected(self):
        response = self.client.post("/api/auth/google/", {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("accounts.views.id_token.verify_oauth2_token")
    def test_invalid_credential_is_rejected(self, mock_verify):
        mock_verify.side_effect = ValueError("bad token")
        response = self.client.post("/api/auth/google/", {"credential": "bad"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("accounts.views.id_token.verify_oauth2_token")
    def test_valid_credential_creates_user_and_returns_tokens(self, mock_verify):
        mock_verify.return_value = {
            "email": "new@example.com",
            "given_name": "New",
            "family_name": "User",
        }
        response = self.client.post("/api/auth/google/", {"credential": "good"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "new@example.com")
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    @patch("accounts.views.id_token.verify_oauth2_token")
    def test_existing_user_is_reused_not_duplicated(self, mock_verify):
        User.objects.create_user(username="existing@example.com", email="existing@example.com")
        mock_verify.return_value = {"email": "existing@example.com"}
        response = self.client.post("/api/auth/google/", {"credential": "good"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.filter(email="existing@example.com").count(), 1)

    @patch("accounts.views.id_token.verify_oauth2_token")
    def test_credential_without_email_is_rejected(self, mock_verify):
        mock_verify.return_value = {}
        response = self.client.post("/api/auth/google/", {"credential": "good"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(APITestCase):
    def test_valid_refresh_token_returns_new_access_token(self):
        user = User.objects.create_user(username="a@example.com", email="a@example.com")
        refresh = RefreshToken.for_user(user)
        response = self.client.post(
            "/api/auth/token/refresh/", {"refresh": str(refresh)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_refresh_token_is_rejected(self):
        response = self.client.post(
            "/api/auth/token/refresh/", {"refresh": "not-a-real-token"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
