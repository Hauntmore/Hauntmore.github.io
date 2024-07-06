from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import CommentForm, CreateListingForm
from .models import CATEGORIES, AuctionListing, Bid, Comment, User


def index(request: HttpRequest):
    return render(
        request,
        "auctions/index.html",
        {
            "listings": AuctionListing.objects.filter(active=True)
            .order_by("-posted_at")
            .values()
        },
    )


def list_categories(request: HttpRequest):
    return render(request, "auctions/categories.html", {"categories": CATEGORIES})


def category(request: HttpRequest, category: str):
    listings = AuctionListing.objects.filter(category=category)

    return render(
        request,
        "auctions/category.html",
        {"listings": listings, "category": category},
    )


@login_required
def create(request: HttpRequest):
    if request.method == "POST":
        form = CreateListingForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]

            description = form.cleaned_data["description"]

            starting_bid = form.cleaned_data["starting_bid"]

            CATEGORIES_DICT = {
                "A": "Automotive",
                "B": "Health & Beauty",
                "C": "Collectibles & Art",
                "E": "Electronics",
                "F": "Fashion",
                "H": "Home & Garden",
                "I": "Business & Industrial",
                "M": "Movies, Music, & Books",
                "O": "Others",
                "P": "Pet",
                "R": "Real Estate",
                "S": "Sporting Goods",
                "T": "Toys & Games",
            }

            category = CATEGORIES_DICT.get(form.cleaned_data["category"])

            image_url = form.cleaned_data["image_url"]

            # Save a record.
            auction = AuctionListing(
                user=User.objects.get(pk=request.user.id),  # type: ignore
                title=title,
                description=description,
                starting_bid=starting_bid,
                category=category,
                image_url=image_url,
            )

            auction.save()

            bid = Bid(amount=starting_bid, user=request.user, auction=auction)
            bid.save()

            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            # If a field input is invalid.
            return render(request, "auctions/create.html", {"form": form})

    return render(request, "auctions/create.html", {"form": CreateListingForm()})


def listing(request: HttpRequest, id: int):
    try:
        listing = AuctionListing.objects.get(pk=id)

        bid = get_object_or_404(Bid, auction=listing)

        comments = Comment.objects.filter(auction=listing)

        if request.user.is_authenticated:
            user = get_object_or_404(User, id=request.user.id)  # type: ignore

            auction = get_object_or_404(AuctionListing, id=id)

            is_in_watchlist = user.watchlist.filter(id=auction.id).exists()  # type: ignore

            if is_in_watchlist:
                on_watchlist = True
            else:
                on_watchlist = False
        else:
            on_watchlist = False

        return render(
            request,
            "auctions/listing.html",
            {
                "listing": listing,
                "on_watchlist": on_watchlist,
                "request": request,
                "bid": bid,
                "comments": comments,
                "comment_form": CommentForm(),
            },
        )
    except AuctionListing.DoesNotExist:
        return render(
            request,
            "auctions/listing.html",
            {
                "code": 404,
                "message": "That auction doesn't exist!",
            },
        )


@login_required(login_url="auctions/login.html")
def watchlist(request: HttpRequest):
    return render(
        request, "auctions/watchlist.html", {"watchlist": request.user.watchlist.all()}  # type: ignore
    )


@login_required(login_url="auctions/login.html")
def watch(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(AuctionListing, id=auction_id)

    request.user.watchlist.add(auction)  # type: ignore

    request.user.watchlist_counter += 1  # type: ignore

    request.user.save()

    render(
        request, "auctions/watchlist.html", {"watchlist": request.user.watchlist.all()}  # type: ignore
    )

    return HttpResponseRedirect(reverse("auctions:watchlist"))


@login_required(login_url="auctions/login.html")
def unwatch(request: HttpRequest, auction_id: int):
    auction = get_object_or_404(AuctionListing, id=auction_id)

    request.user.watchlist.remove(auction)  # type: ignore

    request.user.watchlist_counter -= 1  # type: ignore

    render(
        request, "auctions/watchlist.html", {"watchlist": request.user.watchlist.all()}  # type: ignore
    )

    return HttpResponseRedirect(reverse("auctions:watchlist"))


@login_required(login_url="auctions/login.html")
def update_bid(request: HttpRequest, id: int):
    amount = request.POST["bid"]  # type: ignore

    if amount:
        amount = float(amount)  # type: ignore
        auction = get_object_or_404(AuctionListing, id=id)
        if amount > get_object_or_404(Bid, id=id).amount:
            bid = get_object_or_404(Bid, id=id)
            bid.user, bid.amount = request.user, amount  # type: ignore
            bid.save()
            auction.bid_counter += 1  # type: ignore
            auction.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            raise ValidationError("Bid must be greater than current Bid value")
    else:
        raise ValidationError("Bid must be greater than current Bid value")


@login_required
def close_bid(request: HttpRequest, id: int):
    auction = get_object_or_404(AuctionListing, id=id)
    auction.active, auction.winner = False, request.user.username  # type: ignore
    auction.save()
    return HttpResponseRedirect(reverse("auctions:index"))


@login_required  # type: ignore
def comments(request: HttpRequest, id: int):
    anonymous = User.first_name
    if request.user is not anonymous:
        form = CommentForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            comment = Comment(
                user=request.user, auction=get_object_or_404(AuctionListing, id=id), **f
            )
            comment.save()
            return HttpResponseRedirect(reverse("auctions:listing", kwargs={"id": id}))
    else:
        return render(
            request,
            "auctions/login.html",
            {"message": "Must be logged in to be able to comment!"},
        )


def login_view(request: HttpRequest):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]  # type: ignore

        password = request.POST["password"]  # type: ignore

        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def register(request: HttpRequest):
    if request.method == "POST":
        username = request.POST["username"]  # type: ignore
        email = request.POST["email"]  # type: ignore

        # Ensure password matches confirmation
        password = request.POST["password"]  # type: ignore
        confirmation = request.POST["confirmation"]  # type: ignore

        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)  # type: ignore
            user.save()  # type: ignore
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)  # type: ignore
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")
