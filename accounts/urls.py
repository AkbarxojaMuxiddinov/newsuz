from django.urls import path
from .views import RegisterAPIView, ProfileAPIView, LogoutAPIView, PasswordResetRequestAPIView
from rest_framework.authtoken.views import obtain_auth_token
from .views import ChangePasswordAPIView, PasswordResetConfirmAPIView, LoginAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("me/", ProfileAPIView.as_view(), name="profile"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("change_password/", ChangePasswordAPIView.as_view(), name="change_password"),
    path("reset-password/",
         PasswordResetRequestAPIView.as_view(),name="reset_password"),
    path("reset-password/confirm/", PasswordResetConfirmAPIView.as_view(),name="reset_password_confirm"),

]
