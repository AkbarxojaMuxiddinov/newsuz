from django.urls import path
from .views import NewsListAPIView, NewsDetailAPIView
from engagement.views import CommentCreateAPIView

urlpatterns = [
    path('', NewsListAPIView.as_view(), name='news_list' ),
    path("<slug:slug>/", NewsDetailAPIView.as_view(), name='news_detail' ),
    path("<slug:slug>/comments/", CommentCreateAPIView.as_view(), name="comment-create"),

]