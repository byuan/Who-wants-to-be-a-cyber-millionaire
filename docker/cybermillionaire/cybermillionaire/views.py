#views.py file

from django.shortcuts import render, redirect
import cybermillionaire.export as e
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .ai_report import generate_ai_feedback
from .mysql_db import get_or_create_user, save_topic_settings, get_topic_settings, create_game_session, save_game_results, get_user_results, get_available_topics, add_available_topic, get_game_results
from .question_queue import start_question_generation, get_questions, pop_questions, generate_initial_questions, stop_question_generation
import re
from django.contrib.auth.hashers import make_password, check_password

def require_login(request):
    if "user_id" not in request.session:
        return redirect("/login/")
    return None

def save_results(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return JsonResponse({"status":"error"}, status=405)
    try:
        data = json.loads(request.body)
        if not isinstance(data, dict):
            raise ValueError("Expected an object")
        history = data.get("history")
        score = data.get("finalMoney")
        difficulty = data.get("difficulty", "unknown")
        if type(score) is not int or not 0 <= score <= 1000000:
            raise ValueError("Invalid score")
        if not isinstance(difficulty, str) or len(difficulty) > 20:
            raise ValueError("Invalid difficulty")
        if not isinstance(history, list) or not 1 <= len(history) <= 200:
            raise ValueError("Invalid history")
        for item in history:
            if not isinstance(item, dict):
                raise ValueError("Invalid answer")
            for field in ("question", "selected", "correct"):
                if not isinstance(item.get(field), str) or not 1 <= len(item[field]) <= 10000:
                    raise ValueError("Invalid answer text")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"status": "error", "message": "Invalid game results"}, status=400)
    user_id = request.session["user_id"]
    session_id = create_game_session(user_id,data.get("difficulty", "unknown"),data["finalMoney"])
    save_game_results(session_id,data["history"])
    stop_question_generation(user_id)
    return JsonResponse({"status":"success"})

def get_results(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    user_id = request.session["user_id"]
    results = get_user_results(user_id)
    return JsonResponse(results,safe=False)

def save_topics(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    if request.method != "POST":
        return JsonResponse({"status": "invalid request"}, status=405)
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
    
@ensure_csrf_cookie
def start1(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("1")
    return render(request,"game.html",{"game_data": game_data})

@ensure_csrf_cookie
def start2(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("2")
    return render(request,"game.html",{"game_data": game_data})

@ensure_csrf_cookie
def start3(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("3")
    return render(request,"game.html",{"game_data": game_data})

@ensure_csrf_cookie
def start4(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    game_data = e.export_questions("4")
    return render(request,"game.html",{"game_data": game_data})

@ensure_csrf_cookie
def dynamic_start1(request):
    redirect_response = require_login(request)

    if redirect_response:
        return redirect_response

    user_id = request.session["user_id"]

    initial_questions = generate_initial_questions(
        "easy",
        user_id,
        5
    )

    start_question_generation(
        "easy",
        user_id
    )

    game_data = {
        "games": [
            {
                "questions": initial_questions
            }
        ]
    }

    return render(
        request,
        "game.html",
        {"game_data": game_data}
    )


@ensure_csrf_cookie
def dynamic_start2(request):
    redirect_response = require_login(request)

    if redirect_response:
        return redirect_response

    user_id = request.session["user_id"]

    initial_questions = generate_initial_questions(
        "medium",
        user_id,
        5
    )

    start_question_generation(
        "medium",
        user_id
    )

    game_data = {
        "games": [
            {
                "questions": initial_questions
            }
        ]
    }

    return render(
        request,
        "game.html",
        {"game_data": game_data}
    )

@ensure_csrf_cookie
def dynamic_start3(request):
    redirect_response = require_login(request)

    if redirect_response:
        return redirect_response

    user_id = request.session["user_id"]

    # Generate first 5 questions concurrently
    initial_questions = generate_initial_questions(
        "hard",
        user_id,
        5
    )

    # Start background generator for future questions
    start_question_generation(
        "hard",
        user_id
    )

    game_data = {
        "games": [
            {
                "questions": initial_questions
            }
        ]
    }

    return render(
        request,
        "game.html",
        {"game_data": game_data}
    )


@ensure_csrf_cookie
def dynamic_start4(request):
    redirect_response = require_login(request)

    if redirect_response:
        return redirect_response

    user_id = request.session["user_id"]

    initial_questions = generate_initial_questions(
        "expert",
        user_id,
        5
    )

    start_question_generation(
        "expert",
        user_id
    )

    game_data = {
        "games": [
            {
                "questions": initial_questions
            }
        ]
    }

    return render(
        request,
        "game.html",
        {"game_data": game_data}
    )

def get_question_queue(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    user_id = request.session["user_id"]
    questions = get_questions(user_id)
    return JsonResponse(
        questions,
        safe=False
    )

def get_new_questions(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response
    user_id = request.session["user_id"]
    questions = pop_questions(user_id, 5)
    print("Sending questions:", len(questions))
    return JsonResponse(questions,safe=False)

def add_topic(request):
    redirect_response = require_login(request)
    if redirect_response:
        return redirect_response

    if not request.session.get("is_admin", False):
        return redirect("/topics/")

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
        username = request.POST.get("username", "").strip()
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
        password = request.POST.get("password")
        if not password:
            return render(request, "login.html", {
                "error": "Please enter a password."
            })

        result = get_or_create_user(username, password)
        if result is None:
            return render(request, "login.html", {
                "error": "Invalid username or password."
            })

        user_id, is_admin = result
        request.session.cycle_key()
        request.session["user_id"] = user_id
        request.session["username"] = username
        request.session["is_admin"] = is_admin
        return redirect("/")
    return render(request,"login.html")

def logout(request):
    stop_question_generation(request.session.get("user_id"))
    request.session.flush()
    return redirect("/login/")