from django.urls import path, include
from user.views import (
    UserRegisterAPIView,
    UserProfilePictureUploadAPIView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path(
        "upload-profile-picture/",
        UserProfilePictureUploadAPIView.as_view(),
        name="upload-profile-picture",
    ),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", UserRegisterAPIView.as_view()),
]
