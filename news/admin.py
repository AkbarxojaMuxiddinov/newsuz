from django.contrib import admin
from .models import Category, Tag, News,NewsImage,Banner
from functools import partial
from django.db import transaction
from telegram_integration.services import send_news_telegram

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    inlines = [NewsImageInline]
    list_display = ("title", "category", "status", "is_featured", "created_at")
    list_filter = ("status", "category", "is_featured")
    search_fields =  ("title", "short_description", "body")
    prepopulated_fields = {"slug": ("title",)}


    def save_model(self, request, obj, form, change):
        was_published = False

        if change:
            was_published = News.objects.filter(
                pk=obj.pk,
                status=News.Status.PUBLISHED,
            ).exists()

        super().save_model(request, obj, form, change)

        if (
                obj.status == News.Status.PUBLISHED
                and not was_published
                and obj.send_to_telegram
        ):
            transaction.on_commit(
                partial(send_news_telegram, obj)
            )

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)
