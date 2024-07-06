from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORIES = [
    ("A", "Automotive"),
    ("B", "Health & Beauty"),
    ("C", "Collectibles & Art"),
    ("E", "Electronics"),
    ("F", "Fashion"),
    ("H", "Home & Garden"),
    ("I", "Business & Industrial"),
    ("M", "Movies, Music, & Books"),
    ("O", "Others"),
    ("P", "Pet"),
    ("R", "Real Estate"),
    ("S", "Sporting Goods"),
    ("T", "Toys & Games"),
]


class User(AbstractUser):
    watchlist_counter = models.IntegerField(default=0, blank=True)
    watchlist = models.ManyToManyField(  # type: ignore
        "AuctionListing", related_name="watchlist", blank=True
    )

    pass


class AuctionListing(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=150)

    description = models.CharField(max_length=1000)

    starting_bid = models.DecimalField(max_digits=12, decimal_places=2, blank=True)

    image_url = models.URLField(
        blank=True,
        default="https://cdn2.thecatapi.com/images/MTY3ODIyMQ.jpg",
    )

    category = models.CharField(max_length=1, blank=True, null=True, choices=CATEGORIES)

    posted_at = models.DateTimeField(auto_now_add=True)

    active = models.BooleanField(default=True)

    bid_counter = models.IntegerField(default=1)

    winner = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"[{self.id}] {self.title}: by {self.user.username} - {self.posted_at}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} was bidded on {self.auction} by {self.user.username} for {self.auction.title} posted by {self.auction.user}."


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} commented on {self.auction.title} by {self.auction.user}: {self.text}"
