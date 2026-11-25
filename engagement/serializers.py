from rest_framework import serializers
from .models import Comment, SavedNews, Subscription
from news.models import News

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "news", "user", "text", "status", "created_at")
        read_only_fields = ("id", "news", "user", "status", "created_at")

class SavedNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedNews
        fields = ("id", "news", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_news(self, news):
        if news.status != News.Status.PUBLISHED:
            raise serializers.ValidationError(
                "Faqat elon qilingan yangilikni saqlash mumkin"
            )
        return news

    def validate(self, attrs):
        if SavedNews.objects.filter(
            user=self.context["request"].user,
            news=attrs["news"],
        ).exists():
            raise serializers.ValidationError(
                "Bu yangilik allaqachon saqlangan"
            )
        return attrs

class SubscriptionRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SubscriptionUnsubscribeSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=1024)
    
