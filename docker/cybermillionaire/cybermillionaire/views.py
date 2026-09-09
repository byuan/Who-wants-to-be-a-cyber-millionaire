"""HTTP views for accounts, quizzes, topic preferences, and reports."""

from django.shortcuts import render, redirect
import cybermillionaire.export as e
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .ai_report import generate_ai_feedback
from .mysql_db import get_or_create_user, save_topic_settings, get_topic_settings, create_game_session, save_game_results, get_user_results, get_available_topics, add_available_topic, get_game_results
from .question_queue import start_question_generation, get_questions, pop_questions, generate_initial_questions, stop_question_generation
import re
from functools import wraps
from .mysql_db import DIFFICULTIES

def login_required(view):
    """Protect views using the application's existing session-based login."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if "user_id" not in request.session:
            return redirect("/login/")
        return view(request, *args, **kwargs)
    return wrapped


@login_required
def save_results(request):
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

@login_required
def get_results(request):
    user_id = request.session["user_id"]
    results = get_user_results(user_id)
    return JsonResponse(results,safe=False)

@login_required
def save_topics(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid request"}, status=405)
    user_id = request.session["user_id"]
    settings = {
        difficulty: request.POST.getlist(difficulty + "_topics")
        for difficulty in DIFFICULTIES
    }
    save_topic_settings(user_id, settings)
    return index(request)
    
@login_required
def ai_feedback(request):
    user_id = request.session["user_id"]
    results = get_user_results(user_id)
    feedback = generate_ai_feedback(results)
    return render(request, "feedback.html", {"feedback": feedback})

@login_required
def ai_game_feedback(request, session_id):

    user_id = request.session["user_id"]
    game = get_game_results(session_id, user_id)
    if game is None:
        return redirect("/")

    feedback = generate_ai_feedback(game)
    return render(request,"feedback.html",{"feedback": feedback})

@login_required
def topics(request):
    user_id = request.session["user_id"]
    settings = get_topic_settings(user_id)
    all_topics = get_available_topics()
    labels = ("Primary School", "Secondary School", "College", "Expert")
    groups = [
        {"key": difficulty, "label": label, "selected": settings[difficulty]}
        for difficulty, label in zip(DIFFICULTIES, labels)
    ]
    return render(request, "topics.html", {"groups": groups, "all_topics": all_topics})

@login_required
def index(request):
    return render(request,"index.html",{"username": request.session["username"]})

@ensure_csrf_cookie
@login_required
def start_game(request, level):
    game_data = e.export_questions(level)
    return render(request, "game.html", {"game_data": game_data})


@ensure_csrf_cookie
@login_required
def start_dynamic_game(request, level):
    user_id = request.session["user_id"]
    questions = generate_initial_questions(level, user_id, 5)
    start_question_generation(level, user_id)
    game_data = {"games": [{"questions": questions}]}
    return render(request, "game.html", {"game_data": game_data})


@login_required
def get_question_queue(request):
    user_id = request.session["user_id"]
    questions = get_questions(user_id)
    return JsonResponse(
        questions,
        safe=False
    )

@login_required
def get_new_questions(request):
    user_id = request.session["user_id"]
    questions = pop_questions(user_id, 5)
    print("Sending questions:", len(questions))
    return JsonResponse(questions,safe=False)

@login_required
def add_topic(request):

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