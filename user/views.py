from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from datetime import datetime

from mixins.logging_mixin import LoggingMixin

# serilaizer
from user.serializers.user import UserRegisterSerializer, UserLoginSerializer


class UserLoginAPIView(LoggingMixin, APIView):
    def post(self, request, *args, **kargs):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            response = {"username": {"detail": "User Doesnot exist!"}}
            if User.objects.filter(username=request.data["username"]).exists():
                user = User.objects.get(username=request.data["username"])
                user.last_login = datetime.now()
                user.save(update_fields=["last_login"])
                token, created = Token.objects.get_or_create(user=user)
                response = {
                    "success": True,
                    "username": user.username,
                    "email": user.email,
                    "token": token.key,
                }
                return Response(response, status=status.HTTP_200_OK)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegisterAPIView(LoggingMixin, APIView):
    def post(self, request, *args, **kargs):
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

    def post(self, request, *args):
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response(
            {"success": True, "detail": "Logged out!"}, status=status.HTTP_200_OK
        )