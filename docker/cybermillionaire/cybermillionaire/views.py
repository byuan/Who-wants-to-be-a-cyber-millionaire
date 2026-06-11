"""
views.py

All eight game-start views share identical logic: call export_questions()
with a selection key, then render game.html. A single parameterised view
replaces the original eight.
"""

from django.shortcuts import HttpResponse
from django import template
import cybermillionaire.export as e


def index(request):
    t = template.loader.get_template("index.html")
    return HttpResponse(t.render())


def start_game(request, selection: str):
    """Generic view for every difficulty / mode combination."""
    e.export_questions(selection)
    t = template.loader.get_template("game.html")
    return HttpResponse(t.render())
