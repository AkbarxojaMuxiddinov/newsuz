from django.db import models
from string import Formatter
from django.core.exceptions import ValidationError

class TelegramLog(models.Model):
    class Status(models.TextChoices):
        SENT = ('sent', 'Yuborildi')
        ERROR = ('error', 'Xato')
        RETRY = ('retry', 'Qayta urinish')

    news = models.ForeignKey(
        'news.News',
        on_delete=models.CASCADE,
        related_name='telegram_log',
    )
    channel_id = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=Status.choices)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.news.title} - {self.status}"

class TelegramSettings(models.Model):
    channel_id = models.CharField(max_length=100,help_text="@kanal_username yoki raqamli kanal ID")
    auto_send = models.BooleanField(default=True)

    def clean(self):
        super().clean()

        try:
            parts = list(Formatter().parse(self.post_template))
        except ValueError:
            raise ValidationError({
                "post_template": "Formatdagi qavslar notogri yozilgan"
            })

        for text, field, format_spec, conversion in parts:
            if field is None:
                continue

            if (
                field not in {"title", "description", "url"}
                or format_spec
                or conversion
            ):
                raise ValidationError({
                    "post_template":
                        "Faqat {title}, {description}, {url} ishlating"
                })

    def __str__(self):
        return "Telgram sozlamalari"

    post_template = models.TextField(
        default=(
            "{title}\n\n"
            "{description}\n\n"
            "Batafsil o'qish: {url}"
        ),
        help_text="Mavjud belgilar: {title}, {description}, {url}",
    )