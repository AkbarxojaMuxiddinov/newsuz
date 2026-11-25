from rest_framework import serializers

from .models import News, NewsImage,Banner


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ("id", "image")



class NewsSerializer(serializers.ModelSerializer):
    images = NewsImageSerializer(many=True, read_only=True)
    class Meta:
        model = News
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "body",
            "image",
            "category",
            "author",
            "status",
            "is_featured",
            "view_count",
            "created_at",
            "updated_at",
            "published_at",
            "images",
        )

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ("id", "title", "image", "link")