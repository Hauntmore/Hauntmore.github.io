from django import forms

from .models import Post


class CreatePostForm(forms.ModelForm):
    content = forms.CharField(
        label="New Post",
        max_length=500,
        required=True,
        widget=forms.Textarea(
            attrs={
                "placeholder": "What is on your mind right now?",
                "autofocus": "autofocus",
                "class": "form-control",
                "rows": "3",
            }
        ),
    )

    class Meta:
        model = Post
        fields = ["content"]
