import requests
import random
import json

# Dictionary to hold all the level choices
levels = {"easy": ("You are a school teacher trying to create a cybersecurity quiz.", "primary school"), 
          "medium": ("You are a high school teacher trying to create a cybersecurity quiz.", "secondary school"), 
          "hard" : ("You are a cybersecurity professor trying to create a quiz.", "college"), 
          "expert" : ("You are a cybersecurity expert trying to create a quiz.", "expert with technical experience")}

# Load user-selected topics
def load_topic_settings():
    with open("./cybermillionaire/topic_settings.json") as f:
        return json.load(f)

# Function uses Random module to pick a word and returns it
def pick_a_word(words):
    return random.choice(words) # returns a random word

# Function that reaches out to the API
def api(words, content, question_level):
    word = pick_a_word(words)

    prompt = f"""
{content}

Write one unique {question_level} level cybersecurity question about {word}.

You MUST return ONLY the following format:

Question: <question>

A. <answer>
B. <answer>
C. <answer>
D. <answer>

Correct Answer: <A, B, C, or D>

Questions must make sense.
Questions must have valid grammatical structure.
Questions must always have exactly 4 unique answers followed by the correct answer.
The Correct Answer MUST always be reiterated on a seperate line below the answers. 
Do not provide explanations.
Do not provide reasoning.
Do not use markdown.
"""

    response = requests.post(
        "http://192.168.1.28:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        },
    )

    return response.json()["response"].strip()

def generate_question(level):
    settings = load_topic_settings()

    words = settings[level]
    content = levels[level][0] # sets the correct content field for the specified level
    question_level = levels[level][1] # sets the correct question level field for the specified level

    return api(words, content, question_level)

if __name__ == '__main__':
    level = "expert"  # Default level for direct execution
    print(generate_question(level))