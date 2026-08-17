import requests
import random
from .mysql_db import get_topic_settings
from openai import OpenAI
from google import genai
import os

# Dictionary to hold all the level choices
LEVELS = {"easy": ("You are a school teacher trying to create a cybersecurity quiz.", "primary school"), 
          "medium": ("You are a high school teacher trying to create a cybersecurity quiz.", "secondary school"), 
          "hard" : ("You are a cybersecurity professor trying to create a quiz.", "college"), 
          "expert" : ("You are a cybersecurity expert trying to create a quiz.", "expert with technical experience")}

# Load user-selected topics
def load_topic_settings(user_id):
    return get_topic_settings(user_id)

# Function uses Random module to pick a word and returns it
def pick_a_word(words):
    if not words:
        return "a random cybersecurity topic"
    return random.choice(words) # returns a random word

def build_prompt(system_prompt, question_level, topic):
    return f"""
{system_prompt}

Write ONE unique {question_level} cybersecurity question about "{topic}".

Return ONLY this format exactly:

Question: <question>

A. <answer>
B. <answer>
C. <answer>
D. <answer>

Correct Answer: <A, B, C, or D>

Rules:
- You MUST have one and only one correct answer.
- You MUST indicate the correct answer.
- Exactly four answer choices.
- All answers must be unique.
- Use correct grammar.
- No explanations.
- No markdown.
- No extra text before or after the format.
"""

# Function that reaches out to the API
def api(ai_model, topic, system_prompt, question_level):
    ai_model = os.getenv("AI_MODEL")
    prompt = build_prompt(system_prompt, question_level, topic)
    if ai_model.startswith("gpt"):
        client = OpenAI(api_key=os.getenv("API_KEY"))
        response = client.chat.completions.create(
            model=ai_model,
            messages=[{"role": "system","content": system_prompt},{"role": "user","content": prompt}]
        )
        return response.choices[0].message.content.strip()

    elif ai_model.startswith("gemini"):
        client = genai.Client(api_key=os.getenv("API_KEY"))
        response = client.models.generate_content(
            model=ai_model,
            contents=prompt
        )
        return response.text.strip()
    
    elif ai_model.startswith("llama"):
        response = requests.post(os.getenv("AI_IP"),json={"model": ai_model,"prompt": prompt,"stream": False})
        return response.json()["response"].strip()

def generate_question(level, user_id):

    settings = load_topic_settings(user_id)
    topic = pick_a_word(settings[level])
    system_prompt, question_level = LEVELS[level]
    return api(os.getenv("LLAMA_MODEL"),topic,system_prompt,question_level)

if __name__ == '__main__':
    level = "expert"  # Default level for direct execution
    print(generate_question(level))