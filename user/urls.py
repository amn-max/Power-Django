from django.urls import path
from user.views import (
    UserLoginAPIView,
    UserRegisterAPIView,
    UserLogoutAPIView,
    UserProfilePictureUploadAPIView,
)

urlpatterns = [
    path("login/", UserLoginAPIView.as_view(), name="user_login"),
    path("register/", UserRegisterAPIView().as_view(), name="user_register"),
    path("logout/", UserLogoutAPIView.as_view(), name="user_logout"),
    path(
        "upload-profile-picture/",
        UserProfilePictureUploadAPIView.as_view(),
        name="upload-profile-picture",
    ),
]
