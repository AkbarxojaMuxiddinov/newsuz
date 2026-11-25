"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from engagement.views import SavedNewsDeleteAPIView, SavedNewsListCreateAPIView, SubscriptionRequestSerializer, \
SubscriptionRequestAPIView
from django.conf import settings
from django.conf.urls.static import static
from news.views import BannerListAPIView
from engagement.views import SubscriptionConfirmAPIView, SubscriptionUnsubscribeAPIView

urlpatterns = [
    path("", include("news.site_urls")),
    path('admin/', admin.site.urls),
    path("api/news/", include('news.urls')),
    path("api/accounts/", include('accounts.urls')),
    path("api/saved-news/<int:pk>/", SavedNewsDeleteAPIView.as_view(), name="saved-news-delete"),
    path(
    "api/saved-news/",
    SavedNewsListCreateAPIView.as_view(),
    name="saved-news",
),  path("api/banners/", BannerListAPIView.as_view(), name="banner-list"),
    path("api/subscriptions/",SubscriptionRequestAPIView.as_view(), name="subscription-request"),
    path("api/subscriptions/confirm/",SubscriptionConfirmAPIView.as_view(), name="subscription-confirm"),
    path("api/subscriptions/unsubscribe/",SubscriptionUnsubscribeAPIView.as_view(), name="subscription-unsubscribe"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
