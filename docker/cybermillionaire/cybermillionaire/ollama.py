import requests
import json

prompt = """
Generate 1 cybersecurity question.

Return only valid JSON.

{
  "question": "",
  "answers": [],
  "correct": 0,
  "topic": ""
}
"""

response = requests.post(
    "http://192.168.1.28:11434/api/generate",
    json={
        "model": "qwen3:8b",
        "prompt": prompt,
        "stream": False
    }
)

questions = json.loads(response.json()["response"])
print(questions)

with open("C:\Million\docker\cybermillionaire\static\js\millionaire.json", "w") as f:
    json.dump(questions, f, indent=4)