from django.db.models import F
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from unicodedata import category
from .models import News,Banner
from .serializers import NewsSerializer,BannerSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import  SearchFilter

class NewsListAPIView(ListAPIView):
    serializer_class = NewsSerializer
    filter_backends = [SearchFilter]
    search_fields = ["title", "short_description", "body"]

    def get_queryset(self):
        queryset = News.objects.filter(status=News.Status.PUBLISHED)
        category_slug = self.request.query_params.get("category")
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset.order_by("-published_at", "-created_at")


class NewsDetailAPIView(RetrieveAPIView):
    serializer_class = NewsSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return News.objects.filter(status=News.Status.PUBLISHED)

    def retrieve(self, request, *args, **kwargs):
        news = self.get_object()
        News.objects.filter(pk=news.pk).update(
            view_count=F("view_count") + 1
        )
        news.refresh_from_db()
        serializer = self.get_serializer(news)
        return Response(serializer.data)

class BannerListAPIView(ListAPIView):
    serializer_class = BannerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Banner.objects.filter(is_active=True).order_by("-created_at","-id")
