#views.py file

from django.shortcuts import HttpResponse
from django import template
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

            return JsonResponse({"status": "success"})

        return JsonResponse({"status": "invalid request"})

    except Exception as e:
        return JsonResponse({"error": str(e)})
    
def ai_feedback(request):
    feedback = generate_ai_feedback("results.json")
    t = template.loader.get_template('feedback.html')
    html = t.render({"feedback": feedback})
    return HttpResponse(html)

def topics(request):
    t = template.loader.get_template('topics.html')
    html = t.render()
    return HttpResponse(html)

def index(request):
    t = template.loader.get_template('index.html')
    html = t.render()
    return HttpResponse(html)
    
def start1(request):        # Static Primary School Level
    e.export_questions('1')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)

def start2(request):        # Static Secondary School Level
    e.export_questions('2')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)

    
def start3(request):        # Static College Level
    e.export_questions('3')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)
    
    
def start4(request):        # Static Expert Level
    e.export_questions('4')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)

# Dynamic views
def dynamic_start1(request):  # Dynamic Primary School Level
    e.export_questions('dynamic-1')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)

def dynamic_start2(request):  # Dynamic Secondary School Level
    e.export_questions('dynamic-2')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)

def dynamic_start3(request):  # Dynamic College Level
    e.export_questions('dynamic-3')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)

def dynamic_start4(request):  # Dynamic Expert Level
    e.export_questions('dynamic-4')
    t = template.loader.get_template('game.html')
    html = t.render()
    return HttpResponse(html)
