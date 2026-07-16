import requests
import random
from .mysql_db import get_topic_settings, get_ai_model
from openai import OpenAI
from google import genai

# Dictionary to hold all the level choices
levels = {"easy": ("You are a school teacher trying to create a cybersecurity quiz.", "primary school"), 
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

# Function that reaches out to the API
def api(ai_model, words, content, question_level):
    word = pick_a_word(words)
    if ai_model == "gpt-3.5-turbo-0125":
        client = OpenAI(api_key="")

        completion = client.chat.completions.create(
            model=ai_model,
            messages=[
                {
                    "role": "system",
                    "content": content
                },
                {
                    "role": "user",
                    "content": (
                        f"Write one unique {question_level} level cybersecurity question about {word} "
                        "and provide multiple answers (one correct, three incorrect, but state the correct answer) "
                        "similar to the game style of Who Wants to Be a Millionaire.\n\n"
                        "Format:\n"
                        "Question: <question>\n\n"
                        "A. <answer>\n"
                        "B. <answer>\n"
                        "C. <answer>\n"
                        "D. <answer>\n\n"
                        "Correct Answer: <correct answer>"
                    )
                }
            ]
        )

        return completion.choices[0].message.content

    elif ai_model == "gemini-3.1-flash-lite":
        client = genai.Client(api_key="")

        prompt = f"""
    {content}

    Write one unique {question_level} level cybersecurity question about {word}
    and provide multiple answers (one correct, three incorrect).

    Format exactly like this:

    Question: <question>

    A. <answer>
    B. <answer>
    C. <answer>
    D. <answer>

    Correct Answer: <correct answer>
    """

        response = client.models.generate_content(
            model=ai_model,
            contents=prompt
        )

        return response.text
    elif(ai_model == "llama3.2:3b"):
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
                    "model": ai_model,
                    "prompt": prompt,
                    "stream": False
                },
            )

    return response.json()["response"].strip()

def generate_question(level, user_id):

    settings = load_topic_settings(user_id)
    words = settings[level]
    content = levels[level][0]
    question_level = levels[level][1]
    ai_model = get_ai_model(user_id)

    return api(ai_model, words, content, question_level)

if __name__ == '__main__':
    level = "expert"  # Default level for direct execution
    print(generate_question(level))