from rest_framework import serializers
from django.contrib.auth import get_user_model

# all auth
from dj_rest_auth.registration.serializers import RegisterSerializer


User = get_user_model()


class UserRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password2",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        user.save(update_fields=["first_name", "last_name"])
