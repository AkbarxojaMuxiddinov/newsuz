from django.contrib.auth.base_user import AbstractBaseUser
from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.throttling import ScopedRateThrottle

from .serializers import PasswordResetConfirmSerializer

from .serializers import PasswordResetRequestSerializer


from .serializers import RegisterSerializer,ProfileSerializer, ChangePasswordSerializer

class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class ProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        request.auth.delete()
        return Response(
            {"detail": "Tizimdan chiqildi"},
            status=status.HTTP_200_OK,
        )



class ChangePasswordAPIView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save(update_fields=["password"])
            Token.objects.filter(user=user).delete()

        return Response({
            "detail": "Parol o'zgartirildi Qayta login qiling"
        })

class PasswordResetRequestAPIView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        users = get_user_model().objects.filter(email__iexact=serializer.validated_data["email"], is_active=True)

        for user in users:
            if not user.has_usable_password():
                continue

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = (
                f"{settings.SITE_URL.rstrip('/')}"
                f"/api/accounts/reset-password/confirm/"
                f"?uid={uid}&token={token}"
            )

            send_mail(
                subject="Parolni tiklash",
                message=f"Parolingizni tiklash havolasi:\n{link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

        return Response({
            "detail": "Mos hisob mavjud bo'lsa tiklash xati yuborildi"
        })


class PasswordResetConfirmAPIView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_confirm"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            user = get_user_model().objects.select_for_update().get(pk=data["user"].pk)

            if not default_token_generator.check_token(user, data["token"]):
                raise ValidationError("Tiklash havolasi yaroqsiz")

            user.set_password(data["new_password"])
            user.save(update_fields=["password"])
            Token.objects.filter(user=user).delete()

        return Response({
            "detail": "Parol tiklandi. Yangi parol bilan kiring"
        })

class LoginAPIView(ObtainAuthToken):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"