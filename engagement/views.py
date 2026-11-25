from idlelib.debugobj_r import remote_object_tree_item

from django.db.migrations import serializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import DestroyAPIView, ListCreateAPIView,GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from news.models import News
from .models import Comment,SavedNews,Subscription
from .serializers import CommentSerializer,SavedNewsSerializer,SubscriptionRequestSerializer,SubscriptionUnsubscribeSerializer
from rest_framework.response import Response
from .services import send_subscription_confirmation
from django.core import signing
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle


class CommentCreateAPIView(ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        news = get_object_or_404(
            News,
            slug=self.kwargs["slug"],
            status=News.Status.PUBLISHED,
        )
        return Comment.objects.filter(
            news=news,
            status=Comment.Status.APPROVED,
        ).order_by("created_at", "id")

    def perform_create(self, serializer):
        news = get_object_or_404(
            News,
            slug=self.kwargs["slug"],
            status=News.Status.PUBLISHED,
        )
        serializer.save(user=self.request.user, news=news)


class SavedNewsListCreateAPIView(ListCreateAPIView):
    serializer_class = SavedNewsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedNews.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedNewsDeleteAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedNews.objects.filter(user=self.request.user)


class SubscriptionRequestAPIView(GenericAPIView):
    serializer_class = SubscriptionRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "subscription"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription, created = Subscription.objects.get_or_create(
            email=serializer.validated_data["email"],
            defaults={"is_active": False},
        )

        if not subscription.is_active:
            send_subscription_confirmation(subscription)

        return Response({
            "detail": "Obuna tasdiqlanishi kerak bo'lsa xat yuborildi"
        })


class SubscriptionConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self,request):
        token = request.query_params.get("token")

        if not token:
            return Response(
                {"detail": "Tasdqilash tokeni kerak"},
                status=400,
            )
        try:
            data = signing.loads(
                token,
                salt="subscription-confirmation",
                max_age=24 * 60 * 60,
            )
        except signing.BadSignature:
            return Response(
                {"detail": "Havola yaroqsiz  yoki muddati tugagan"},
                status=400,

            )
        subscription = get_object_or_404(
            Subscription,
            pk=data["subscription_id"],
            email=data["email"],
        )
        subscription.is_active = True
        subscription.save(update_fields=["is_active"])

        return Response({
            "detail": "Obuna Tasdiqlandi"
        })


class SubscriptionUnsubscribeAPIView(GenericAPIView):
    serializer_class = SubscriptionUnsubscribeSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "detail": "Obunadan chiqishni tasdiqlash uchun POST yuboring"
        })

    def post(self, request):
        token = (
            request.data.get("token")
            or request.query_params.get("token")
        )
        serializer = self.get_serializer(data={"token": token})
        serializer.is_valid(raise_exception=True)

        try:
            data = signing.loads(
                serializer.validated_data["token"],
                salt="subscription-unsubscribe",
                max_age=30 * 24 * 60 * 60,
            )
        except signing.BadSignature:
            return Response(
                {"detail": "Havola yaroqsiz yoki muddati tugagan"},
                status=400,
            )

        subscription = get_object_or_404(
            Subscription,
            pk=data["subscription_id"],
            email=data["email"],
        )
        subscription.is_active = False
        subscription.save(update_fields=["is_active"])

        return Response({
            "detail": "Obunadan chiqdingiz"
        })


