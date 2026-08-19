import json
import requests    
from collections import Counter
import os

def build_summary(data):
    total_games = len(data)
    total_questions = 0
    total_correct = 0

    question_counter = Counter()
    missed_counter = Counter()

    for game in data:
        for question in game["history"]:
            total_questions += 1
            question_counter[question["question"]] += 1

            if question["isCorrect"]:
                total_correct += 1
            else:
                missed_counter[question["question"]] += 1

    accuracy = 0
    if total_questions > 0:
        accuracy = round((total_correct / total_questions) * 100, 1)

    return {
        "games_played": total_games,
        "questions_answered": total_questions,
        "questions_correct": total_correct,
        "accuracy": accuracy,
        "most_missed_questions": missed_counter.most_common(5),
        "most_seen_questions": question_counter.most_common(5)
    }

def generate_ai_feedback(data):
    summary = build_summary(data)
    prompt = f"""
You are a cybersecurity learning coach.

A student has completed multiple quiz sessions.

Below is a statistical summary of the student's performance:

{json.dumps(summary, indent=2)}

Here is their performance data:

{json.dumps(data, indent=2)}

Provide feedback based on these rules:
- Focus only on patterns in correctness
- Identify strengths and weaknesses
- Detect improvement or decline over time
- Be concise and practical
- Do NOT repeat raw data
- Do NOT use invalid characters such as emojis
- Give actionable feedback
- Do NOT invent or create game sessions that did not happen.
"""

    response = requests.post(
        os.getenv("AI_IP"),json={"model": os.getenv("AI_MODEL"),"prompt": prompt,"stream": False})

    return response.json()["response"]