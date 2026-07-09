#views.py file

from django.shortcuts import HttpResponse
from django.shortcuts import render
import cybermillionaire.export as e
import json
import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .ai_report import generate_ai_feedback

@csrf_exempt
def save_results(request):
    if request.method == "POST":

        data = json.loads(request.body)
        filename = "results.json"

        if os.path.exists(filename):
            with open(filename, "r") as f:
                results = json.load(f)
        else:
            results = []

        results.append({
            "played_at": datetime.now().isoformat(),
            "history": data["history"]
        })

        with open(filename, "w") as f:
            json.dump(results, f, indent=4)

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"})

@csrf_exempt
def get_results(request):
    try:
        with open("results.json", "r") as f:
            data = json.load(f)

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)})
    
@csrf_exempt
def save_topics(request):
    try:
        if request.method == "POST":

            settings = {
                "easy": request.POST.getlist("easy_topics"),
                "medium": request.POST.getlist("medium_topics"),
                "hard": request.POST.getlist("hard_topics"),
                "expert": request.POST.getlist("expert_topics")
            }

            with open("cybermillionaire/topic_settings.json", "w") as f:
                json.dump(settings, f, indent=4)

                return HttpResponse(index(request))

        return JsonResponse({"status": "invalid request"})

    except Exception as e:
        return JsonResponse({"error": str(e)})
    
def ai_feedback(request):
    feedback = generate_ai_feedback("results.json")
    return render(request, "feedback.html", {
        "feedback": feedback
    })

def topics(request):
    try:
        with open("cybermillionaire/topic_settings.json", "r") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {
            "easy": [],
            "medium": [],
            "hard": [],
            "expert": []
        }

    return render(request, "topics.html", {
        "settings": settings
    })

def index(request):
    return render(request, "index.html")

def start_game(request, mode):
    e.export_questions(mode)
    return render(request, "game.html")
    
def start1(request):
    return start_game(request, "1")

def start2(request):
    return start_game(request, "2")

def start3(request):
    return start_game(request, "3")

def start4(request):
    return start_game(request, "4")

def dynamic_start1(request):
    return start_game(request, "dynamic-1")

def dynamic_start2(request):
    return start_game(request, "dynamic-2")

def dynamic_start3(request):
    return start_game(request, "dynamic-3")

def dynamic_start4(request):
    return start_game(request, "dynamic-4")