#views.py file

from django.shortcuts import render
import cybermillionaire.export as e


def index(request):
    return render(request, "index.html")


def start_game(request, selection):
    e.export_questions(selection)
    return render(request, "game.html")


def start1(request):  # Static Primary School Level
    return start_game(request, "1")


def start2(request):  # Static Secondary School Level
    return start_game(request, "2")


def start3(request):  # Static College Level
    return start_game(request, "3")


def start4(request):  # Static Expert Level
    return start_game(request, "4")


def dynamic_start1(request):  # Dynamic Primary School Level
    return start_game(request, "dynamic-1")


def dynamic_start2(request):  # Dynamic Secondary School Level
    return start_game(request, "dynamic-2")


def dynamic_start3(request):  # Dynamic College Level
    return start_game(request, "dynamic-3")


def dynamic_start4(request):  # Dynamic Expert Level
    return start_game(request, "dynamic-4")
