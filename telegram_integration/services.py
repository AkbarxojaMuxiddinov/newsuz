import json
from urllib.request import Request, urlopen
from django.conf import settings
from urllib.error import URLError,HTTPError
from .models import TelegramLog,TelegramSettings
from django.utils import timezone
from django.urls import reverse
import requests


def send_telegram_message(text, channel_id=None):
    token = settings.TELEGRAM_BOT_TOKEN
    channel_id = channel_id or settings.TELEGRAM_CHANNEL_ID

    if not token or not channel_id:
        raise ValueError("Telgram token yoki kanal sozlanmagan ! ")

    data = json.dumps({
        "chat_id": channel_id,
        "text": text
    }).encode("utf-8")

    request = Request(
        url = f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=10) as response:
        result = json.load(response)

    return result["result"]


def send_news_telegram(news):
    telegram_settings = TelegramSettings.objects.first()

    if telegram_settings is None or not telegram_settings.auto_send:
        return

    channel_id = telegram_settings.channel_id

    article_path = reverse("portal:article", kwargs={"slug": news.slug})
    url = f"{settings.SITE_URL.rstrip('/')}{article_path}"

    text = telegram_settings.post_template.format(
        title=news.title,
        description=news.short_description,
        url=url,
    )

    try:
        if news.image:
            send_telegram_photo(news.image, text, channel_id=channel_id)

        else:
            send_telegram_message(text, channel_id=channel_id)

    except HTTPError as error:
        TelegramLog.objects.create(
            news=news,
            channel_id=channel_id,
            status=TelegramLog.Status.ERROR,
            error_message=f"Telegram HTTP xatosi: {error.code}"

        )

    except requests.exceptions.HTTPError as error:
        TelegramLog.objects.create(
            news=news,
            channel_id=channel_id,
            status=TelegramLog.Status.ERROR,
            error_message=f"Telegram HTTP xatosi: {error.response.status_code}",
        )
    except(URLError, TimeoutError,OSError, requests.RequestException):
        TelegramLog.objects.create(
            news=news,
            channel_id=channel_id,
            status=TelegramLog.Status.ERROR,
            error_message="Rasmni o'qish yoki Telegramga ulanishda xato.",
        )

    else:
        TelegramLog.objects.create(
            news=news,
            channel_id=channel_id,
            status=TelegramLog.Status.SENT,
            sent_at=timezone.now(),
        )




def send_telegram_photo(image, caption, channel_id=None):
    token = settings.TELEGRAM_BOT_TOKEN
    channel_id = channel_id or settings.TELEGRAM_CHANNEL_ID

    if not token or not channel_id:
        raise ValueError("Telegram token yoki kanal sozlanmagan")

    with image.open("rb") as photo:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendPhoto",
            data={
                "chat_id": channel_id,
                "caption": caption,
            },
            files={"photo": photo},
            timeout=30,

        )
    response.raise_for_status()
    return response.json()["result"]

