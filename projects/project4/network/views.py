from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User

User = get_user_model()


def index(request: HttpRequest):
    return render(request, "network/index.html")


def create_post(request: HttpRequest):
    return render(
        request, "network/create_post.html", {"create_post_form": CreatePostForm()}
    )


def login_view(request: HttpRequest):
    if request.method == "POST":

        username = request.POST.get("username", None)

        password = request.POST.get("password", None)

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


def logout_view(request: HttpRequest):
    logout(request)

    return HttpResponseRedirect(reverse("network:index"))


def register(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username", None)

        email = request.POST.get("email", None)

        password = request.POST.get("password", None)

        confirmation = request.POST.get("confirmation", None)

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
