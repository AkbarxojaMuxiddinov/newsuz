from django.urls import path

from . import site_views

app_name = "portal"

urlpatterns = [
    path("", site_views.home, name="home"),
    path("yangilik/<slug:slug>/", site_views.article, name="article"),
    path("kirish/", site_views.account, {"mode": "login"}, name="login"),
    path("royxatdan-otish/", site_views.account, {"mode": "register"}, name="register"),
]
