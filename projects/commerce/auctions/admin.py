from django.contrib import admin

from .models import AuctionListing, Bid, Comment, User

# Register your models here.


# User table - visible columns for admin view
class UserAdmin(admin.ModelAdmin):  # type: ignore

    list_display = (
        "id",
        "username",
        "email",
        "password",
        "watchlist_counter",
    )


class AuctionListingAdmin(admin.ModelAdmin):  # type: ignore

    list_display = (
        "id",
        "user",
        "title",
        "description",
        "category",
        "starting_bid",
        "image_url",
        "posted_at",
        "active",
        "bid_counter",
        "winner",
    )


class BidAdmin(admin.ModelAdmin):  # type: ignore

    list_display = ("auction", "user", "amount", "created_at")


class CommentAdmin(admin.ModelAdmin):  # type: ignore

    list_display = ("auction", "user", "text", "created_at")


admin.site.register(User, UserAdmin)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
