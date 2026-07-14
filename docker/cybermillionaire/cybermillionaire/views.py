#views.py file

from django.shortcuts import HttpResponse, render, redirect
import cybermillionaire.export as e
import json
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_report import generate_ai_feedback
from .mysql_db import get_or_create_user, save_topic_settings, get_topic_settings, create_game_session, save_game_results, get_user_results

@csrf_exempt
def save_results(request):

    if request.method != "POST":
        return JsonResponse({"status":"error"})

    data = json.loads(request.body)
    user_id = request.session["user_id"]
    session_id = create_game_session(
        user_id,
        data.get("difficulty", "unknown"),
        data["finalMoney"]
    )

    save_game_results(
        session_id,
        data["history"]
    )

    return JsonResponse({"status":"success"})

def get_results(request):
    user_id = request.session["user_id"]
    results = get_user_results(user_id)
    return JsonResponse(results,safe=False)

@csrf_exempt
def save_topics(request):

    if request.method != "POST":
        return JsonResponse({"status": "invalid request"})

    user_id = request.session["user_id"]

    settings = {
        "easy": request.POST.getlist("easy_topics"),
        "medium": request.POST.getlist("medium_topics"),
        "hard": request.POST.getlist("hard_topics"),
        "expert": request.POST.getlist("expert_topics")
    }
    save_topic_settings(user_id, settings)
    return index(request)
    
def ai_feedback(request):
    feedback = generate_ai_feedback("results.json")
    return render(request, "feedback.html", {
        "feedback": feedback
    })

def topics(request):
    user_id = request.session["user_id"]
    settings = get_topic_settings(user_id)
    return render(request,"topics.html",{"settings": settings})

def index(request):
    if "user_id" not in request.session:
        return render(request,"login.html")
    return render(request,"index.html",{"username": request.session["username"]})

def start_game(request, mode):
    e.export_questions(mode)
    return render(request, "game.html")
    
def start1(request):
    game_data = e.export_questions("1")
    return render(request,"game.html",{"game_data": game_data})

def start2(request):
    game_data = e.export_questions("2")
    return render(request,"game.html",{"game_data": game_data})

def start3(request):
    game_data = e.export_questions("3")
    return render(request,"game.html",{"game_data": game_data})

def start4(request):
    game_data = e.export_questions("4")
    return render(request,"game.html",{"game_data": game_data})

def dynamic_start1(request):
    game = e.export_questions("dynamic-1",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def dynamic_start2(request):
    game = e.export_questions("dynamic-2",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def dynamic_start3(request):
    game = e.export_questions("dynamic-3",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def dynamic_start4(request):
    game = e.export_questions("dynamic-4",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def login(request):

    if request.method == "POST":

        username = request.POST.get("username").strip()
        user_id = get_or_create_user(
            username
        )
        request.session["user_id"] = user_id
        request.session["username"] = username
        return redirect("/")

    return render(
        request,
        "login.html"
    )