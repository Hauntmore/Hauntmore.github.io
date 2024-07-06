import re
from decimal import Decimal

from django import forms

from .models import CATEGORIES, AuctionListing


def parse(value: str):
    value = re.sub(r"\s+", "", value)

    value = value.replace("$", "")

    value = value.replace(",", "")

    return Decimal(value)


class CustomDecimalField(forms.DecimalField):
    def clean(self, value: str):
        parsed = parse(value)

        return super().clean(parsed)


class CreateListingForm(forms.ModelForm):
    title = forms.CharField(
        label="Listing Title",
        max_length=150,
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "The listing title.",
            }
        ),
    )

    description = forms.CharField(
        label="Listing Description",
        max_length=1000,
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Give a detailed description about the listing.",
            }
        ),
    )

    starting_bid = CustomDecimalField(
        label="Starting Bid",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Provide the starting bid for this listing (e.g. 23987.99, $1,456.90, or 1450).",
            }
        ),
        max_digits=12,
        decimal_places=2,
    )

    image_url = forms.URLField(
        label="Image URL",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Optional (Recommended): Provide an image link of the producted being listed so potential buyers are able to see the item.",
            }
        ),
    )

    category = forms.ChoiceField(
        required=False,
        choices=CATEGORIES,
    )

    class Meta:
        model = AuctionListing
        fields = ["title", "description", "starting_bid", "image_url", "category"]


class CommentForm(forms.Form):
    text = forms.CharField(
        label="",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control-md lead form-group",
                "rows": "3",
                "cols": "100",
            }
        ),
    )

    def clean_comment(self):
        text = self.cleaned_data.get("text")
        if len(text) > 0:  # type: ignore
            return text
        return self.errors
