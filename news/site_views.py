from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from engagement.models import Comment

from .models import Category, News


MONTHS = (
    "yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul",
    "avgust", "sentyabr", "oktabr", "noyabr", "dekabr",
)


def published_news():
    return News.objects.filter(status=News.Status.PUBLISHED).select_related(
        "category", "author"
    ).order_by(
        F("published_at").desc(nulls_last=True), "-created_at", "-pk"
    )


def page_context():
    today = timezone.localdate()
    return {
        "topics": Category.objects.filter(news__status=News.Status.PUBLISHED)
        .distinct().order_by("name"),
        "edition_date": f"{today.day} {MONTHS[today.month - 1]}, {today.year}",
    }


def home(request):
    search = request.GET.get("q", "").strip()[:150]
    topic = request.GET.get("category", "").strip()[:120]
    articles = published_news()
    if search:
        articles = articles.filter(
            Q(title__icontains=search)
            | Q(short_description__icontains=search)
            | Q(body__icontains=search)
        )
    if topic:
        articles = articles.filter(category__slug=topic)

    page = Paginator(articles, 9).get_page(request.GET.get("page"))
    archive = request.GET.get("view") == "all"
    show_hero = not archive and not search and not topic and page.number == 1
    featured = None
    latest = []
    if show_hero:
        featured = articles.filter(is_featured=True).first() or articles.first()
        if featured:
            latest = list(articles.exclude(pk=featured.pk)[:5])

    return render(request, "news/portal/home.html", {
        **page_context(),
        "search": search,
        "selected_topic": topic,
        "topic_title": Category.objects.filter(slug=topic).values_list("name", flat=True).first() if topic else "",
        "page_obj": page,
        "featured": featured,
        "latest": latest,
        "archive": archive,
        "timeline": articles[:6] if featured else [],
        "popular": articles.filter(view_count__gt=0).order_by(
            "-view_count", "-created_at", "-pk"
        )[:4] if featured else [],
    })


def article(request, slug):
    news = get_object_or_404(published_news().prefetch_related("images", "tags"), slug=slug)
    if request.method == "GET":
        News.objects.filter(pk=news.pk).update(view_count=F("view_count") + 1)
        news.refresh_from_db(fields=["view_count"])

    approved_comments = news.comments.filter(
        status=Comment.Status.APPROVED
    ).select_related("user").order_by("created_at", "pk")
    return render(request, "news/portal/article.html", {
        **page_context(),
        "article": news,
        "related": published_news().filter(category_id=news.category_id).exclude(pk=news.pk)[:3],
        "comment_page": Paginator(approved_comments, 20).get_page(request.GET.get("comments")),
        "comment_endpoint": reverse("comment-create", kwargs={"slug": slug}),
    })


def account(request, mode):
    return render(request, "news/portal/account.html", {
        **page_context(),
        "mode": mode,
        "next_path": request.GET.get("next", ""),
    })
