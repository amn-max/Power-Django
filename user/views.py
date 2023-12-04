from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone
from django.http import HttpRequest
from django.core.files.storage import default_storage
from mixins.logging_mixin import LoggingMixin
from dj_rest_auth.registration.views import RegisterView

# serilaizer
from user.serializers.user import UserRegisterSerializer

User = get_user_model()


class UserRegisterAPIView(LoggingMixin, RegisterView):
    serializer_class = UserRegisterSerializer


class UserProfilePictureUploadAPIView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args):
        user = request.user
        profile_picture = request.FILES.get("profile_picture")

        if profile_picture:
            file_path = f"profile_pics/{user.id}_{profile_picture.name}"
            default_storage.save(file_path, profile_picture)

            user.profile_picture = file_path
            user.save(update_fields=["profile_picture"])
            return Response(
                {"success": True, "detail": "Profile picture uploaded successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"success": False, "detail": "No profile picture provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )
