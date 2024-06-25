from random import randint

from django.http import HttpRequest
from django.shortcuts import redirect, render
from markdown2 import markdown  # type: ignore

from . import util


def index(request: HttpRequest):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request: HttpRequest, title: str):
    content = util.get_entry(title.strip())

    if content is None:
        content = "## Page was not found!"

    content = markdown(content)  # type: ignore

    return render(
        request, "encyclopedia/entry.html", {"content": content, "title": title}
    )


def search(request: HttpRequest):
    query = request.GET.get("search_query")

    if query is not None:
        query = query.strip()

        if query in util.list_entries():
            return redirect("encyclopedia:entry", title=query)
        return render(
            request,
            "encyclopedia/search.html",
            {"entries": util.search(query), "search_query": query},
        )

    return query


def edit(request: HttpRequest, title: str):
    content = util.get_entry(title.strip())

    if content is None:
        return render(request, "encyclopedia/edit.html", {"error": "404 Not Found"})

    if request.method == "POST":
        content = request.POST.get("content")

        if content is not None:
            content = content.strip()
        if not content:
            return render(
                request,
                "encyclopedia/edit.html",
                {
                    "message": "Cannot save with an empty field.",
                    "title": title,
                    "content": content,
                },
            )

        util.save_entry(title, content)

        return redirect("encyclopedia:entry", title=title)

    return render(
        request, "encyclopedia/edit.html", {"content": content, "title": title}
    )


def create(request: HttpRequest):
    if request.method == "POST":
        title = request.POST.get("title")

        if title is not None:
            title.strip()

        content = request.POST.get("content")

        if content is not None:
            content.strip()

        if not title or not content:
            return render(
                request,
                "encyclopedia/add.html",
                {
                    "message": "Cannot save with an empty field.",
                    "title": title,
                    "content": content,
                },
            )

        if title in util.list_entries():
            return render(
                request,
                "encyclopedia/add.html",
                {
                    "message": "This title already exists. Try another one!",
                    "title": title,
                    "content": content,
                },
            )

        util.save_entry(title, content)

        return redirect("encyclopedia:entry", title=title)

    return render(request, "encyclopedia/add.html")


def random_page(_request: HttpRequest):
    entries = util.list_entries()

    random_title = entries[randint(0, len(entries) - 1)]

    return redirect("encyclopedia:entry", title=random_title)
