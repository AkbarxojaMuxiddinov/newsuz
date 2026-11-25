from urllib.parse import urlencode
from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.db.models.sql import query


def send_subscription_confirmation(subscription):
    token = signing.dumps(
        {
            "subscription_id": subscription.pk,
            
            "email": subscription.email,
        },
        salt="subscription-confirmation",
    )

    query = urlencode({"token": token})
    link = (
        f"{settings.SITE_URL.rstrip('/')}"
        f"/api/subscriptions/confirm/?{query}"
    )
    unsubscribe_link = get_unsubscribe_link(subscription)
    send_mail(
        subject="Obunani tasdiqlash",
        message=(
            f"Obunani tasdiqlash uchun havolani oching:\n{link}\n\n"
            f"Obunadan chiqish:\n{unsubscribe_link}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscription.email],
    )

def get_unsubscribe_link(subscription):
    token = signing.dumps(
        {
            "subscription_id": subscription.pk,
            "email": subscription.email,
        },
        salt= "subscription-unsubscribe",
    )

    query = urlencode({"token": token})

    return (
        f"{settings.SITE_URL.rstrip('/')}"
        f"/api/subscriptions/unsubscribe/?{query}"
    )