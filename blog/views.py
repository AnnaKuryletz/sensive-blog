from django.shortcuts import render, get_object_or_404
from blog.models import Post, Tag
from django.db.models import Count


def serialize_post(post):
    comments_count = getattr(post, "comments_count", 0)
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in post.tags.all()],
        "first_tag_title": post.tags.first().title if post.tags.exists() else None,
    }


def serialize_tag(tag):
    return {
        "title": tag.title,
        "posts_with_tag": getattr(tag, "posts_count", 0),
    }


def index(request):

    most_popular_posts = (
        Post.objects.popular()
        .select_related("author")
        .prefetch_related("tags", "comments")[:5]
    )

    most_fresh_posts = (
        Post.objects.prefetch_related("author", "tags")
        .annotate(comments_count=Count("comments"))
        .order_by("-published_at")[:5]
    )

    most_popular_tags = Tag.objects.popular().annotate(posts_count=Count("posts"))[:5]

    context = {
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
        "page_posts": [serialize_post(post) for post in most_fresh_posts],
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.annotate(likes_count=Count("likes")), slug=slug
    )
    comments = post.comments.select_related("author")
    serialized_comments = []
    serialized_comments = [
        {
            "text": comment.text,
            "published_at": comment.published_at,
            "author": comment.author.username,
        }
        for comment in comments
    ]

    related_tags = post.tags.all()
    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": serialized_comments,
        "likes_amount": post.likes.count(),
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = Tag.objects.popular().annotate(posts_count=Count("posts"))[:5]

    most_popular_posts = Post.objects.popular().prefetch_related(
        "author", "tags", "comments"
    )[:5]

    context = {
        "post": serialized_post,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):

    tag = get_object_or_404(Tag, title=tag_title)
    most_popular_tags = Tag.objects.popular().annotate(posts_count=Count("posts"))[:5]
    most_popular_posts = Post.objects.popular().prefetch_related(
        "author", "tags", "comments"
    )[:5]

    related_posts = (
        tag.posts.select_related("author")
        .prefetch_related("comments", "tags")
        .annotate(comments_count=Count("comments"))[:20]
    )

    context = {
        "tag": tag.title,
        "popular_tags": [serialize_tag(tag) for tag in most_popular_tags],
        "posts": [serialize_post(post) for post in related_posts],
        "most_popular_posts": [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, "contacts.html", {})
