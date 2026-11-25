from django.db import models
from django.conf import settings
from django.db import models
from django.template.backends.django import reraise
from django.utils import timezone
from .validators import validate_news_image_size



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120,unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name



class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60,unique=True)

    def __str__(self):
        return self.name



class News(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        PUBLISHED = "published", "Elon qilingan"
        ARCHIVED = "archived", "arxivlangan"


    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=250)
    body = models.TextField()
    image = models.ImageField(
        upload_to="news/",
        blank=True,
        null=True,
        validators=[validate_news_image_size],
    )


    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="news",
    )
    tags = models.ManyToManyField(Tag,blank=True, related_name="news")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="news",
    )


    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    is_featured = models.BooleanField(default=False)
    send_to_telegram = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        upload_to="news/gallery/",
        validators=[validate_news_image_size],
    )

    def __str__(self):
        return f"{self.news.title} - rasm"


class Banner(models.Model):
    title = models.CharField(max_length=150)
    image = models.ImageField(
        upload_to="banners/",
        validators=[validate_news_image_size],
    )
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title