from django.contrib import admin

from .models import Comment, Subscription

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("news", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("text", "user__username", "news__title")

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
    readonly_fields = ("created_at",)