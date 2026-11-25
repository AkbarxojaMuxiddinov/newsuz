from django.contrib import admin

from .models import TelegramLog, TelegramSettings
from urllib.error import HTTPError,URLError
from .services import send_telegram_message,send_news_telegram


@admin.register(TelegramLog)
class TelegramLogAdmin(admin.ModelAdmin):
    list_display =("news", "channel_id", "status", "sent_at")
    list_filter = ("status",)
    search_fields = ("news__title", "channel_id")

    readonly_fields = (
        "news",
        "channel_id",
        "status",
        "error_message",
        "sent_at",
    )

    def has_add_permission(self, request):
        return False

    actions = ["retry_failed"]

    @admin.action(description="Xatoli yangiliklarni qayta yuborish")
    def retry_failed(self, request, queryset):
        telegram_settings = TelegramSettings.objects.first()

        if telegram_settings is None or not telegram_settings.auto_send:
            self.message_user(
                request,
                "Avval Telegram sozlamalarida Auto send belgisini yoqing",
                level="WARNING",
            )
            return

        logs = queryset.filter(
            status=TelegramLog.Status.ERROR,
            news__status="published",
        ).select_related("news")

        attempted_news = set()

        for log in logs:
            if log.news_id in attempted_news:
                continue

            attempted_news.add(log.news_id)
            send_news_telegram(log.news)

        self.message_user(
            request,
            f"{len(attempted_news)} ta yangilik uchun qayta urinish bajarildi"
            "Natijani Telegram jurnalidan tekshiring",
        )

@admin.register(TelegramSettings)
class TelegramSettingsAdmin(admin.ModelAdmin):
    actions = ["send_test_message"]
    list_display = ("channel_id", "auto_send")

    def has_add_permission(self, request):
        return (
            super().has_add_permission(request)
            and not TelegramSettings.objects.exists()
        )

    @admin.action(description="Telgramga sinov xabar yuborish")
    def send_test_message(self, request, queryset):
        telegram_settings = queryset.first()

        if telegram_settings is None:
            return

        try:
            send_telegram_message(
                "Telegram ulanishi ishlayapti",
                channel_id=telegram_settings.channel_id,
            )

        except (HTTPError, URLError, TimeoutError, ValueError):
            self.message_user(
                request,
                "Xabar yuborilmadi. Token kanal va bot huqularini tekshiring",
                level="ERROR",
            )
        else:
            self.message_user(
                request,
                "Sinov xabari Telgrmaga yuborildi",
                level="SUCCESS",
            )