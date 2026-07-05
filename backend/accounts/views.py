from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings

from .serializers import UserSerializer

User = get_user_model()


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        credential = request.data.get("credential")
        if not credential:
            raise AuthenticationFailed("Missing Google credential.")

        try:
            payload = id_token.verify_oauth2_token(
                credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError as exc:
            raise AuthenticationFailed("Invalid Google credential.") from exc

        email = payload.get("email")
        if not email:
            raise AuthenticationFailed("Google account has no email.")

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": payload.get("given_name", ""),
                "last_name": payload.get("family_name", ""),
            },
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
