from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [  # type: ignore
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create, name="create"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watch/<int:auction_id>", views.watch, name="watch"),
    path("unwatch/<int:auction_id>", views.unwatch, name="unwatch"),
    path("categories/", views.list_categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("update-bid/<int:id>", views.update_bid, name="update_bid"),
    path("close-bid/<int:id>", views.close_bid, name="close_bid"),
    path("comments/<int:id>", views.comments, name="comments"),  # type: ignore
]
