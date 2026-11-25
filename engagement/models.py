from django.db import models
from django.conf import settings

class Comment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        APPROVED = "approved", "tasdiqlandi"
        REJECTED = "rejected", "bekor qilindi"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    news = models.ForeignKey(
        "news.News",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.news.title}"

class SavedNews(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_news",
    )
    news = models.ForeignKey(
        "news.News",
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "news"],
                name="unique_saved_news_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user.username} — {self.news.title}"

    
class Subscription(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


