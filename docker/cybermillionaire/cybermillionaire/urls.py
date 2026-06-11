"""
urls.py

A single path captures the selection slug (e.g. "primary-school",
"dynamic-college") and maps it to the selection key expected by
export_questions().
"""

from django.conf.urls import url
from django.contrib import admin
from . import views

# Maps URL slug → export_questions() selection key
_SLUG_TO_SELECTION = {
    "primary-school":         "1",
    "secondary-school":       "2",
    "college":                "3",
    "expert":                 "4",
    "dynamic-primary-school": "dynamic-1",
    "dynamic-secondary-school": "dynamic-2",
    "dynamic-college":        "dynamic-3",
    "dynamic-expert":         "dynamic-4",
}

# Build named URL patterns from the mapping so {% url %} tags keep working
_game_patterns = [
    url(
        rf"^{slug}",
        lambda request, sel=selection: views.start_game(request, sel),
        name=slug,
    )
    for slug, selection in _SLUG_TO_SELECTION.items()
]

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    *_game_patterns,
    url(r"", views.index, name="start-page"),
]
