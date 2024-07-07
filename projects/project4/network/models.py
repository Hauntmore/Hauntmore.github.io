from typing import Any, Dict
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


class User(AbstractUser):
    id = models.AutoField(primary_key=True)


class Post(models.Model):
    id = models.AutoField(primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    content = models.CharField(max_length=500)

    posted_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, default=0, related_name="liked_posts")  # type: ignore

    objects = models.Manager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    followers = models.ManyToManyField(User, default=0, related_name="follower_user")  # type: ignore

    following = models.ManyToManyField(User, default=0, related_name="following_user")  # type: ignore


@receiver(post_save, sender=User)
def create_profile(
    sender: type, instance: User, created: bool, **_kwargs: Dict[str, Any]
):
    if created:
        Profile.objects.create(user=instance)
