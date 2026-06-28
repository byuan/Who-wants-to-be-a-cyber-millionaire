import json
import requests
import os

def load_results(path="./results.json"):
    with open(path, "r") as f:
        return json.load(f)
    
from collections import Counter

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

def generate_ai_feedback(path):
    data = load_results(path)
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
"""

    response = requests.post(
        "http://192.168.1.28:11434/api/generate",
        json={
            "model": "qwen2.5:3b-instruct",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

if __name__ == '__main__':
    print(generate_ai_feedback("./docker/cybermillionaire/results.json"))