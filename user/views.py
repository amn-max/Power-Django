from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
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
from rest_framework_simplejwt.tokens import RefreshToken

# serilaizer
from user.serializers.user import UserRegisterSerializer, UserLoginSerializer

User = get_user_model()


class UserLoginAPIView(LoggingMixin, APIView):
    def post(self, request: HttpRequest, *args, **kargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            response = {"username": {"detail": "User Doesnot exist!"}}
            if User.objects.filter(username=request.data["username"]).exists():
                user = User.objects.get(username=request.data["username"])
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])
                refresh = str(RefreshToken.for_user(user))
                access = str(RefreshToken.for_user(user).access_token)
                response = {
                    "success": True,
                    "username": user.username,
                    "email": user.email,
                    "refresh_token": refresh,
                    "access_token": access,
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterAPIView(LoggingMixin, APIView):
    def post(self, request: HttpRequest, *args, **kargs):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = {
                "success": True,
                "user": serializer.data,
                "token": Token.objects.get(
                    user=User.objects.get(username=serializer.data["username"])
                ).key,
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors, code=status.HTTP_406_NOT_ACCEPTABLE)


class UserLogoutAPIView(LoggingMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: HttpRequest, *args):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"success": True, "detail": "Logged out!"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


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
