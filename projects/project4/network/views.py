import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Page, Paginator
from django.core.serializers import serialize
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import CreatePostForm
from .models import Post, Profile, User


def pagination(request: HttpRequest):
    all_posts = Post.objects.all().order_by("-posted_at")

    paginator = Paginator(all_posts, 10)

    page_number = request.GET.get("page")

    posts_per_page: Page = paginator.get_page(page_number)

    return posts_per_page


@csrf_exempt
def index(request: HttpRequest):
    posts_per_page = pagination(request)

    return render(
        request,
        "network/index.html",
        {
            "request": request,
            "create_post_form": CreatePostForm(),
            "posts": posts_per_page,
        },
    )


@csrf_exempt
@login_required
def following(request: HttpRequest):
    followed_users = request.user.profile.following.all()  # type: ignore

    followed_users_posts = Post.objects.filter(user__in=followed_users).order_by(
        "-posted_at"
    )

    return render(request, "network/following.html", {"posts": followed_users_posts})


def profile(request: HttpRequest, username: str):
    if request.method != "GET":
        return JsonResponse({"error": "This endpoint only accepts GET."}, status=400)

    try:
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile not found."}, status=404)

    posts = Post.objects.filter(user=user).order_by("-posted_at")

    is_following = False

    if request.user.is_authenticated:
        is_following = profile.followers.filter(id=request.user.id).exists()  # type: ignore

    JsonResponse(
        {
            "message": f"You have gotten {user.username}'s profile.",
        },
        status=200,
    )

    return render(
        request,
        "network/profile.html",
        {
            "user": user,
            "profile": profile,
            "posts": posts,
            "is_following": is_following,
        },
    )


@csrf_exempt
@login_required
@require_http_methods(["POST", "DELETE"])
def follow(request: HttpRequest, username: str):
    profile = get_object_or_404(Profile, user__username=username)
    request_user_profile = get_object_or_404(Profile, user__username=request.user.username)  # type: ignore

    status_code = 201

    if request.method == "POST":
        request_user_profile.following.add(request.user)  # type: ignore
        profile.followers.add(request.user)  # type: ignore
    elif request.method == "DELETE":
        request_user_profile.following.remove(request.user)  # type: ignore
        profile.followers.remove(request.user)  # type: ignore
        status_code = 202

    return JsonResponse({"profile": serialize("json", [profile])}, status=status_code)


@csrf_exempt
@login_required
def create_post(request: HttpRequest):

    if request.method != "POST":
        return JsonResponse({"error": "This endpoint only accepts POST."}, status=400)

    data = json.loads(request.body)

    content = data.get("content")

    post = Post(user=request.user, content=content)

    post.save()

    return JsonResponse({"message": "The post has been made."}, status=201)


@csrf_exempt
@login_required
def update_post(request: HttpRequest, post_id: int):
    if request.method != "PUT":
        return JsonResponse({"error": "This endpoint only accepts PUT."}, status=400)

    data = json.loads(request.body)

    new_content = data.get("content")

    post = get_object_or_404(Post, pk=post_id)

    post.content = new_content

    post.save()

    return JsonResponse(
        {"message": "The post has been updated.", "new_content": new_content},
        status=201,
    )


@csrf_exempt
@login_required
def like(request: HttpRequest, post_id: int):
    if request.method != "POST":
        return JsonResponse({"error": "This endpoint only accepts POST."}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():  # type: ignore
        post.likes.remove(user)  # type: ignore
    else:
        post.likes.add(user)  # type: ignore

    like_count = post.likes.count()  # type: ignore

    return JsonResponse(
        {"message": "Successful execution.", "likes": like_count},
        status=201,
    )


def login_view(request: HttpRequest):
    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "You have given an invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


@login_required
def logout_view(request: HttpRequest):
    logout(request)

    return HttpResponseRedirect(reverse("network:index"))


def register(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")

        email = request.POST.get("email")

        password = request.POST.get("password")

        confirmation = request.POST.get("confirmation")

        if password != confirmation:
            return render(
                request,
                "network/register.html",
                {"message": "Both passwords must match."},
            )

        try:
            user = User.objects.create_user(username, email, password)  # type: ignore

            user.save()  # type: ignore
        except IntegrityError:
            return render(
                request,
                "network/register.html",
                {"message": "This username has already been taken."},
            )

        login(request, user)  # type: ignore

        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")
