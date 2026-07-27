#views.py file

from django.shortcuts import render, redirect
import cybermillionaire.export as e
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_report import generate_ai_feedback
from .mysql_db import get_or_create_user, save_topic_settings, get_topic_settings, create_game_session, save_game_results, get_user_results, get_available_topics, add_available_topic, get_game_results
import re

def require_login(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    return None

@csrf_exempt
def save_results(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return JsonResponse({"status":"error"})
    data = json.loads(request.body)
    user_id = request.session["user_id"]
    session_id = create_game_session(user_id,data.get("difficulty", "unknown"),data["finalMoney"])
    save_game_results(session_id,data["history"])
    return JsonResponse({"status":"success"})

def get_results(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    user_id = request.session["user_id"]
    results = get_user_results(user_id)
    return JsonResponse(results,safe=False)

@csrf_exempt
def save_topics(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
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
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    user_id = request.session["user_id"]
    results = get_user_results(user_id)
    feedback = generate_ai_feedback(results)
    return render(request, "feedback.html", {"feedback": feedback})

def ai_game_feedback(request, session_id):

    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response

    user_id = request.session["user_id"]
    game = get_game_results(session_id, user_id)
    if game is None:
        return redirect("/")

    feedback = generate_ai_feedback(game)
    return render(request,"feedback.html",{"feedback": feedback})

def topics(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    user_id = request.session["user_id"]
    settings = get_topic_settings(user_id)
    all_topics = get_available_topics()
    topics = {"easy": all_topics,"medium": all_topics,"hard": all_topics,"expert": all_topics}

    return render(request,"topics.html",{"settings": settings,"topics": topics})

def index(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    return render(request,"index.html",{"username": request.session["username"]})

def start_game(request, mode):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    e.export_questions(mode)
    return render(request, "game.html")
    
def start1(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("1")
    return render(request,"game.html",{"game_data": game_data})

def start2(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("2")
    return render(request,"game.html",{"game_data": game_data})

def start3(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("3")
    return render(request,"game.html",{"game_data": game_data})

def start4(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("4")
    return render(request,"game.html",{"game_data": game_data})

def dynamic_start1(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game = e.export_questions("dynamic-1",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def dynamic_start2(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game = e.export_questions("dynamic-2",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def dynamic_start3(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game = e.export_questions("dynamic-3",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def dynamic_start4(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game = e.export_questions("dynamic-4",request.session["user_id"])
    return render(request,"game.html",{"game_data": game})

def add_topic(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    if request.method == "POST":
        topic = request.POST.get("new_topic", "").strip()
        if not topic:
            return redirect("/topics/")
        if len(topic) > 100:
            return redirect("/topics/")
        if not re.match(r"^[a-zA-Z0-9\s\-/]+$", topic):
            return redirect("/topics/")
        add_available_topic(topic)

    return redirect("/topics/")

def login(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        if not username:
            return render(request, "login.html", {
                "error": "Please enter a username."
            })
        if len(username) > 50:
            return render(request, "login.html", {
                "error": "Username must be 50 characters or less."
            })
        if not re.match(r"^[a-zA-Z0-9_ ]+$", username):
            return render(request, "login.html", {
                "error": "Username can only contain letters, numbers, spaces, and underscores."
            })
        user_id = get_or_create_user(username)
        request.session["user_id"] = user_id
        request.session["username"] = username
        return redirect("/")
    return render(request,"login.html")

def logout(request):
    request.session.flush()
    return redirect("/login/")