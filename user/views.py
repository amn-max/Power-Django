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
from keycloak import KeycloakOpenID, KeycloakOpenIDConnection, KeycloakAdmin
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/auth/",
    client_id="power-django",
    realm_name="master",
    client_secret_key="Ps01E535aRlAJN4oZjbGavaYclXIT9I9",
)


keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080/auth/",
    username="admin",
    password="Password@123",
    realm_name="master",
    user_realm_name="master",
    client_id="power-django",
    client_secret_key="Ps01E535aRlAJN4oZjbGavaYclXIT9I9",
    verify=True,
)

# serilaizer
from user.serializers.user import UserRegisterSerializer, UserLoginSerializer

User = get_user_model()


@parser_classes([JSONParser])
class UserLoginAPIView(LoggingMixin, APIView):
    def post(self, request: HttpRequest, *args, **kargs):
        request_body = request.data
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            response = {"username": {"detail": "User Doesnot exist!"}}
            if User.objects.filter(username=request.data["username"]).exists():
                user = User.objects.get(username=request.data["username"])
                user.last_login = timezone.now()
                user.save(update_fields=["last_login"])

                token = keycloak_openid.token(
                    request_body["username"], request_body["password"]
                )

                response = {
                    "success": True,
                    "username": user.username,
                    "email": user.email,
                    "token": token,
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@parser_classes([JSONParser])
class UserRegisterAPIView(LoggingMixin, APIView):
    def post(self, request: HttpRequest, *args, **kargs):
        request_body = request.data

        if request_body["password"] != request_body["password2"]:
            raise ValidationError({"message": "Both password must match"})

        Keycloak_user_id = keycloak_admin.create_user(
            {
                "email": request_body["email"],
                "username": request_body["username"],
                "enabled": True,
                "firstName": request_body["first_name"],
                "lastName": request_body["last_name"],
                "credentials": [
                    {
                        "value": request_body["password"],
                        "type": "password",
                    }
                ],
            }
        )
        request_body["keycloak_id"] = str(Keycloak_user_id)
        serializer = UserRegisterSerializer(data=request_body)
        if serializer.is_valid():
            serializer.save()

            token = keycloak_openid.token(
                request_body["username"], request_body["password"]
            )

            response = {
                "success": True,
                "user": serializer.data,
                "token": token,
            }
            return Response(response, status=status.HTTP_200_OK)
        raise ValidationError(serializer.errors, code=status.HTTP_406_NOT_ACCEPTABLE)


class UserLogoutAPIView(LoggingMixin, APIView):
    def post(self, request: HttpRequest, *args):
        try:
            request_body = request.data
            KEYCLOAK_PUBLIC_KEY = (
                "-----BEGIN PUBLIC KEY-----\n"
                + keycloak_openid.public_key()
                + "\n-----END PUBLIC KEY-----"
            )
            options = {"verify_signature": True, "verify_aud": True, "verify_exp": True}
            token_info = keycloak_openid.decode_token(
                request_body["access_token"], key=KEYCLOAK_PUBLIC_KEY, options=options
            )
            refresh_token = request.data["refresh_token"]
            keycloak_openid.logout(refresh_token)
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
