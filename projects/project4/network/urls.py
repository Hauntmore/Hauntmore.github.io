from django.urls import path

from . import views

app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("post/", view=views.create_post, name="create_post"),
    path("like/<int:post_id>/", views.like, name="like"),
    path("update_post/<int:post_id>/", views.update_post, name="update_post"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("follow/<str:username>/", views.follow, name="follow"),
    path("following/", views.following, name="following"),
]
