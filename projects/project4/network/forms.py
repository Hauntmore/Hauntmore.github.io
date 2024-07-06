from django import forms


class CreatePostForm(forms.Form):
    user =
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea)
