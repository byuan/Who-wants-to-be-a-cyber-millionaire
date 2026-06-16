from openai import OpenAI
from google import genai
import random

# Bags of words for each level
BAG_O_WORDS_PRIMARY = ['Passwords', 'Internet Safety', 'Cyberbullying', 'Social Media', 'Secure Websites', 'Hacking', 'Digital Footprints', 'Data', 'Phishing', 'Safe Downloading'] 
BAG_O_WORDS_SECONDARY = ['Passwords', 'Phishing', 'Encryption', 'Firewall', 'Malware', 'Two-factor authentication', 'Social Engineering', 'Network Security', 'Endpoint Security', 'Advanced Persistent Threats']
BAG_O_WORDS_COLLEGE = ['Intrusion Detection Systems', 'Cyber Threat Intelligence', 'Digital Forensics', 'Cryptography', 'Blockchain Security', 'Secure Coding Practices', 'Ethical Hacking', 'Social Engineering', 'Cyber Incident Response', 'Network Encryption']
BAG_O_WORDS_EXPERT = ['TCP Protocol', 'Wireless Security Protocol', 'HTTP Headers', 'Virtualization', 'Kerberos Authentication', 'TCP/UDP Protocol', 'SSL/X509 Certificates', 'Asymmetric/Symmetric Encryption for Cryptography', 'Linux/Unix System Forensics', 'Technical Aspects of Network Protocols']

# Dictionary to hold all the level choices
levels = {"easy": (BAG_O_WORDS_PRIMARY, "You are an elementary school teacher trying to create a cybersecurity quiz.", "primary school"), 
          "medium": (BAG_O_WORDS_SECONDARY, "You are a high school teacher trying to create a cybersecurity quiz.", "secondary school"), 
          "hard" : (BAG_O_WORDS_COLLEGE, "You are a cybersecurity professor trying to create a quiz.", "college"), 
          "expert" : (BAG_O_WORDS_EXPERT, "You are a cybersecurity expert trying to create a quiz.", "expert with technical experience")}


# Function uses Random module to pick a word and returns it
def pick_a_word(BAG_O_WORDS):
    word = random.randint(0, len(BAG_O_WORDS) - 1) # randomly selects the index from the length of the specified BAG_O_WORDS
    return BAG_O_WORDS[word] # returns the word at the selected index in the specified BAG_O_WORDS

# Function that reaches out to the API
def api(BAG_O_WORDS, content, question_level):
    word = pick_a_word(BAG_O_WORDS) # picks a random word from BAG_O_WORDS

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
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text

def generate_question(level):
    BAG_O_WORDS = levels[level][0] # sets the correct BAG_O_WORDS for the specified level
    content = levels[level][1] # sets the correct content field for the specified level
    question_level = levels[level][2] # sets the correct question level field for the specified level

    return api(BAG_O_WORDS, content, question_level)

if __name__ == '__main__':
    level = "expert"  # Default level for direct execution
    print(generate_question(level))