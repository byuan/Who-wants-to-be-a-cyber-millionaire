import json
import requests
import os

def load_results(path="C:/Million/docker/cybermillionaire/results.json"):
    with open(path, "r") as f:
        return json.load(f)

def generate_ai_feedback():
    data = load_results()
    prompt = f"""
You are a cybersecurity learning coach.

A student has completed multiple quiz sessions.

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
    print(generate_ai_feedback())